from __future__ import absolute_import
from __future__ import unicode_literals

from laipvt.interface.serviceinterface import ServiceInterface
from laipvt.sysutil.util import path_join, log, status_me



class DataServiceController(ServiceInterface):
    def __init__(self, check_result, service_path):
        super(DataServiceController, self).__init__(check_result, service_path)
        self.nginx_template = path_join(self.templates_dir, "nginx/http/nginx-dataservice.tmpl")
        self.nginx_tmp = path_join("/tmp", "nginx-dataservice.conf")
        self.nginx_file_remote = path_join(self.deploy_dir, "nginx/http/nginx-dataservice.conf")

    @status_me("dataservice")
    def push_dataservice_images(self):
        self.push_images(self.project)

    @status_me("dataservice")
    def deploy_dataservice_configmap(self):
        self.deploy_all_configmap()

    @status_me("dataservice")
    def start_dataservice_service(self):
        self._create_namespace(namespaces=self.namespaces,
                               istio_injection_namespaces=self.istio_injection_namespaces)
        self.start_service(project=self.project, version=self.private_deploy_version)

    @status_me("dataservice")
    def prepare_dataservice_data(self):
        self.prepare_data(project=self.project)

    @status_me("dataservice")
    def dataservice_proxy_on_nginx(self):
        self.proxy_on_nginx(self.nginx_template, self.nginx_tmp, self.nginx_file_remote)


    def run(self):
        self.push_dataservice_images()
        self.deploy_dataservice_configmap()
        self.start_dataservice_service()
        self.dataservice_proxy_on_nginx()
        self.prepare_dataservice_data()
        self.project_pod_check()

