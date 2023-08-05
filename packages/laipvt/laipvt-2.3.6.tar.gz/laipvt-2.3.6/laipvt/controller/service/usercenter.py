from __future__ import absolute_import
from __future__ import unicode_literals
import time
from laipvt.interface.serviceinterface import ServiceInterface
from laipvt.sysutil.util import path_join, log, status_me


class UserCenterController(ServiceInterface):
    def __init__(self, check_result, service_path):
        super(UserCenterController, self).__init__(check_result, service_path)

        self.app_config_hosts = path_join(self.config, "Usercenter/usercenter-config.conf")
        self.app_config_container = "/app/appsettings.json"

        self.nginx_template = path_join(self.templates_dir, "nginx/http/nginx-entuc.tmpl")
        self.nginx_tmp = path_join("/tmp", "nginx-entuc.conf")
        self.nginx_file_remote = path_join(self.deploy_dir, "nginx/http/nginx-entuc.conf")

    @status_me("usercenter")
    def deploy_configmap(self):
        self.deploy_all_configmap()

    @status_me("usercenter")
    def deploy_usercenter_istio(self):
        self.deploy_istio()

    @status_me("usercenter")
    def init_usercenter_minio(self):
        self.init_minio()

    @status_me("usercenter")
    def init_usercenter_mysql(self):
        self.init_mysql()

    @status_me("usercenter")
    def init_usercenter_rabbitmq(self):
        self.init_rabbitmq()

    @status_me("usercenter")
    def push_usercenter_images(self):
        self.push_images(self.project)

    @status_me("usercenter")
    def start_usercenter_service(self):
        self.start_service(project=self.project, version=self.private_deploy_version)

    @status_me("usercenter")
    def usercenter_proxy_on_nginx(self):
        self.proxy_on_nginx(self.nginx_template, self.nginx_tmp, self.nginx_file_remote)

    @status_me("usercenter")
    def usercenter_init_user(self):
        time.sleep(120)
        self.init_usercenter_user()

    def run(self):
        self.init_usercenter_mysql()
        self.init_usercenter_minio()
        self.init_usercenter_rabbitmq()
        self.push_usercenter_images()
        self.deploy_configmap()
        self.deploy_usercenter_istio()
        self.start_usercenter_service()
        self.usercenter_proxy_on_nginx()
        self.project_pod_check()
        self.usercenter_init_user()

