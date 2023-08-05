from __future__ import absolute_import
from __future__ import unicode_literals

from laipvt.interface.serviceinterface import ServiceInterface
from laipvt.sysutil.util import status_me


class OcrTableController(ServiceInterface):
    def __init__(self, check_result, service_path):
        super(OcrTableController, self).__init__(check_result, service_path)
        self.tf_name = "ocr-table"

    @status_me("ocr_table")
    def push_table_images(self):
        self.push_images(self.project)

    @status_me("ocr_table")
    def start_table_service(self):
        self._create_namespace(namespaces=self.namespaces,
                               istio_injection_namespaces=self.istio_injection_namespaces)
        self.start_service(project=self.project, version=self.private_deploy_version, tf_name=self.tf_name)

    @status_me("ocr_table")
    def prepare_table_data(self):
        self.prepare_data(project=self.project)

    def run(self):
        self.push_table_images()
        self.start_table_service()
        self.prepare_table_data()
