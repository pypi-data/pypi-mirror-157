from __future__ import absolute_import
from __future__ import unicode_literals

from laipvt.interface.serviceinterface import ServiceInterface
from laipvt.sysutil.util import status_me


class NlpController(ServiceInterface):
    def __init__(self, check_result, service_path):
        super(NlpController, self).__init__(check_result, service_path)

    @status_me("nlp")
    def push_nlp_images(self):
        self.push_images(self.project)

    @status_me("nlp")
    def deploy_nlp_configmap(self):
        self.deploy_all_configmap()

    @status_me("nlp")
    def start_nlp_service(self):
        self._create_namespace(namespaces=self.namespaces,
                               istio_injection_namespaces=self.istio_injection_namespaces)
        self.start_service(project=self.project, version=self.private_deploy_version)

    @status_me("nlp")
    def prepare_nlp_data(self):
        self.prepare_data(project=self.project)

    def run(self):
        self.push_nlp_images()
        self.deploy_nlp_configmap()
        self.start_nlp_service()
        self.prepare_nlp_data()
        self.project_pod_check()

