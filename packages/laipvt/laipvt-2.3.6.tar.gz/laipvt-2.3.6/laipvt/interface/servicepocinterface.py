from __future__ import absolute_import
from __future__ import unicode_literals
import os
import json
import time
from redis.sentinel import Sentinel
from laipvt.model.cmd import DockerImageModel
from laipvt.model.harbor import HarborModel
from laipvt.helper.exception import UtilsError
from laipvt.handler.confighandler import CheckResultHandler, ServerHandler, PvtAdminConfigHandler
from laipvt.handler.middlewarehandler import HarborConfigHandler
from laipvt.sysutil.template import FileTemplate
from laipvt.sysutil.util import path_join, log, ssh_obj, to_object, walk_sql_path
from laipvt.handler.middlewarehandler import MiddlewareConfigHandler
from laipvt.model.cmd import ComposeModel
from laipvt.model.sql import SqlModule
from laipvt.model.server import runcmd
from laipvt.helper.errors import Helper

class ServicePocInterface:
    def __init__(self, check_result: CheckResultHandler, service_path):
        """
         check_result: 对象，前置检查结果
         service_path: 对象，服务进程详情
         """
        self.check_result = check_result
        self.service_path = service_path

        self.middleware_servers = self.check_result.servers
        self.middleware_server_list = self.middleware_servers.get_role_ip("master")

        self.middleware_cfg = to_object(MiddlewareConfigHandler("mysql").get_all_config_with_check_result())
        for k, v in self.middleware_cfg.items():
            if not self.middleware_cfg[k]["ipaddress"]:
                self.middleware_cfg[k]["ipaddress"] = self.middleware_server_list
        self.middleware_cfg.update(self.check_result.__dict__)

        self.servers = check_result.servers.get()
        self.service_info = service_path.config
        self.private_deploy_version = self.service_info.tag

        self.namespace = self.service_path.config.namespace
        self.namespaces = [self.namespace, "proxy"]
        self.istio_injection_namespaces = [self.namespace, "proxy", ]
        self.project = self.namespace

        self.templates_dir = self.service_path.templates
        self.data_dir = self.service_path.data
        self.deploy_dir = self.check_result.deploy_dir

        self.service_charts_remote = path_join(self.deploy_dir, "charts")
        self.harbor_cfg = HarborConfigHandler().get_config_with_check_result()
        try:
            harbor_ip = self.harbor_cfg["harbor"]["lb"]
        except IndexError:
            harbor_ip = self.check_result.servers.get_role_ip("harbor")[0]
        self.registry_hub = "{}:{}".format(harbor_ip, self.harbor_cfg["harbor"]["nginx_harbor_proxy_port"])

        self.etcd_servers = self.check_result.servers.get_role_ip("master")
        self.etcd_endpoint = "\,".join(
            ["{}:{}".format(server, self.middleware_cfg.etcd.http_port) for server in self.etcd_servers]
        )

        self.env_k8s_config_src = path_join(self.templates_dir, "env_k8s_config")
        self.env_k8s_config_dest = path_join(self.templates_dir, "env_k8s_config_dest")
        self.env_k8s_config_remote = path_join(self.deploy_dir, "env_k8s_config_dest")

        self.nginx_compose_file = path_join(self.deploy_dir, "nginx", "docker-compose.yml")

        self.servers = self.check_result.servers.get()
        self.middleware_cfg["k8s_hosts"] = [x.ipaddress for x in self.servers]
        self.master_hosts = self.check_result.servers.get_role_obj("master")
        self.middleware_cfg["k8s_masters"] = [x.ipaddress for x in self.master_hosts]

        self.replicas = 1
        self.nodes = self.check_result.servers.get_role_obj("node")
        self.master_host = self.check_result.servers.get_role_obj("master")[0]
        self.harbor_hosts = self.check_result.servers.get_role_obj("harbor")

        self.rabbitmq_init_file_template_path = path_join(self.templates_dir, "init_rabbitmq.tmpl")
        self.rabbitmq_init_file_path = path_join(self.templates_dir, "init_rabbitmq.sh")

        self.redis_init_file_template_path = path_join(self.templates_dir, "init_redis.tmpl")
        self.redis_init_file_path = path_join(self.templates_dir, "init_redis.sh")

        self.component = self.service_path.config.component

        # bin
        self.fill_bin_src = path_join(self.templates_dir, "pvt_gen-linux-amd64")
        self.fill_bin_remote = path_join(self.deploy_dir, "pvt_gen-linux-amd64")
        # valuePath
        self.templates_src = path_join(self.templates_dir, "env_pvt_templates")
        self.common_dest = path_join("/tmp", "{}_env_pvt_common".format(self.project))
        self.common_remote = path_join(self.deploy_dir, "{}_env_pvt_common".format(self.project))
        # tmplPath
        self.config_templates = path_join(self.templates_dir,
                                          "{}_conf_templates".format(self.component),
                                          self.component.capitalize())
        self.config_remote = path_join(self.deploy_dir,
                                       "{}_conf_templates".format(self.component),
                                       self.component.capitalize())

        self.config_target = path_join(self.deploy_dir, "{}_configmap".format(self.component))
        # config原生配置
        self.config = path_join(self.deploy_dir, "{}_config".format(self.component))

        # configmap
        self.configmap = path_join(self.config_target, self.component.capitalize())
        self.configmap_remote = path_join(self.deploy_dir, self.component.capitalize())

    def push_images(self, project):
        harbor = HarborModel(username="admin", host=self.registry_hub, password=self.middleware_cfg["harbor"]["password"])
        if project not in harbor.list_project():
            harbor.create_project(project)

        if os.path.exists(self.service_path.images):
            for image in os.listdir(self.service_path.images):
                image_path = path_join(self.service_path.images, image)
                log.info(Helper().PUSH_IMAGE.format(image_path))
                # print(image_path)
                docker = DockerImageModel(
                    image=image_path, project=project, repo=self.registry_hub, tag_version=self.private_deploy_version
                )
                docker.run()

    def proxy_on_nginx(self, nginx_template, nginx_tmp, nginx_file_remote):
        FileTemplate(self.middleware_cfg, nginx_template, nginx_tmp).fill()
        self._send_file(src=nginx_tmp, dest=nginx_file_remote)
        compose_cmd = ComposeModel(self.nginx_compose_file)
        for server in self.servers:
            self._exec_command_to_host(cmd=compose_cmd.restart(), server=server, check_res=True)

    def init_mysql(self, sql_path):
        log.info(sql_path)
        db_info = walk_sql_path(sql_path)
        if self.middleware_cfg.mysql.is_deploy:
            mysql_host = self.master_host
        else:
            mysql_host = self.middleware_cfg.mysql.ipaddress[0]
        sql = SqlModule(host=mysql_host, port=int(self.middleware_cfg.mysql.port),
                        user=self.middleware_cfg.mysql.username, passwd=self.middleware_cfg.mysql.password)
        for db_name, sql_files in db_info.items():
            create_db = CREATE_DB.format(db_name=db_name)
            sql.insert_sql(create_db)
            sql.use_db(db_name)
            for sql_file in sql_files:
                sql.import_from_file(sql_file, file_eof=";\n")

    def init_rabbitmq(self):
        # log.info("渲染初始化RabbitMQ脚本: {} -- > {}".format(
        #     self.rabbitmq_init_file_template_path,
        #     self.rabbitmq_init_file_path)
        # )
        FileTemplate(self.middleware_cfg, self.rabbitmq_init_file_template_path, self.rabbitmq_init_file_path).fill()

        fp = open(self.rabbitmq_init_file_path)
        # log.info("开始执行初始化RabbitMQ命令")

        for cmd in fp.readlines():
            if cmd.strip():
                log.info(cmd)
                code, res = runcmd(cmd)
                if code != 0:
                    log.error(res)
                    exit(2)

    def init_redis(self):
        if self.middleware_cfg["redis"]["is_deploy"]:
            # 如果是自建redis服务，连接哨兵服务器，获取master节点地址
            pool = []
            for host in self.middleware_servers.get_role_obj("master"):
                redis_endpoint = (host.ipaddress, self.middleware_cfg["redis"]["port_sentinel"])
                pool.append(redis_endpoint)
            sentinel = Sentinel(pool, socket_timeout=0.5)
            # 获取主服务器地址
            master_address = sentinel.discover_master(self.middleware_cfg.redis.master_name)[0]
            # server_object_list = self.check_result.servers.search_server(key="ipaddress", value=master)
            self.middleware_cfg["redis"]["master_address"] = master_address

        # log.info("渲染初始化redis脚本: {} -- > {}".format(
        #     self.redis_init_file_template_path,
        #     self.redis_init_file_path)
        # )
        FileTemplate(self.middleware_cfg, self.redis_init_file_template_path, self.redis_init_file_path).fill()

        fp = open(self.redis_init_file_path)
        # log.info("开始执行初始化redis命令")

        for cmd in fp.readlines():
            if cmd.strip():
                log.info(cmd)
                code, res = runcmd(cmd)
                if code != 0:
                    log.error(res)
                    exit(2)

    def init_identity_user(self):
        init_user_cmd = INIT_IDENTITY_USER
        self._exec_command_to_host(cmd=init_user_cmd, server=self.servers[0], check_res=False)
