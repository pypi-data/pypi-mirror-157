from __future__ import absolute_import
from __future__ import unicode_literals

from laipvt.interface.serviceinterface import ServiceInterface
from laipvt.sysutil.util import status_me


class OcrIdcardController(ServiceInterface):
    def __init__(self, check_result, service_path):
        super(OcrIdcardController, self).__init__(check_result, service_path)
        self.tf_name = "ocr-idcard-server"

    @status_me("ocr_idcard")
    def push_ocr_idcard_images(self):
        self.push_images(self.project)

    @status_me("ocr_idcard")
    def start_ocr_idcard_service(self):
        self._create_namespace(namespaces=self.namespaces,
                               istio_injection_namespaces=self.istio_injection_namespaces)
        self.start_service(project=self.project, version=self.private_deploy_version, tf_name=self.tf_name)

    @status_me("ocr_idcard")
    def prepare_ocr_idcard_data(self):
        self.prepare_data(project=self.project)

    def run(self):
        self.push_ocr_idcard_images()
        self.start_ocr_idcard_service()
        self.prepare_ocr_idcard_data()
