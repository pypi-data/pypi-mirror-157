#!/bin/env python
# -*- encoding: utf-8 -*-
import json
import os
from laipvt.sysutil.conf import status_file


dict_tmpl = {
    "basesystem": {
        "kubernetes_unpack": 0,
        "install_harbor": 0,
        "install_nginx": 0,
        "add_hosts": 0,
        "system_prepare": 0,
        "init_primary_master": 0,
        "cp_kube_config": 0,
        "kube_completion": 0,
        "install_network_plugin": 0,
        "join_master": 0,
        "join_node": 0,
        "install_helm": 0,
        "install_istio": 0,
        "install_rook": 0,
        "install_nvidia_device_plugin": 0,
        "install_chaosblade": 0,
        "create_namespace": 0
    },
    "nginx": {
        "renew_apiserver_config": 0
    },
    "middleware": {
        "deploy_etcd": 0,
        "deploy_license": 0,
        "deploy_minio": 0,
        "deploy_mysql": 0,
        "deploy_redis": 0,
        "deploy_es": 0,
        "deploy_rabbitmq": 0,
        "deploy_identity": 0,
        "deploy_commander_identity": 0,
        "deploy_monitor": 0,
        "deploy_keepalived": 0,
        "deploy_siber": 0
    },
    "license": {
        "push_license_images": 0,
        "deploy_license_configmap": 0,
        "deploy_license_istio": 0,
        "prepare_license_data_file": 0,
        "start_license_service": 0,
        "license_proxy_on_nginx": 0,
        "init_license_entuc_clients": 0
    },
    "mage": {
        "init_mage_mysql": 0,
        "init_identity_user": 0,
        "init_minio_data": 0,
        "push_mage_images": 0,
        "deploy_configmap": 0,
        "deploy_mage_istio": 0,
        "start_mage_service": 0,
        "mage_proxy_on_nginx": 0,
        "mage_transfer_data": 0,
        "hide_menu": 0,
        "init_mage_entuc_clients": 0
    },
    "chatbot": {
        "push_chatbot_images": 0,
        "init_chatbot_mysql": 0,
        "deploy_chatbot_configmap": 0,
        "deploy_chatbot_istio": 0,
        "start_chatbot_service": 0,
        "chatbot_proxy_on_nginx": 0,
        "prepare_data_chatbot": 0,
        "chatbot_apptest": 0,
        "init_chatbot_entuc_clients": 0
    },
    "nlp": {
        "push_nlp_images": 0,
        "deploy_nlp_configmap": 0,
        "start_nlp_service": 0,
        "prepare_nlp_data": 0
    },
    "ocr": {
        "push_ocr_images": 0,
        "deploy_ocr_configmap": 0,
        "start_ocr_service": 0,
        "prepare_ocr_data": 0,
        "apply_ocr_model_svc": 0
    },
    "ocr_text": {
        "push_text_images": 0,
        "start_text_service": 0,
        "prepare_text_data": 0
    },
    "ocr_table": {
        "push_table_images": 0,
        "start_table_service": 0,
        "prepare_table_data": 0
    },
    "ocr_bizlicense": {
        "push_bizlicense_images": 0,
        "start_bizlicense_service": 0,
        "prepare_bizlicense_data": 0
    },
    "ocr_idcard": {
        "push_ocr_idcard_images": 0,
        "start_ocr_idcard_service": 0,
        "prepare_ocr_idcard_data": 0
    },
    "captcha": {
        "push_captcha_images": 0,
        "start_captcha_service": 0,
        "prepare_captcha_data": 0
    },
    "seal": {
        "push_seal_images": 0,
        "start_seal_service": 0,
        "prepare_seal_data": 0
    },
    "ocr_layout_analysis": {
        "push_layout_analysis_images": 0,
        "start_layout_analysis_service": 0,
        "prepare_layout_analysis_data": 0
    },
    "rpa_collaboration": {
        "push_rpa_collaboration_images": 0,
        "init_rpa_collaboration_mysql": 0,
        "init_rpa_collaboration_minio": 0,
        "deploy_rpa_collaboration_configmap": 0,
        "deploy_rpa_collaboration_istio": 0,
        "start_rpa_collaboration_service": 0,
        "prepare_rpa_collaboration_data": 0,
        "rpa_collaboration_proxy_on_nginx": 0,
        "init_rpa_collaboration_entuc_clients": 0,
        "rpa_collaboration_apptest": 0
    },
    "commander": {
        "init_commander_mysql": 0,
        "init_commander_rabbitmq": 0,
        "init_minio_data": 0,
        "init_commander_redis": 0,
        "deploy_configmap": 0,
        "deploy_commander_istio": 0,
        "push_commander_images": 0,
        "start_commander_service": 0,
        "commander_proxy_on_nginx": 0,
        "init_tenant": 0,
        "commander_apptest": 0,
        "init_commander_entuc_clients": 0
    },
    "usercenter": {
        "push_usercenter_images": 0,
        "init_minio_data": 0,
        "init_usercenter_mysql": 0,
        "init_usercenter_rabbitmq": 0,
        "deploy_configmap": 0,
        "deploy_usercenter_istio": 0,
        "start_usercenter_service": 0,
        "usercenter_proxy_on_nginx": 0,
        "usercenter_init_user": 0
    },
    "dataservice": {
        "push_dataservice_images": 0,
        "deploy_dataservice_configmap": 0,
        "start_dataservice_service": 0,
        "dataservice_proxy_on_nginx": 0,
        "prepare_dataservice_data": 0
    },
    "notice": {
        "push_notice_images": 0,
        "init_notice_mysql": 0,
        "deploy_notice_istio": 0,
        "deploy_notice_configmap": 0,
        "start_notice_service": 0,
        "notice_proxy_on_nginx": 0,
        "prepare_notice_data": 0,
        "notice_apptest": 0
    }
}


class Status:
    def __init__(self):
        self.status_file = status_file
        self.STATUS_SUCCESS = 1
        self.STATUS_FAILED = 2
        self.STATUS_NOT_RUNNING = 0
        self.status_dicts = [self.STATUS_NOT_RUNNING, self.STATUS_SUCCESS, self.STATUS_FAILED]
        if os.path.exists(self.status_file):
            with open(self.status_file, 'r') as fp:
                self.status = json.load(fp)
        else:
            with open(self.status_file, 'a') as fp:
                fp.write(json.dumps(dict_tmpl, indent=4))
            self.status = dict_tmpl

    def reset_status(self):
        status = json.loads(json.dumps(dict_tmpl))
        with open(self.status_file, "w") as sf:
            json.dump(status, sf, indent=4)

    def _reload(self):
        with open(self.status_file) as sf:
            self.status = json.load(sf)

    def _update(self):
        with open(self.status_file, "w") as sf:
            json.dump(self.status, sf, indent=4)
        self._reload()

    def get_status_failed(self, project_name):
        step_list = []
        proj = self.status[project_name]
        for step in proj:
            if proj[step] == self.STATUS_FAILED:
                step_list.append(step)
        return step_list

    def get_status(self, project, step):
        try:
            self._reload()
            return self.status_dicts[self.status[project][step]]
        except KeyError:
            self.update_status(project, step, 0)
            self._reload()
            return self.status_dicts[self.status[project][step]]

    def update_status(self, project, step, value):
        try:
            self.status[project][step] = int(self.status_dicts[value])
            self._update()
            return True
        except IndexError:
            return False
