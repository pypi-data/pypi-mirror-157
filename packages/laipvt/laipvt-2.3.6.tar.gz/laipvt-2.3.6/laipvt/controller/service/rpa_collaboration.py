from __future__ import absolute_import
from __future__ import unicode_literals

from laipvt.interface.serviceinterface import ServiceInterface
from laipvt.sysutil.util import status_me, path_join


class RpaCollaborationController(ServiceInterface):
    def __init__(self, check_result, service_path):
        super(RpaCollaborationController, self).__init__(check_result, service_path)
        self.nginx_template = path_join(self.templates_dir, "nginx/http/nginx-rpa-collaboration.tmpl")
        self.nginx_tmp = path_join("/tmp", "nginx-rpa-collaboration.conf")
        self.nginx_file_remote = path_join(self.deploy_dir, "nginx/http/nginx-rpa-collaboration.conf")


    @status_me("rpa_collaboration")
    def push_rpa_collaboration_images(self):
        self.push_images(self.project)

    @status_me("rpa_collaboration")
    def init_rpa_collaboration_mysql(self):
        self.init_mysql()

    @status_me("rpa_collaboration")
    def init_rpa_collaboration_minio(self):
        self.init_minio()

    @status_me("rpa_collaboration")
    def deploy_rpa_collaboration_configmap(self):
        self.deploy_all_configmap()

    @status_me("rpa_collaboration")
    def deploy_rpa_collaboration_istio(self):
        self.deploy_istio()

    @status_me("rpa_collaboration")
    def start_rpa_collaboration_service(self):
        self._create_namespace(namespaces=self.namespaces,
                               istio_injection_namespaces=self.istio_injection_namespaces)
        self.start_service(project=self.project, version=self.private_deploy_version)

    @status_me("rpa_collaboration")
    def prepare_rpa_collaboration_data(self):
        self.prepare_data(project=self.project)

    @status_me("rpa_collaboration")
    def rpa_collaboration_proxy_on_nginx(self):
        self.proxy_on_nginx(self.nginx_template, self.nginx_tmp, self.nginx_file_remote)

    @status_me("rpa_collaboration")
    def init_rpa_collaboration_entuc_clients(self):
        self.init_usercenter_clients(project=self.project)

    @status_me("rpa_collaboration")
    def rpa_collaboration_apptest(self):
        self.app_test(project=self.project)

    def run_apptest(self):
        self.app_test(project=self.project)

    def run(self):
        self.push_rpa_collaboration_images()
        self.init_rpa_collaboration_mysql()
        self.init_rpa_collaboration_minio()
        self.deploy_rpa_collaboration_istio()
        self.deploy_rpa_collaboration_configmap()
        self.start_rpa_collaboration_service()
        self.prepare_rpa_collaboration_data()
        self.rpa_collaboration_proxy_on_nginx()
        self.project_pod_check()
        self.init_rpa_collaboration_entuc_clients()
        self.rpa_collaboration_apptest()
