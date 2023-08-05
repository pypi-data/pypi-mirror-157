from __future__ import absolute_import
from __future__ import unicode_literals

from laipvt.sysutil.conf import YamlConfig
from laipvt.sysutil.gvalue import PORT_MAP, DEPLOY_LANGUAGE

module_require_tfserver = ("ocr_standard", "captcha", "nlp", "ocr_seal")
tfserver_name = {
    "ocr_standard": ["ocr-ctpn-tf-server", "ocr-text-recognition-tf-server",
                     "ocr-unet-table-tf-serving", "semantic-correct"],
    "captcha": ["verification-tf-serving"],
    "nlp": ["bert-service-tf"],
    "ocr_seal": ["ocr-seal-tf-serving"]
}

tfserver_image_name = {
    "ocr_standard": "tfserving",
    "captcha": "tfserving",
    "nlp": "tfserving",
    "ocr_seal": "tfserving"
}

# service_module_relation = {
#     "commander": [x for x in range(0, 9)],
#     "usercenter": [10],
#     "dataservice": [81],
#     "mage": [x for x in range(31, 51)],
#     # "wulai": [x for x in range(11, 31)],
#     "chatbot": [x for x in range(11, 31)],
#     "nlp": [33, 34, 35],
#     "captcha": [32],
#     "ocr_text_table": [36, 37],
#     "ocr_3rd": [x for x in range(51, 80)],
#     "ocr_seal": [38, 39],
#     "ocr": [40],
#     "ocr_idcard_server": [41, 42]
# }
service_module_relation = {
    # "entcmd": [x for x in range(0, 9)],
    # "entuc": [10],
    "entcmd": [10],
    "entuc": [0],
    "notice": [6],
    "dataservice": [16],
    "mage": [x for x in range(31)],
    # "wulai": [x for x in range(11, 31)],
    "chatbot": [x for x in range(11)],
    "nlp": [34],
    "captcha": [32],
    "ocr_text": [36, 37],
    "ocr_table": [38, 39],
    "ocr_seal": [40],
    "ocr_idcard": [42],
    "ocr": [30],
    "ocr_3rd": [x for x in range(61, 104)]
}

machine_module_relation = {
    "cpu": [x for x in range(34, 129) if x % 2 == 0],
    "gpu": [x for x in range(34, 129) if x % 2 != 0]
}
ocr_standard = range(36, 51)
ocr = range(51, 80)
if DEPLOY_LANGUAGE == "cn":
    module_info = {
        0: ("entuc", "usercenter用户中心"),
        1: ("license", "License授权服务"),
        5: ("rpa-collaboration", "人机协同中心"),
        6: ("notice", "通知中心"),
        10: ("entcmd", "Enterprise Commander"),
        11: ("chatbot", "ChatBot吾来对话机器人"),
        16: ("dataservice", "数据服务"),
        30: ("ocr", "ocr go服务"),
        31: ("mage", "UiBot Mage"),
        32: ("captcha", "验证码识别"),
        33: ("geo", "标准地址"),
        34: ("nlp", "文本分类、信息抽取"),
        36: ("ocr_text_cpu", "通用文字识别(标准版 CPU)"),
        37: ("ocr_text", "通用文字识别(标准版 GPU)"),
        38: ("ocr_table_cpu", "通用表格识别(标准版 CPU)"),
        39: ("ocr_table", "通用表格识别(标准版 GPU)"),
        40: ("ocr_seal_cpu", "印章识别(标准版 CPU)"),
        41: ("ocr_seal", "印章识别(标准版 GPU)"),
        42: ("ocr_idcard_cpu", "通用卡证识别(标准版CPU)"),
        43: ("ocr_idcard", "通用卡证识别(标准版GPU)"),
        45: ("ocr_layout_analysis", "版面分析CPU"),
        47: ("ocr_bizlicense", "营业执照GPU"),
        61: ("i_document", "通用文字识别(合合CPU)"),
        62: ("i_document_gpu", "通用文字识别(合合GPU)"),
        63: ("i_table", "通用表格识别(合合CPU)"),
        64: ("i_table_gpu", "通用表格识别(合合GPU)"),
        65: ("i_receipt", "通用多票据识别(合合CPU)"),
        66: ("i_receipt_gpu", "通用多票据识别(合合GPU)"),
        67: ("i_idcard", "通用卡证识别-身份证(合合CPU)"),
        68: ("i_idcard_gpu", "通用卡证识别-身份证(合合GPU)"),
        69: ("i_bankcard", "通用卡证识别-银行卡(合合CPU)"),
        70: ("i_bankcard_gpu", "通用卡证识别-银行卡(合合GPU)"),
        71: ("i_vehicle", "通用卡证识别-机动车登记证(合合CPU)"),
        72: ("i_vehicle_gpu", "通用卡证识别-机动车登记证(合合GPU)"),
        73: ("i_vehiclelicense", "通用卡证识别-机动车行驶证(合合CPU)"),
        74: ("i_vehiclelicense_gpu", "通用卡证识别-机动车行驶证(合合GPU)"),
        75: ("i_biz", "通用卡证识别-营业执照(合合CPU)"),
        76: ("i_biz_gpu", "通用卡证识别-营业执照(合合GPU)"),
        83: ("i_driverlicense", "通用卡证识别-驾驶证(合合CPU)"),
        84: ("i_driverlicense_gpu", "通用卡证识别-驾驶证(合合GPU)"),
        91: ("i_passport", "通用卡证识别-护照(合合CPU)"),
        92: ("i_passport_gpu", "通用卡证识别-护照(合合GPU)"),
        103: ("i_vehiclecert", "通用卡证识别-车辆合格证(合合CPU)"),
        104: ("i_vehiclecert_gpu", "通用卡证识别-车辆合格证(合合GPU)"),
        112: ("t_document_gpu", "通用文字识别 - 探智立方GPU"),
        114: ("t_table_gpu", "通用表格识别 - 探智立方GPU"),
        116: ("t_receipt_gpu", "通用多票据识别 - 探智立方GPU"),
        118: ("t_idcard_gpu", "通用卡证识别-身份证- 探智立方GPU"),
        120: ("t_biz_gpu", "通用卡证识别-营业执照-探智立方GPU"),
        122: ("t_driverlicense_gpu", "通用卡证识别-驾驶证-探智立方GPU"),
        124: ("t_vehiclelicense_gpu", "通用卡证识别-行驶证-探智立方GPU"),
        126: ("t_bankcard_gpu", "通用卡证识别-银行卡-探智立方GPU"),
        128: ("t_vehicle_gpu", "通用卡证识别-车辆登记证-探智立方GPU"),
        130: ("t_marriage_gpu", "通用卡证识别-结婚证-探智立方GPU"),
        132: ("t_hrb_gpu", "通用卡证识别-户口本-探智立方GPU"),
    }
