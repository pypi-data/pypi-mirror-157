from __future__ import absolute_import
from __future__ import unicode_literals

import os
import json
from minio import Minio
from laipvt.helper.exception import UtilsError
from laipvt.interface.serviceinterface import ServiceInterface
from laipvt.sysutil.template import FileTemplate
from laipvt.sysutil.util import path_join, log, status_me
from laipvt.sysutil.command import CREATE_DB
from laipvt.sysutil.conf import AccountIdConfig
from laipvt.model.sql import SqlModule
from laipvt.sysutil.command import HIDE_MENU_SQL


class MageController(ServiceInterface):
    def __init__(self, check_result, service_path):
        super(MageController, self).__init__(check_result, service_path)

        self.nginx_template = path_join(self.templates_dir, "nginx/http/nginx-mage.tmpl")
        self.nginx_tmp = path_join("/tmp", "nginx-mage.conf")
        self.nginx_file_remote = path_join(self.deploy_dir, "nginx/http/nginx-mage.conf")
        self.minio_data_list = [
            path_join(self.data_dir, "mage_minio_data"),
            path_join(self.data_dir, "siber_minio_data")
        ]

    @status_me("mage")
    def deploy_configmap(self):
        self.deploy_all_configmap()

    @status_me("mage")
    def deploy_mage_istio(self):
        self.deploy_istio()

    @status_me("mage")
    def init_minio_data(self):
        self.init_minio()
        # try:
        #     for bucket in self.service_info.buckets:
        #         # print(bucket)
        #         try:
        #             endpoint = "{}:{}".format(self.middleware_cfg.minio.lb, self.middleware_cfg.minio.nginx_proxy_port)
        #             cli = Minio(
        #                 endpoint,
        #                 self.middleware_cfg.minio.username,
        #                 self.middleware_cfg.minio.password,
        #                 secure=False
        #             )
        #             if not cli.bucket_exists(bucket):
        #                 cli.make_bucket(bucket)
        #             content_types = {
        #                 'txt': 'text/plain',
        #                 'jpg': 'image/jpg',
        #                 'gif': 'image/gif',
        #                 'png': 'image/png',
        #                 'jpeg': 'image/jpeg',
        #                 'pdf': 'application/pdf',
        #                 'tif': 'image/tiff',
        #                 'tiff': 'image/tiff',
        #                 'bmp': 'image/bmp',
        #                 'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        #             }
        #             for data_dir in self.minio_data_list:
        #                 for i in os.listdir(data_dir):
        #                     image_name = path_join(data_dir, i)
        #                     file_type = content_types[i.split('.')[-1]]
        #                     # cli.fput_object(bucket, i, image_name, content_type=file_type)
        #                     # if i.split('.')[-1] == "xlsx":
        #                     cli.fput_object(bucket, "document-mining-backend/" + i,  image_name, content_type=file_type)
        #
        #             policy_read_write = {
        #                 "Version": "2012-10-17",
        #                 "Statement": [
        #                     {
        #                         "Action": [
        #                             "s3:GetObject"
        #                         ],
        #                         "Effect": "Allow",
        #                         "Principal": "*",
        #                         "Resource": [
        #                             "arn:aws:s3:::{}/*".format(bucket)
        #                         ],
        #                         "Sid": ""
        #                     }
        #                 ]
        #             }
        #             cli.set_bucket_policy(bucket, json.dumps(policy_read_write))
        #
        #         except Exception as e:
        #             log.error(e)
        #             log.error("Minio上传数据失败")
        #             exit(2)
        # except Exception as e:
        #     log.error(e)
        #     log.error("创建bucket失败")
        #     exit(2)

    def create_mage_db_if_exist(self):
        if self.middleware_cfg.mysql.is_deploy:
            mysql_host = self.master_host.ipaddress
        else:
            mysql_host = self.middleware_cfg.mysql.ipaddress[0]
        sql = SqlModule(host=mysql_host, port=int(self.middleware_cfg.mysql.port),
                        user=self.middleware_cfg.mysql.username, passwd=self.middleware_cfg.mysql.password)
        if not sql.select("show databases like '%_saas_docuds';"):
            create_db = CREATE_DB.format(db_name="laiye_saas_docuds")
            sql.insert_sql(create_db)

    @status_me("mage")
    def init_mage_mysql(self):
        log.info("初始化mage mysql")
        version = self.private_deploy_version.split("-")[0]

        self.create_mage_db_if_exist()
        cmd = "docker run --rm --entrypoint /home/works/program/mageTool \
        {}/{}/document-mining-innerservice:{} --operateMode dbnew \
        --host {} --user {} --password {} --port {} --toVersion {}".format(
            self.registry_hub, self.project, self.private_deploy_version,
            self.middleware_cfg.mysql.ipaddress[0], self.middleware_cfg.mysql.username, self.middleware_cfg.mysql.password, self.middleware_cfg.mysql.port,
            version
        )
        res = self._exec_command_to_host(cmd=cmd, server=self.servers[0], check_res=True)
        if res["code"] != 0:
            log.error("初始化mage mysql失败")
            log.error(res["stdout"])
            exit(2)
        log.info("初始化mage mysql完成")
        #self.init_mysql(sql_path=self.service_path.sqls)
        # 渲染siber sqls目录
        # FileTemplate(self.middleware_cfg, self.service_path.siber_sqls, self.service_path.siber_sqls_ok).fill()
        # self.init_mysql(sql_path=self.service_path.siber_sqls_ok)

    @status_me("mage")
    def mage_transfer_data(self):
        src_dir_path = path_join(self.service_path.data, "mage_transfer_data")
        dest_dir_path = path_join(self.deploy_dir, "mage_transfer_data")
        image = "{}/{}/document-mining-innerservice:{}".format(self.registry_hub, self.project, self.private_deploy_version)
        version = self.private_deploy_version.split("-")[0]

        cmd = "docker run --rm --entrypoint /home/works/program/mageTool {image} \
         --operateMode datatransfer --dataMode 2 --minioAddr http://{minio_host}:{minio_port} \
          --host {mysql_host} --user {mysql_user} --password {mysql_password} --port {mysql_port} \
          --toVersion {version}".format(
            image=image, minio_host=self.middleware_cfg.minio.lb, minio_port=self.middleware_cfg.minio.port,
            mysql_host=self.middleware_cfg.mysql.ipaddress[0],mysql_user=self.middleware_cfg.mysql.username,
            mysql_password=self.middleware_cfg.mysql.password, mysql_port=self.middleware_cfg.mysql.port,
            version=version
        )
        self._send_file(src=src_dir_path, dest=dest_dir_path)
        res = self._exec_command_to_host(cmd=cmd, server=self.servers[0], check_res=True)
        log.info("userid: {}".format(res["stdout"].split("\n")[-1]))
        AccountIdConfig().save(res["stdout"].split("\n")[-1])

    @status_me("mage")
    def hide_menu(self):
        if self.middleware_cfg.mysql.is_deploy:
            mysql_host = self.master_host.ipaddress
        else:
            mysql_host = self.middleware_cfg.mysql.ipaddress[0]
        hide_menu_id = ",".join(self.admin_config.hide_menu_id)

        sql = SqlModule(host=mysql_host, port=int(self.middleware_cfg.mysql.port),
                        user=self.middleware_cfg.mysql.username, passwd=self.middleware_cfg.mysql.password)
        sql.insert_sql(HIDE_MENU_SQL.format(hide_menu_id=hide_menu_id))

    @status_me("mage")
    def push_mage_images(self):
        self.push_images(self.project)

    @status_me("mage")
    def start_mage_service(self):
        self.start_service(project=self.project, version=self.private_deploy_version)

    @status_me("mage")
    def mage_proxy_on_nginx(self):
        self.proxy_on_nginx(self.nginx_template, self.nginx_tmp, self.nginx_file_remote)

    @status_me("mage")
    def init_mage_entuc_clients(self):
        self.init_usercenter_clients(project=self.project)

    def run(self):
        self.push_mage_images()
        self.init_mage_mysql()
        # self.init_identity_user()
        self.init_minio_data()
        self.deploy_configmap()
        self.deploy_mage_istio()
        # self.mage_transfer_data()
        self.start_mage_service()
        self.mage_proxy_on_nginx()
        self.project_pod_check()

        self.hide_menu()
        self.init_mage_entuc_clients()
