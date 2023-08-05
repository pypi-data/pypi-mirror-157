from prettytable import PrettyTable
from laipvt.sysutil.gvalue import CHECK_FILE
from laipvt.handler.confighandler import CheckResultHandler
from laipvt.handler.middlewarehandler import MiddlewareConfigHandler
from laipvt.helper.errors import Helper
from laipvt.sysutil.util import log

def print_project_info():
    try:
        log.info(Helper().PRINT_PROJECT_INFO)
        tb = PrettyTable()
        tb.field_names = ["ProJect", "Desc", "URL"]
        # tb.add_row(["Adelaide", 1295, 1158259, 600.5])

        # 获取前置检查结果
        check_result_file = CHECK_FILE
        check_result = CheckResultHandler(check_result_file)
        # 获取中间件信息
        middleware_cfg = MiddlewareConfigHandler("nginx").get_all_config_with_check_result()
        project_port_map = {
            "license": {
                "desc": "License授权服务(License Service)", "port_name": ["license_web_proxy_port"]
            },
            "entuc": {
                "desc": "用户中心 (Enterprise User Center)", "port_name": ["entuc_proxy_port"]
            },
            "chatbot": {
                "desc": "ChatBot吾来对话机器人 (ChatBot)", "port_name": ["chatbot_proxy_port"]
            },
            "entcmd": {
                "desc": "机器人指挥官 (Enterprise Commander)", "port_name": ["entcmd_proxy_port"]
            },
            "mage": {
                "desc": "UiBot Mage (UiBot Mage)", "port_name": ["mage_proxy_port"]
            },
            "rpa-collaboration": {
                "desc": "人机协同中心 (RPA Collaboration)", "port_name": ["rpa_collaboration_backend_proxy_port"]
            },
            "dataservice": {
                "desc": "数据服务 (Data Service)", "port_name": ["dataservice_proxy_port"]
            },
        }
        for project in check_result.deploy_projects.get():
            if project in project_port_map:
                for port_name in project_port_map[project]["port_name"]:
                    url = "http://{}:{}/".format(middleware_cfg["nginx"]["lb"], middleware_cfg["nginx"][port_name])
                    desc = project_port_map[project]["desc"]
                    tb.add_row([project, desc, url])
        print(tb)

    except Exception as e:

        exit(2)