else:
    module_info = {
        0: ("entuc", "Enterprise Usercenter"),
        1: ("license", "License Service"),
        5: ("rpa-collaboration", "RPA Collaboration"),
        6: ("notice", "Notice Center"),
        10: ("entcmd", "Enterprise Commander"),
        11: ("chatbot", "Conversational AI Platform"),
        16: ("dataservice", "Data Service"),
        30: ("ocr", "Ocr Go"),
        31: ("mage", "Intelligent Document Processing"),
        32: ("captcha", "Captcha"),
        33: ("geo", "Geo"),
        34: ("nlp", "Information Extraction Text Classification"),
        36: ("ocr_text_cpu", "Text REcognition(Standard Edition-CPU)"),
        37: ("ocr_text", "Text REcognition(Standard Edition-GPU)"),
        38: ("ocr_table_cpu", "Form Recognition（Standard Edition-CPU）"),
        39: ("ocr_table", "Form Recognition（Standard Edition-GPU）"),
        40: ("ocr_seal_cpu", "Seal Recognition(Standard Edition-CPU)"),
        41: ("ocr_seal", "Seal Recognition(Standard Edition-GPU)"),
        42: ("ocr_idcard_cpu", "Id Card Recognition(Standard Edition-CPU)"),
        43: ("ocr_idcard", "Id Card Recognition(Standard Edition-GPU)"),
        45: ("ocr_layout_analysis", "Layout Analysis CPU"),
        47: ("ocr_bizlicense", "ocr bizlicense GPU"),
        61: ("i_document", "Text REcognition(hehe CPU)"),
        62: ("i_document_gpu", "Text REcognition(hehe CPU)"),
        63: ("i_table", "Table REcognition(hehe CPU)"),
        64: ("i_table_gpu", "Table REcognition(hehe GPU)"),
        65: ("i_receipt", "Receipt REcognition(hehe CPU)"),
        66: ("i_receipt_gpu", "Receipt REcognition(hehe GPU)"),
        67: ("i_idcard", "IdCard REcognition(hehe CPU)"),
        68: ("i_idcard_gpu", "IdCard REcognition(hehe GPU)"),
        69: ("i_bankcard", "BankCard REcognition(hehe CPU)"),
        70: ("i_bankcard_gpu", "BankCard REcognition(hehe GPU)"),
        71: ("i_vehicle", "Vehicle REcognition(hehe CPU)"),
        72: ("i_vehicle_gpu", "Vehicle REcognition(hehe GPU)"),
        73: ("i_vehiclelicense", "Vehiclelicense REcognition(hehe CPU)"),
        74: ("i_vehiclelicense_gpu", "Vehiclelicense REcognition(hehe GPU)"),
        75: ("i_biz", "Biz REcognition(hehe GPU)"),
        76: ("i_biz_gpu", "Biz REcognition(hehe GPU)"),
        83: ("i_driverlicense", "Driver REcognition(hehe GPU)"),
        84: ("i_driverlicense_gpu", "Driver REcognition(hehe GPU)"),
        91: ("i_passport", "Passport REcognition(hehe GPU)"),
        92: ("i_passport_gpu", "Passport REcognition(hehe GPU)"),
        103: ("i_vehiclecert", "Vehiclecert REcognition(hehe GPU)"),
        104: ("i_vehiclecert_gpu", "Vehiclecert REcognition(hehe GPU)"),
        112: ("t_document_gpu", "Text REcognition(Tanzhilifang GPU)"),
        114: ("t_table_gpu", "Table REcognition(Tanzhilifang GPU)"),
        116: ("t_receipt_gpu", "Receipt REcognition(Tanzhilifang GPU)"),
        118: ("t_idcard_gpu", "IDCard REcognition(Tanzhilifang GPU)"),
        120: ("t_biz_gpu", "Biz REcognition(Tanzhilifang GPU)"),
        122: ("t_driverlicense_gpu", "Driverlicense REcognition(Tanzhilifang GPU)"),
        124: ("t_vehiclelicense_gpu", "Vehiclelicense REcognition(Tanzhilifang GPU)"),
        126: ("t_bankcard_gpu", "BankCard REcognition(Tanzhilifang GPU)"),
        128: ("t_vehicle_gpu", "Vehicle REcognition(Tanzhilifang GPU)"),
        130: ("t_marriage_gpu", "Marriage REcognition(Tanzhilifang GPU)"),
        132: ("t_hrb_gpu", "Hrb REcognition(Tanzhilifang GPU)"),
    }
