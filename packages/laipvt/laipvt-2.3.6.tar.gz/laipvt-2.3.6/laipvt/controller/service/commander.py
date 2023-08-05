from __future__ import absolute_import
from __future__ import unicode_literals

import os
import time

import requests
from minio import Minio
from hashlib import sha256

from laipvt.interface.serviceinterface import ServiceInterface
from laipvt.helper.errors import Helper
from laipvt.sysutil.command import COMMANDER_UPGRADE_INSTALL, CREATE_DB, HELM_INSTALL_COMMANDER, HELM_LIST
from laipvt.sysutil.util import log, path_join, status_me, walk_sql_path, CommanderAes


class CommanderController(ServiceInterface):
    def __init__(self, check_result, service_path):
        super(CommanderController, self).__init__(check_result, service_path)

        self.nginx_template = path_join(self.templates_dir, "nginx/http/nginx-entcmd.tmpl")
        self.nginx_tmp = path_join("/tmp", "nginx-entcmd.conf")
        self.nginx_file_remote = path_join(self.deploy_dir, "nginx/http/nginx-entcmd.conf")
        if self.middleware_cfg["mysql"]["is_deploy"]:
            self.mysql_host = "mysql.default.svc"
            self.mysql_port = 3306
        else:
            self.mysql_host = self.middleware_cfg["mysql"]["ipaddress"][0]
            self.mysql_port = self.middleware_cfg["mysql"]["port"]

        # self.protocol = "https" if self.middleware_cfg["config"]["deploy_https"] else "http"
        # self.tenant_url = "{protocol}://{host}:{port}".format(protocol=self.protocol,
        #                                                       host=self.middleware_cfg.nginx.lb,
        #                                                       port=self.middleware_cfg.nginx.commander_tenant_port)

    @status_me("commander")
    def deploy_configmap(self):
        self.deploy_all_configmap()

    @status_me("commander")
    def deploy_commander_istio(self):
        self.deploy_istio()

    @status_me("commander")
    def init_commander_mysql(self):
        self.init_mysql()

    @status_me("commander")
    def init_commander_rabbitmq(self):
        self.init_rabbitmq()

    @status_me("commander")
    def init_commander_redis(self):
        self.init_redis()

    @status_me("commander")
    def init_commander_minio(self):
        self.init_minio()

    @status_me("commander")
    def push_commander_images(self):
        self.push_images(self.project)

    def upgrade_service(self, project):
        for service, processes in self.service_path.config.services.items():
            for process in processes:
                log.info("{}开始更新".format(process))
                self._create_logs_dir(service)
                file_path = os.path.join(self.service_path.charts, process)

                if self.middleware_cfg["redis"]["is_deploy"]:
                    config_server = "\,".join(
                            [
                                    "{}:{}\,serviceName={}\,allowAdmin=true".format(
                                            server,
                                            self.middleware_cfg["redis"]["port_sentinel"],
                                            self.middleware_cfg["redis"]["master_name"]
                                    ) for server in self.middleware_servers.get_role_ip("master")
                            ]
                    )
                else:
                    config_server = "{}:{}".format(self.middleware_cfg["redis"]["ipaddress"][0],
                                                   self.middleware_cfg["redis"]["port"])

                cmd = COMMANDER_UPGRADE_INSTALL.format(
                        process=process, replicas=self.replicas,
                        registry_hub=path_join(self.registry_hub, project),
                        image_name=process, image_tag=self.private_deploy_version,
                        pvt_work_dir=self.deploy_dir,
                        config_server=config_server,
                        config_server_passwd=self.middleware_cfg["redis"]["password"],
                        mysql_host=self.mysql_host, mysql_port=self.mysql_port,
                        mysql_user=self.middleware_cfg["mysql"]["username"],
                        mysql_password=self.middleware_cfg["mysql"]["password"],
                        etcd_endpoint=self.etcd_endpoint, mysql_database="uibot_global",
                        mysql_charset="utf8mb4",
                        oidc_authority="http://{}:{}".format(
                                self.middleware_cfg["identity"]["lb"],
                                self.middleware_cfg["identity"]["nginx_proxy_port"]),
                        oidc_secret="laiye",
                        file_path=file_path)

                self._exec_command_to_host(cmd=cmd, server=self.servers[0])

    @status_me("commander")
    def start_commander_service(self):
        self.start_service(project=self.project, version=self.private_deploy_version)

    @status_me("commander")
    def commander_proxy_on_nginx(self):
        self.proxy_on_nginx(self.nginx_template, self.nginx_tmp, self.nginx_file_remote)

    def login_tenant(self):
        log.info(Helper().LOGIN_TENANT)
        login_account_url = "{tenant_url}/api/tenant/account/getCurrentInfo".format(tenant_url=self.tenant_url)
        AccountResponse = requests.get(login_account_url)  # goto get the xsrf-token for post request.
        preCookies = AccountResponse.cookies  # include xsrf-token for future use.
        XsrfTOKEN = preCookies.get('XSRF-TOKEN')  # need this to header.
        loginHeaders = {
                'X-XSRF-TOKEN': XsrfTOKEN,
                'Referer':      self.tenant_url
        }
        # 将默认密码加密：先将token使用sha256加密，然后取其前32位，再使用aes加密
        tenant_password = "123456".ljust(16, "\n")
        sha256_token = sha256(XsrfTOKEN.encode('utf-8')).hexdigest()[:32]
        password = CommanderAes.encrypt_oracle(sha256_token, tenant_password)
        data = {'userName': 'admin', 'password': password}
        login_url = "{tenant_url}/api/global/account/webLogin".format(tenant_url=self.tenant_url)
        response = requests.post(login_url, json=data, headers=loginHeaders, cookies=preCookies,
                                 verify=False)
        auth_cookie = ''
        # print(response)
        ret = response.json()
        if ret['code'] == 0:
            auth_cookies = preCookies
            auth_cookies.set('GlobalUser', response.cookies.get('GlobalUser'))
            # f"GlobalUser={cookies.get('GlobalUser', None)}"
            # log.info(auth_cookies)
            log.info("Login succeed")
            return auth_cookies, loginHeaders
        else:
            log.error("Login error!")
            exit(2)

    def tenant_init_mysql(self, auth_cookies, login_headers):
        log.info("租户平台配置MySql数据库")
        db_mysql = {
                "name":     "mysql-1",
                "host":     self.mysql_host,
                "port":     self.mysql_port,
                "dbName":   "uibot_rpa",
                "userName": self.middleware_cfg.mysql.username,
                "password": self.middleware_cfg.mysql.password,
                "type":     "10"
        }
        mysql_url = "{tenant_url}/api/global/database/create".format(tenant_url=self.tenant_url)
        resp1 = requests.post(mysql_url, json=db_mysql, cookies=auth_cookies, headers=login_headers, verify=False)
        json_resp1 = resp1.json()
        if json_resp1['code'] == 0:
            log.info("配置MySQL数据库完成")
        else:
            log.error("配置MySQL数据库失败")
            exit(2)

    @status_me("commander")
    def init_tenant(self):
        counter = 0
        succeed = False
        # 重试 10 次，如果还是不成功就报错
        while not succeed and counter < 100:
            time.sleep(5)
            try:
                auth_cookies, loginHeaders = self.login_tenant()
                self.tenant_init_mysql(auth_cookies=auth_cookies, login_headers=loginHeaders)
                succeed = True
            except Exception as e:
                # log.error(e)
                succeed = False
                counter += 1
        if not succeed:
            log.error("登录租户系统失败，请检查容器是否启动。")
            exit(2)

    @status_me("commander")
    def commander_apptest(self):
        self.app_test(project=self.project)

    @status_me("commander")
    def init_commander_entuc_clients(self):
        self.init_usercenter_clients(project=self.project)

    def run_apptest(self):
        self.app_test(project=self.project)

    def run(self):
        self.init_commander_mysql()
        self.init_commander_rabbitmq()
        self.init_commander_minio()
        self.deploy_configmap()
        self.push_commander_images()
        self.deploy_commander_istio()
        self.start_commander_service()
        self.commander_proxy_on_nginx()
        self.project_pod_check()
        self.init_commander_entuc_clients()
        self.commander_apptest()
