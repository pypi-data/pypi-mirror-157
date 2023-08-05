#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import os
import re
import json
from laipvt.helper.errors import Helper
from laipvt.sysutil.gvalue import CHECK_FILE, PROJECT_INFO_FILE
from laipvt.sysutil.util import find
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
from laipvt.controller.service.notice import NoticeController
from laipvt.controller.service.ocr_text import OcrTextController
from laipvt.controller.service.ocr_table import OcrTableController
from laipvt.controller.service.ocr_idcard_server import OcrIdcardController
from laipvt.controller.service.rpa_collaboration import RpaCollaborationController
from laipvt.controller.service.ocr_layout_analysis import OcrLayoutAnalysisController
from laipvt.controller.service.ocr_bizlicense import OcrBizlicenseController
from laipvt.controller.middleware.monitor import MonitorController
from laipvt.controller.middleware.keepalived import KeepalivedController
from laipvt.handler.middlewarehandler import EtcdConfigHandler, MysqlConfigHandler, EsConfigHandler, \
    MinioConfigHandler, RabbitmqConfigHandler, RedisConfigHandler, HarborConfigHandler, NginxConfigHandler, \
    IdentityConfigHandler, SiberConfigHandler, OcrConfigHandler, MonitorConfigHandler, KeepalivedConfigHandler
from laipvt.sysutil.util import write_to_file, read_form_json_file, gen_https_self_signed_ca, modify_umask
from laipvt.sysutil.kube_common import wait_pod_running
from laipvt.sysutil.print_info import print_project_info
from laipvt.sysutil.check import is_pre_check, check_use_https_ca, check_https_ca_self_signed