# module_info = {
#     0: ("commander", "UiBot Commander"),
#     10: ("usercenter", "usercenter用户中心"),
#     # 11: ("wulai", "吾来对话机器人"),
#     11: ("chatbot", "ChatBot吾来对话机器人"),
#     31: ("mage", "UiBot Mage"),
#     32: ("captcha", "验证码识别"),
#     33: ("geo", "标准地址"),
#     34: ("nlp", "文本分类、信息抽取"),
#     35: ("nlp", "文本分类、信息抽取(GPU)"),
#     36: ("ocr_text_table", "通用文字识别(标准版 CPU)"),
#     37: ("ocr_text_table_gpu", "通用文字识别(标准版 GPU)"),
#     38: ("ocr_seal", "印章识别(标准版 CPU)"),
#     39: ("ocr_seal_gpu", "印章识别(标准版 GPU)"),
#     40: ("ocr", "ocr-go服务-cpu"),
#     41: ("ocr", "ocr-go服务-gpu"),
#     42: ("ocr_idcard_server", "通用卡证识别(标准版)CPU"),
#     43: ("ocr_idcard_server_gpu", "通用卡证识别(标准版)GPU"),
#     51: ("ocr_document_gpu", "通用文字识别(高级版 GPU)"),
#     52: ("ocr_document", "通用文字识别(高级版 CPU)"),
#     53: ("ocr_table_gpu", "通用表格识别(高级版 GPU)"),
#     54: ("ocr_table", "通用表格识别(高级版 CPU)"),
#     55: ("ocr_receipt_gpu", "通用票据识别(高级版 GPU)"),
#     56: ("ocr_receipt", "通用票据识别(高级版 CPU)"),
#     57: ("ocr_idcard_gpu", "通用卡证识别-身份证(高级版 GPU)"),
#     58: ("ocr_idcard", "通用卡证识别-身份证(高级版 CPU)"),
#     59: ("ocr_bankcard_gpu", "通用卡证识别-银行卡(高级版 GPU)"),
#     60: ("ocr_bankcard", "通用卡证识别-银行卡(高级版 CPU)"),
#     61: ("ocr_vehicle_gpu", "通用卡证识别-机动车登记证(高级版 GPU)"),
#     62: ("ocr_vehicle", "通用卡证识别-机动车登记证(高级版 CPU)"),
#     63: ("ocr_vehiclelicense_gpu", "通用卡证识别-机动车行驶证(高级版 GPU)"),
#     64: ("ocr_vehiclelicense", "通用卡证识别-机动车行驶证(高级版 CPU)"),
#     65: ("ocr_biz_gpu", "通用卡证识别-营业执照(高级版 GPU)"),
#     66: ("ocr_biz", "通用卡证识别-营业执照(高级版 CPU)"),
#     81: ("dataservice", "数据服务")
# }
menu_relation = {
    1001: {
        36: 100101,
        37: 100102,
        51: 100103,
        52: 100104
    }
}

