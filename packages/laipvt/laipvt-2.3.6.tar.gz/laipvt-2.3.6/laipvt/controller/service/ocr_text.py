from __future__ import absolute_import
from __future__ import unicode_literals

from laipvt.interface.serviceinterface import ServiceInterface
from laipvt.sysutil.util import status_me


class OcrTextController(ServiceInterface):
    def __init__(self, check_result, service_path):
        super(OcrTextController, self).__init__(check_result, service_path)
        self.tf_name = "ocr-text"

    @status_me("ocr_text")
    def push_text_images(self):
        self.push_images(self.project)

    @status_me("ocr_text")
    def start_text_service(self):
        self._create_namespace(namespaces=self.namespaces,
                               istio_injection_namespaces=self.istio_injection_namespaces)
        self.start_service(project=self.project, version=self.private_deploy_version, tf_name=self.tf_name)

    @status_me("ocr_text")
    def prepare_text_data(self):
        self.prepare_data(project=self.project)

    def run(self):
        self.push_text_images()
        self.start_text_service()
        self.prepare_text_data()
