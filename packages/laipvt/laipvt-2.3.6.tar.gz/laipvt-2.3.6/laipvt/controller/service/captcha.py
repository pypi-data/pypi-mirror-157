from __future__ import absolute_import
from __future__ import unicode_literals

from laipvt.interface.serviceinterface import ServiceInterface
from laipvt.sysutil.util import path_join, status_me


class CaptchaController(ServiceInterface):
    def __init__(self, check_result, service_path):
        super(CaptchaController, self).__init__(check_result, service_path)
        self.tf_name = "verification"

    @status_me("captcha")
    def push_captcha_images(self):
        self.push_images(self.project)

    @status_me("captcha")
    def start_captcha_service(self):
        self._create_namespace(namespaces=self.namespaces,
                               istio_injection_namespaces=self.istio_injection_namespaces)
        self.start_service(project=self.project, version=self.private_deploy_version, tf_name=self.tf_name)

    @status_me("captcha")
    def prepare_captcha_data(self):
        self.prepare_data(project=self.project)

    def run(self):
        self.push_captcha_images()
        self.start_captcha_service()
        self.prepare_captcha_data()