middleware_port_relation = {
    "minio": {
        "port": 9000,
        "nginx_proxy_port": 10000
    },
    "harbor": {
        "http_port": 8888,
        "nginx_harbor_proxy_port": 8889
    },
    "redis": {
        "port": 6379,
        "port_sentinel": 26379
    },
    "nginx": {
        "k8s_proxy_port": 6444,
        "entcmd_proxy_port": 8080,
        "commander_tenant_port": 8081,
        "mage_proxy_port": 8082,
        "chatbot_proxy_port": 8083,
        "entuc_proxy_port": 8084,
        "dataservice_proxy_port": 8085,
        "notice_proxy_port": 8089,
        "license_web_proxy_port": 8090,
        "rpa_collaboration_backend_proxy_port": 8091,
        "creativity_proxy_port": 8092,
        "entfs_proxy_port": 8093,
        "entiap_proxy_port": 8094
    },
    "mysql": {
        "port": 3306,
        "proxysql_cluster_port": 6032,
        "proxysql_port": 6033,
        "nginx_proxy_port": 6034
    },
    "elasticsearch": {
        "http_port": 9200,
        "tcp_port": 9300
    },
    "rabbitmq": {
        "port": 5672,
        "manage_port": 15672,
        "empd_port": 4369,
        "erlang_port": 25672
    },
    "etcd": {
        "http_port": 12379,
        "tcp_port": 12380
    },
    "identity": {
        "port": 6060,
        "nginx_proxy_port": 6061
    },
    "monitor": {
        "grafana_port": 3000,
        "prometheus_port": 9090,
        "mysql_exporter_port": 9104,
        "redis_exporter_port": 9121,
        "rabbitmq_exporter_port": 9419,
        "elasticsearch_exporter_port": 9114,
        "node_exporter_port": 9100,
        "k8s_metrics_port": 31388,
        "istio_prometheus_port": 31390
    },
    "siber": {
        "port": 88
    },
    "ocr": {
        "ocr_document_gpu": 30006,
        "ocr_table_gpu": 30007,
        "ocr_receipt_gpu": 30008,
        "ocr_idcard_gpu": 30009,
        "ocr_bankcard_gpu": 30013,
        "ocr_vehicle_gpu": 30010,
        "ocr_vehiclelicense_gpu": 30011,
        "ocr_biz_gpu": 30012,
        "ocr_passport_gpu": 30014
    },
    "chronyd": {
        "port": 123,
        "cmdport": 323
    },
}

def init_port_config():
    conf = YamlConfig(PORT_MAP, data=middleware_port_relation)
    conf.write_file(backup=False)

def find_module_by_key(module: str) -> list:
    l = []
    for id in module_info:
        if module_info[id][0] == module:
            res = {}
            res['id'] = id
            res['module'] = module
            res['description'] = module_info[id][1]
            l.append(res)
    return l

def get_module_description(module_id: int) -> str:
    return module_info[module_id][1]

def get_module_key(module_id: int) -> str:
    return module_info[module_id][0]

def get_module_keys(module_ids: list) -> list:
    return [get_module_key(x) for x in module_ids]

def get_all_ports(middleware="") -> list:
    ''':return list[str]'''
    l = []
    try:
        relation = YamlConfig(PORT_MAP).read_file()
    except Exception:
        relation = middleware_port_relation
    if middleware:
        try:
            for k in relation[middleware]:
                l.append(str(relation[middleware][k]))
        except KeyError:
            pass
    else:
        for mid in relation:
            for k in relation[mid]:
                l.append(str(relation[mid][k]))
    return l

def get_port(middleware: str, key: str) -> int:
    try:
        relation = YamlConfig(PORT_MAP).read_file()
    except Exception:
        relation = middleware_port_relation

    try:
        return relation[middleware][key]
    except KeyError:
        for k in relation[middleware].keys():
            if key in k:
                return relation[middleware][k]
        return 0
