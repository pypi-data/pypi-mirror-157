from __future__ import absolute_import
from __future__ import unicode_literals

from laipvt.interface.serviceinterface import ServiceInterface
from laipvt.sysutil.util import status_me, path_join


class OcrStandardController(ServiceInterface):
    def __init__(self, check_result, service_path):
        super(OcrStandardController, self).__init__(check_result, service_path)
        self.tf_name = "ocr"


    @status_me("ocr")
    def push_ocr_images(self):
        self.push_images(self.project)

    @status_me("ocr")
    def deploy_ocr_configmap(self):
        self.deploy_all_configmap()

    @status_me("ocr")
    def start_ocr_service(self):
        self._create_namespace(namespaces=self.namespaces,
                               istio_injection_namespaces=self.istio_injection_namespaces)
        self.start_service(project=self.project, version=self.private_deploy_version, tf_name=self.tf_name)

    @status_me("ocr")
    def prepare_ocr_data(self):
        self.prepare_data(project=self.project)

    @status_me("ocr")
    def apply_ocr_model_svc(self):
        model_svc_src = path_join(self.templates_dir, "model-svc")
        model_svc_dest = path_join(self.deploy_dir, "model-svc")
        self._send_file(src=model_svc_src, dest=model_svc_dest)
        cmd = "kubectl apply -R -f {}".format(model_svc_dest)
        self._exec_command_to_host(cmd=cmd, server=self.harbor_hosts[0])

    def run(self):
        self.push_ocr_images()
        self.deploy_ocr_configmap()
        self.start_ocr_service()
        self.prepare_ocr_data()
        self.apply_ocr_model_svc()
