from __future__ import absolute_import
from __future__ import unicode_literals
import os
from laipvt.interface.serviceinterface import ServiceInterface
from laipvt.handler.middlewarehandler import EtcdConfigHandler
from laipvt.sysutil.util import path_join, log, status_me
from laipvt.controller.middleware.etcd import EtcdController
from laipvt.helper.errors import Helper
from laipvt.sysutil.command import GET_POD_INFO, RESTART_DEPLOYMENT, RESTART_DEPLOYMENT_ALL

class LicenseController(ServiceInterface):
    def __init__(self, check_result, service_path):
        super(LicenseController, self).__init__(check_result, service_path)
        self.nginx_template = path_join(self.templates_dir, "nginx/http/nginx-license.tmpl")
        self.nginx_tmp = path_join("/tmp", "nginx-license.conf")
        self.nginx_file_remote = path_join(self.deploy_dir, "nginx/http/nginx-license.conf")

    @status_me("license")
    def prepare_license_data_file(self, is_renew=False, **kwargs):
        # if is_renew:
        #     lcs_file_path = kwargs.get("license_file")
        # else:
        #     # 找到以.lcs结尾的文件
        #     lcs_file_path_list = list(filter(lambda x: x.endswith(".lcs"), os.listdir(self.service_path.data)))
        #     if lcs_file_path_list:
        #         lcs_file_path = path_join(self.service_path.data, lcs_file_path_list[0])
        #
        #     else:
        #         log.error(Helper().FILE_NOT_FOUND.format("license file"))
        #         exit(2)
        self.prepare_data(project=self.project)

    def restart_service(self):
        etcd = EtcdController(self.check_result, EtcdConfigHandler(), "")
        etcd.reset()
        get_pod_info_cmd = GET_POD_INFO.format("license-manager")
        res = self._exec_command_to_host(cmd=get_pod_info_cmd, server=self.harbor_hosts[0], check_res=True)
        if not (res["code"] == 0 and "Running" in res["stdout"]):
            log.error("license service not found:{}".format(get_pod_info_cmd))
            exit(2)
        restart_deployment_cmd =  RESTART_DEPLOYMENT.format("mid", "license-manager")
        self._exec_command_to_host(cmd=restart_deployment_cmd, server=self.harbor_hosts[0], check_res=True)

        restart_all_deployment_cmd = [
            RESTART_DEPLOYMENT_ALL.format("mage"),
            RESTART_DEPLOYMENT_ALL.format("rpa")
        ]
        self._exec_command_to_host(cmd=restart_all_deployment_cmd, server=self.harbor_hosts[0], check_res=True)

    def renew_license(self, license_file):
        self.prepare_license_data_file(is_renew=True, license_file=license_file)
        self.restart_service()

    @status_me("license")
    def push_license_images(self):
        self.push_images(self.project)

    @status_me("license")
    def start_license_service(self):
        self._create_namespace(namespaces=self.namespaces, istio_injection_namespaces="")
        self.start_service(project=self.project, version=self.private_deploy_version)

    @status_me("license")
    def license_proxy_on_nginx(self):
        self.proxy_on_nginx(self.nginx_template, self.nginx_tmp, self.nginx_file_remote)

    @status_me("license")
    def deploy_license_configmap(self):
        self.deploy_all_configmap()

    @status_me("license")
    def deploy_license_istio(self):
        self.deploy_istio()

    @status_me("license")
    def init_license_entuc_clients(self):
        self.init_usercenter_clients(project="license")

    def run(self):
        self.push_license_images()
        self.deploy_license_configmap()
        self.deploy_license_istio()
        self.start_license_service()
        self.prepare_license_data_file()
        self.license_proxy_on_nginx()
        self.project_pod_check()
        self.init_license_entuc_clients()

