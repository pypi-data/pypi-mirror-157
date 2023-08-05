from __future__ import absolute_import
from __future__ import unicode_literals

import os
from laipvt.sysutil.ssh import SSHConnect
from laipvt.helper.exception import UtilsError
from laipvt.interface.serviceinterface import ServiceInterface
from laipvt.sysutil.template import FileTemplate
from laipvt.sysutil.util import path_join, log, status_me
from laipvt.sysutil.command import GET_PVC_VOLUMENAME_CMD, RESTART_DEPLOYMENT

def ssh_obj(ip, user, password, port=22) -> SSHConnect:
    return SSHConnect(hostip=ip, username=user, password=password, port=port)


class ChatbotController(ServiceInterface):
    def __init__(self, check_result, service_path):
        super(ChatbotController, self).__init__(check_result, service_path)

        self.chatbot_app_config_hosts = path_join(self.config , "Chatbot/laiye-chatbot-app.conf")
        self.chatbot_app_config_container = "/home/works/program/conf/online.conf"

        self.nginx_template = path_join(self.templates_dir, "nginx/http/nginx-chatbot.tmpl")
        self.nginx_tmp = path_join("/tmp", "nginx-chatbot.conf")
        self.nginx_file_remote = path_join(self.deploy_dir, "nginx/http/nginx-chatbot.conf")

    @status_me("chatbot")
    def deploy_chatbot_configmap(self):
        self.deploy_all_configmap()

    @status_me("chatbot")
    def deploy_chatbot_istio(self):
        self.deploy_istio()

    @status_me("chatbot")
    def init_chatbot_mysql(self):
        log.info("初始化mysql数据")
        # version = self.private_deploy_version.split("-")[0]
        mysql_real_ip = self.master_host.ipaddress
        if not self.middleware_cfg.mysql.is_deploy:
            mysql_real_ip = self.middleware_cfg.mysql.ipaddress[0]

        # docker run -t {进程：chatbot-app} --init
        cmd = "docker run --add-host mysql.default.svc:{} -t -v {}:{} {}/{}/chatbot-app:{} --init".format(
            mysql_real_ip,
            self.chatbot_app_config_hosts, self.chatbot_app_config_container,
            self.registry_hub, self.project, self.private_deploy_version
        )
        res = self._exec_command_to_host(cmd=cmd, server=self.servers[0], check_res=True)
        if res["code"] != 0:
            log.error("初始化mysql数据失败")
            log.error(res["stdout"])
            exit(2)
        log.info("初始化mysql数据完成")

    @status_me("chatbot")
    def push_chatbot_images(self):
        self.push_images(self.project)

    @status_me("chatbot")
    def start_chatbot_service(self):
        self.start_service(project=self.project, version=self.private_deploy_version)

    @status_me("chatbot")
    def chatbot_proxy_on_nginx(self):
        self.proxy_on_nginx(self.nginx_template, self.nginx_tmp, self.nginx_file_remote)

    @status_me("chatbot")
    def prepare_data_chatbot(self):
        self.prepare_data(project=self.project)

    @status_me("chatbot")
    def chatbot_apptest(self):
        self.app_test(project=self.project)

    @status_me("chatbot")
    def init_chatbot_entuc_clients(self):
        self.init_usercenter_clients(project=self.project)

    def run_apptest(self):
        self.app_test(project=self.project)

    def run(self):
        self.push_chatbot_images()
        self.deploy_chatbot_configmap()
        self.deploy_chatbot_istio()
        self.init_chatbot_mysql()
        self.start_chatbot_service()
        self.chatbot_proxy_on_nginx()
        self.prepare_data_chatbot()
        self.project_pod_check()
        self.init_chatbot_entuc_clients()
        self.chatbot_apptest()
