from __future__ import absolute_import
from __future__ import unicode_literals

from laipvt.interface.serviceinterface import ServiceInterface
from laipvt.sysutil.util import status_me


class OcrBizlicenseController(ServiceInterface):
    def __init__(self, check_result, service_path):
        super(OcrBizlicenseController, self).__init__(check_result, service_path)
        self.tf_name = "ocr-bizlicense"

    @status_me("ocr_bizlicense")
    def push_bizlicense_images(self):
        self.push_images(self.project)

    @status_me("ocr_bizlicense")
    def start_bizlicense_service(self):
        self._create_namespace(namespaces=self.namespaces,
                               istio_injection_namespaces=self.istio_injection_namespaces)
        self.start_service(project=self.project, version=self.private_deploy_version, tf_name=self.tf_name)

    @status_me("ocr_bizlicense")
    def prepare_bizlicense_data(self):
        self.prepare_data(project=self.project)

    def run(self):
        self.push_bizlicense_images()
        self.start_bizlicense_service()
        self.prepare_bizlicense_data()
