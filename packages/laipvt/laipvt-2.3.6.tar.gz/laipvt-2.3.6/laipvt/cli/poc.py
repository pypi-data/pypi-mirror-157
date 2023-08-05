#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import os
import json
from laipvt.helper.errors import Helper
from laipvt.sysutil.gvalue import CHECK_FILE, PROJECT_INFO_FILE
from laipvt.sysutil.args_poc import Args
from laipvt.handler.confighandler import CheckResultHandler
from laipvt.handler.packagehandler import DeployPackageHandler
from laipvt.controller.kubernetes.kube import KubeController
from laipvt.controller.middleware.harbor import HarborController
from laipvt.controller.middleware.nginx import NginxController
from laipvt.controller.middleware.etcd import EtcdController
from laipvt.controller.middleware.minio import MinioController
from laipvt.controller.middleware.redis import RedisController
from laipvt.controller.middleware.mysql import MysqlController
from laipvt.controller.middleware.elasticsearch import EsController
from laipvt.controller.middleware.rabbitmq import RabbitmqController
from laipvt.controller.middleware.identity import IdentityController
from laipvt.controller.middleware.siber import SiberController
from laipvt.controller.service.license import LicenseController
from laipvt.controller.service.mage import MageController
from laipvt.controller.service.ocr_standard import OcrStandardController
from laipvt.controller.service.nlp import NlpController
from laipvt.controller.service.seal import SealController
from laipvt.controller.service.captcha import CaptchaController
from laipvt.controller.service.commander import CommanderController
from laipvt.controller.service.ocr import OcrController
from laipvt.controller.service.chatbot import ChatbotController
from laipvt.controller.service.usercenter import UserCenterController
from laipvt.controller.service.dataservice import DataServiceController
from laipvt.controller.service.ocr_text import OcrTexttableController
from laipvt.controller.service.ocr_idcard_server import OcrIdcardController
from laipvt.controller.middleware.monitor import MonitorController
from laipvt.controller.middleware.keepalived import KeepalivedController
from laipvt.handler.middlewarehandler import EtcdConfigHandler, MysqlConfigHandler, EsConfigHandler, \
    MinioConfigHandler, RabbitmqConfigHandler, RedisConfigHandler, HarborConfigHandler, NginxConfigHandler, \
    IdentityConfigHandler, SiberConfigHandler, OcrConfigHandler, MonitorConfigHandler, KeepalivedConfigHandler
from laipvt.sysutil.util import find, write_to_file, read_form_json_file, gen_https_self_signed_ca, modify_umask
from laipvt.sysutil.kube_common import wait_pod_running
from laipvt.sysutil.check import is_pre_check, check_use_https_ca, check_https_ca_self_signed




# def main():
#     print("test")

def main():
    args = Args().parse_args()

    if not args.isCheck:
        if not is_pre_check():
            print(Helper().PRECHECK_FAILED)
            exit(2)

    # 获取前置检查结果
    check_result_file = CHECK_FILE
    check_result = CheckResultHandler(check_result_file)

    # 设置umask
    modify_umask(check_result=check_result, is_set=True)

    if args.targzFile:
        pkg_path = False
        if not os.path.exists(args.targzFile):
            cwd = [os.getcwd(), check_result.deploy_dir]
            for d in cwd:
                pkg_path = find(d, args.targzFile, file=True)
                if pkg_path:
                    break
        else:
            pkg_path = os.path.join(os.getcwd(), args.targzFile)
        if not pkg_path:
            print(Helper().FILE_NOT_FOUND)
            exit(2)
        PKG = os.path.dirname(pkg_path)
        ID = os.path.basename(pkg_path).split(".")[0]
        PKG_DIR = pkg_path.split(".")[0]

        # 将项目ID和path写入文件缓存
        project_dict = { "PKG": PKG, "ID": ID }
        write_to_file(PROJECT_INFO_FILE, json.dumps(project_dict, indent=4))

        deploy_package = DeployPackageHandler(PKG, ID)
        if not os.path.exists(PKG_DIR):
            deploy_package.unpack()
        # 解析
        parse_package = deploy_package.parse()
        kubernetes_package = parse_package.kubernetes
        middleware_package = parse_package.middleware
        harbor_package = parse_package.harbor

        if not os.path.exists(os.path.join(PKG_DIR, "middleware")):
            middleware_package.unpack()
        if not os.path.exists(os.path.join(PKG_DIR, "harbor")):
            harbor_package.unpack()

        # install harbor
        haror_path = harbor_package.parse().harbor
        harbor_config = HarborConfigHandler()
        harbor = HarborController(check_result, harbor_config, haror_path)
        harbor.install_harbor()

        # install nginx
        nginx_package = middleware_package.parse().nginx
        nginx_config = NginxConfigHandler()
        nginx = NginxController(check_result, nginx_config, nginx_package)
        nginx.install_nginx()


        # # install identity
        # identity_path = middleware_package.parse().identity
        # identity_config = IdentityConfigHandler()
        # identity = IdentityController(check_result, identity_config, identity_path)
        # identity.deploy_identity()