def deploy_main(args):
    # 获取前置检查结果
    check_result_file = CHECK_FILE
    check_result = CheckResultHandler(check_result_file)

    if args.targzFile:
        if not args.isCheck:
            if not is_pre_check():
                print(Helper().PRECHECK_FAILED)
                exit(2)

        # 设置umask
        modify_umask(check_result=check_result, is_set=True)
        if not check_use_https_ca():
            print(Helper().HTTPS_CERTS_ERROR)
            exit(2)

        if check_https_ca_self_signed():
            gen_https_self_signed_ca()

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
        project_dict = {"PKG": PKG, "ID": ID}
        write_to_file(PROJECT_INFO_FILE, json.dumps(project_dict, indent=4))
        deploy_package = DeployPackageHandler(PKG, ID)
        if not os.path.exists(PKG_DIR):
            deploy_package.unpack()



        # 解析部署包
        parse_package = deploy_package.parse()
        kubernetes_package = parse_package.kubernetes
        middleware_package = parse_package.middleware
        harbor_package = parse_package.harbor

        if not os.path.exists(os.path.join(PKG_DIR, "kubernetes")):
            kubernetes_package.kubernetes_unpack()
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

        # install kubernetes
        if not args.sikpKubernetes:
            kube_info = kubernetes_package.parse()
            kube = KubeController(check_result, kube_info)
            kube.add_hosts()
            kube.system_prepare()
            kube.init_primary_master()
            kube.cp_kube_config()
            kube.kube_completion()
            kube.install_network_plugin()
            kube.join_master()
            kube.join_node()
            kube.install_helm()
            kube.install_istio()
            kube.install_rook()
            kube.install_nvidia_device_plugin()
            kube.install_chaosblade()
            # 更新nginx服务tcp代理apiserever cluster
            nginx.renew_apiserver_config()
            # 临时解决istio vs 命名空间问题
            kube.create_namespace()


        # install service
        services = {
            "license": LicenseController,
            "mage": MageController,
            "entcmd": CommanderController,
            "chatbot": ChatbotController,
            "nlp": NlpController,
            "captcha": CaptchaController,
            "ocr": OcrStandardController,
            "ocr_3rd": OcrController,
            "ocr_seal": SealController,
            "entuc": UserCenterController,
            "dataservice": DataServiceController,
            "notice": NoticeController,
            "ocr_text": OcrTextController,
            "ocr_table": OcrTableController,
            "ocr_idcard": OcrIdcardController,
            "rpa-collaboration": RpaCollaborationController,
            "ocr_layout_analysis": OcrLayoutAnalysisController,
            "ocr_bizlicense": OcrBizlicenseController,
        }

        middlewares = {
            "etcd": (EtcdConfigHandler, EtcdController),
            "minio": (MinioConfigHandler, MinioController),
            "redis": (RedisConfigHandler, RedisController),
            "mysql": (MysqlConfigHandler, MysqlController),
            "elasticsearch": (EsConfigHandler, EsController),
            "rabbitmq": (RabbitmqConfigHandler, RabbitmqController),
        }

        for s in parse_package.service:
            dir_dict = {}
            for i in os.listdir(PKG_DIR):
                # 匹配项目名称，找出部署包
                project_name_find = re.findall(r'(.*)-\d\.{0,3}\d{0,3}_\d{14}.tar.gz', i)
                if project_name_find:
                    dir_dict[project_name_find[0]] = i

            if s.project_name in dir_dict:
                s.unpack(package_name=dir_dict[s.project_name])
                service_path = s.parse()

                # 遍历服务需要的中间件列表，依次安装
                middleware_list = service_path.config.middleware
                middleware_list.insert(0, "etcd")

                for mid in middleware_list:
                    path = middleware_package.parse()[mid]
                    config = middlewares[mid][0]()
                    middleware = middlewares[mid][1](check_result, config, path)
                    middleware.deploy()

                if s.project_name == "ocr_3rd":
                    ocr_handler = OcrConfigHandler()
                    deploy_service = services[s.project_name](service_path, check_result, ocr_handler, s.root_dir)
                else:
                    deploy_service = services[s.project_name](check_result, service_path)

                deploy_service.run()

        # check all pod status
        if not wait_pod_running:
            print("kubernetes集群中有pod启动状态异常，请检查: kubectl get pod -A")
            exit(2)

        # install siber
        # siber_path = middleware_package.parse().siber
        # siber_config = SiberConfigHandler()
        # siber = SiberController(check_result, siber_config, siber_path)
        # siber.deploy_siber()
        # for s in parse_package.service:
        #     if s.project_name == "mage":
        #         siber.replace_mage_collection_tag(parse_package.config.siber_tags)
        #     elif s.project_name == "commander":
        #         exit()

        # 设置umask
        modify_umask(check_result=check_result, is_set=False)
        # 打印帮助信息
        print_project_info()

    if args.which == "license":
        if args.LicenseFile:
            if os.path.exists(args.LicenseFile):
                # print(args.LicenseFile)
                project_dict = read_form_json_file(PROJECT_INFO_FILE)

                # 解析大包
                deploy_package = DeployPackageHandler(project_dict["PKG"], project_dict["ID"])
                parse_package = deploy_package.parse()
                license_package = parse_package.license
                # license_package.unpack()
                license_path = license_package.parse()
                license = LicenseController(check_result, license_path)
                license.renew_license(license_file=args.LicenseFile)
            else:
                print("请检查指定的新授权文件是否存在: {}".format(args.LicenseFile))
                exit(1)

        if args.OcrLicenseFile:
            if os.path.exists(args.OcrLicenseFile):
                project_dict = read_form_json_file(PROJECT_INFO_FILE)

                deploy_package = DeployPackageHandler(project_dict["PKG"], project_dict["ID"])
                parse_package = deploy_package.parse()
                renew_flag = False
                for s in parse_package.service:
                    if s.project_name == "ocr":
                        service_path = s.parse()
                        ocr_handler = OcrConfigHandler()
                        deploy_ocr = OcrController(service_path, check_result, ocr_handler, s.root_dir)
                        deploy_ocr.renew_license(license_file=args.OcrLicenseFile)
                        renew_flag = True

                if not renew_flag:
                    print("OCR license未更新成功，请检查是否存在合合服务")
                    exit(2)

    if args.which == "add":
        if args.Monitor:
            project_dict = read_form_json_file(PROJECT_INFO_FILE)
            deploy_package = DeployPackageHandler(project_dict["PKG"], project_dict["ID"])
            parse_package = deploy_package.parse()
            middleware_package = parse_package.middleware

            monitor_path = middleware_package.parse().monitor
            monitor_config = MonitorConfigHandler()
            monitor = MonitorController(check_result, monitor_config, monitor_path)
            monitor.deploy_monitor()

        if args.Keepalive:
            project_dict = read_form_json_file(PROJECT_INFO_FILE)
            deploy_package = DeployPackageHandler(project_dict["PKG"], project_dict["ID"])
            parse_package = deploy_package.parse()
            middleware_package = parse_package.middleware

            keepalive_path = middleware_package.parse().keepalived
            keepalive_config = KeepalivedConfigHandler()
            keepalive = KeepalivedController(check_result, keepalive_config, keepalive_path)
            keepalive.deploy_keepalived()

    if args.Service:
        print(args.Service)

        package_info = read_form_json_file(PROJECT_INFO_FILE)
        deploy_package = DeployPackageHandler(package_info["PKG"], package_info["ID"])
        PKG_DIR = os.path.join(package_info["PKG"], package_info["ID"])

        # 解析
        parse_package = deploy_package.parse()
        service_package = parse_package.service

        for s in service_package:
            dir_dict = {}
            for i in os.listdir(PKG_DIR):
                # 匹配项目名称，找出服务部署包
                project_name_find = re.findall(r'(.*)-\d\.{0,3}\d{0,3}_\d{14}.tar.gz', i)
                if project_name_find:
                    dir_dict[project_name_find[0]] = i

            if s.project_name in dir_dict:
                s.unpack(package_name=dir_dict[s.project_name])
                service_path = s.parse()
                # print(service_path)

                if args.Service == "chatbot":
                    deploy_service = ChatbotController(check_result, service_path)
                    deploy_service.run_apptest()
                    exit(0)
                elif args.Service == "entcmd":
                    deploy_service = CommanderController(check_result, service_path)
                    deploy_service.run_apptest()
                    exit(0)
                elif args.Service == "rpa-collaboration":
                    deploy_service = RpaCollaborationController(check_result, service_path)
                    deploy_service.run_apptest()
                    exit(0)
                elif args.Service == "notice":
                    deploy_service = NoticeController(check_result, service_path)
                    deploy_service.run_apptest()
                    exit(0)
