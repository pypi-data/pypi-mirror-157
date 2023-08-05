from __future__ import absolute_import
from __future__ import unicode_literals

from laipvt.interface.serviceinterface import ServiceInterface
from laipvt.sysutil.util import path_join, log, status_me


class NoticeController(ServiceInterface):
    def __init__(self, check_result, service_path):
        super(NoticeController, self).__init__(check_result, service_path)
        self.nginx_template = path_join(self.templates_dir, "nginx/http/nginx-notice.tmpl")
        self.nginx_tmp = path_join("/tmp", "nginx-notice.conf")
        self.nginx_file_remote = path_join(self.deploy_dir, "nginx/http/nginx-notice.conf")


    @status_me("notice")
    def push_notice_images(self):
        self.push_images(self.project)

    @status_me("notice")
    def deploy_notice_configmap(self):
        self.deploy_all_configmap()

    @status_me("notice")
    def deploy_notice_istio(self):
        self.deploy_istio()

    @status_me("notice")
    def start_notice_service(self):
        self._create_namespace(namespaces=self.namespaces,
                               istio_injection_namespaces=self.istio_injection_namespaces)
        self.start_service(project=self.project, version=self.private_deploy_version)

    @status_me("notice")
    def prepare_notice_data(self):
        self.prepare_data(project=self.project)

    @status_me("notice")
    def notice_proxy_on_nginx(self):
        self.proxy_on_nginx(self.nginx_template, self.nginx_tmp, self.nginx_file_remote)

    @status_me("notice")
    def notice_apptest(self):
        self.app_test(project=self.project)

    @status_me("notice")
    def init_notice_mysql(self):
        self.init_mysql()

    def run_apptest(self):
        self.app_test(project=self.project)

    def run(self):
        self.push_notice_images()
        self.init_notice_mysql()
        self.deploy_notice_istio()
        self.deploy_notice_configmap()
        self.start_notice_service()
        self.notice_proxy_on_nginx()
        self.prepare_notice_data()
        self.project_pod_check()
        self.notice_apptest()

