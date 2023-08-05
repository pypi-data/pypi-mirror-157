from __future__ import absolute_import
from __future__ import unicode_literals

import json
import requests
from requests.adapters import HTTPAdapter
from requests.auth import HTTPBasicAuth
from laipvt.helper.errors import Helper
from laipvt.interface.middlewareinterface import MiddlewareInterface
from laipvt.handler.confighandler import CheckResultHandler
from laipvt.handler.middlewarehandler import HarborConfigHandler
from laipvt.sysutil.util import path_join, ssh_obj, log, status_me, post, get, put
from laipvt.sysutil.template import FileTemplate
from laipvt.model.cmd import ComposeModel
from laipvt.sysutil.command import BASH_RUN, TARGZ_DECOMPRESSION, CHMOD_USER_GROUP, ENABLE_HARBOR_SERVICE


class HarborController(MiddlewareInterface):
    def __init__(self, result: CheckResultHandler, handler: HarborConfigHandler, template: str):
        super(HarborController, self).__init__(result, handler, template)

        self.harbor_conf_tmp = path_join("/tmp", "harbor.yml")
        self.harbor_conf_template = path_join(self.template, "config.tmpl")
        self.harbor_conf_file = path_join(self.base_dir, "harbor.yml")
        self.harbor_service_template = path_join(self.template, "harbor.service.tmpl")
        self.harbor_service_tmp = path_join("/tmp", "harbor.service")
        self.harbor_service_file = "/usr/lib/systemd/system/harbor.service"
        self.habor_data = path_join(self.template, "data")
        self._docker_compose_file = path_join(self.base_dir, "docker-compose.yaml")
        self.harbor_cfg = HarborConfigHandler().get_config_with_check_result()
        self.harbor_cfg["harbor"]["log_location"] = path_join(self.base_dir, "var/log/harbor")
        self.harbor_cfg["harbor"]["data_volume"] = path_join(self.base_dir, "data")
        self.harbor_cfg["harbor"]["deploy_path"] = self.base_dir
        self.harbor_cfg["harbor"]["ipaddress"] = [ip.ipaddress for ip in self.harbor_server]
        self.harbor_nginx_tmp = path_join("/tmp", "nginx-harbor.conf")
        self.harbor_nginx_template = path_join(self.template, "nginx-harbor.tmpl")
        self.harbor_nginx_file = path_join(self.deploy_dir, "nginx/http/nginx-harbor.conf")
        self.master_harbor = self.harbor_server[0]

    def _generic_config(self):
        """
        如果是多机Harbor 只将data目录拷贝到第一台harbor上，传输第二台的时候将data.tar.gz过滤掉，使用内部同步机制，节约部署时间
        :return:
        """
        for num_id, server in enumerate(self.harbor_server):
            self.harbor_cfg["harbor"]["localhost_ip"] = server.ipaddress
            FileTemplate(self.harbor_cfg, self.harbor_conf_template, self.harbor_conf_tmp).fill()
            FileTemplate(self.harbor_cfg, self.harbor_service_template, self.harbor_service_tmp).fill()
            if num_id == 0:
                self.send_config_file(server=server, src=self.template, dest=self.base_dir)
            else:
                self.send_config_file(server=server, src=self.template, dest=self.base_dir, ignore='data.tar.gz')
            self.send_config_file(server=server, src=self.harbor_conf_tmp, dest=self.harbor_conf_file)
            self.send_config_file(server=server, src=self.harbor_service_tmp, dest=self.harbor_service_file)

    def ssh_cli(self, cmd):
        for server in self.harbor_server:
            ssh_cli = ssh_obj(ip=server.ipaddress, user=server.username, password=server.password, port=server.port)
            res = ssh_cli.run_cmd(cmd)
            ssh_cli.close()
        return res

    def _install_harbor(self):
        cmd = BASH_RUN.format(path_join(self.base_dir, "install.sh"))
        res = self.ssh_cli(cmd)
        if res["code"] != 0:
            log.error("{} {}".format(res["stdout"], res["stderr"]))
            exit(2)

    def _unpack_data(self):
        """
        只解压第一台Harbor的数据目录
        :return:
        """
        ssh_cli = ssh_obj(
            ip=self.master_harbor.ipaddress,
            user=self.master_harbor.username,
            password=self.master_harbor.password,
            port=self.master_harbor.port
        )
        cmd = [
            TARGZ_DECOMPRESSION.format(path_join(self.base_dir, "data.tar.gz"), self.base_dir),
            CHMOD_USER_GROUP.format(
                "999", "999",
                path_join(self.base_dir, "data", "database"),
                path_join(self.base_dir, "data", "redis")),
            CHMOD_USER_GROUP.format(
                "10000", "10000",
                path_join(self.base_dir, "data", "secret"),
                path_join(self.base_dir, "data", "registry"))
        ]
        res_list = ssh_cli.run_cmdlist(cmd)
        for res in res_list:
            if res["code"] != 0:
                log.error(Helper().DECOMPRESS_HARBOR_DATA_ERROR.format(res["stdout"], res["stderr"]))
                exit(2)

    def _start(self):
        compose_cmd = ComposeModel(self.docker_compose_file)
        for server in self.harbor_server:
            log.info(Helper().START_MIDDLEWARE_SERVICE.format(server.ipaddress, self.middleware_name))
            ssh_cli = ssh_obj(ip=server.ipaddress, user=server.username, password=server.password, port=server.port)
            try:
                res = ssh_cli.run_cmd(compose_cmd.up())
                if res["code"] != 0:
                    log.error(Helper().START_MIDDLEWARE_SERVICE_ERROR.format(res["stderr"], res["stdout"]))
                    exit(2)
                res = ssh_cli.run_cmd(ENABLE_HARBOR_SERVICE)
                if res["code"] != 0:
                    log.error(Helper().START_MIDDLEWARE_SERVICE_ERROR.format(res["stderr"], res["stdout"]))
                    exit(2)
            except Exception as e:
                log.error(e)
                exit(2)
            finally:
                ssh_cli.close()

    def _check(self):
        super().wait_for_service_start()
        s = requests.Session()
        s.mount('http://', HTTPAdapter(max_retries=3))
        s.mount('https://', HTTPAdapter(max_retries=3))
        try:
            for server in self.harbor_server:
                url = "http://{IP}:{PORT}/api/v2.0/health".format(
                    IP=server.ipaddress, PORT=self.harbor_cfg["harbor"]["http_port"]
                )
                log.info(Helper().CHECK_MIDDLEWARE_SERVICE.format(self.middleware_name,
                                                                  server.ipaddress,
                                                                  self.harbor_cfg["harbor"]["http_port"]))
                result = s.get(url, timeout=5).json()
                if result["status"] == "healthy":
                    log.info(Helper().CHECK_MIDDLEWARE_SERVICE_PORT_SUCCEED.format(server.ipaddress,
                                                                                   self.harbor_cfg["harbor"]["http_port"]))
                else:
                    log.error(Helper().CHECK_MIDDLEWARE_SERVICE_PORT_FAILED.format(server.ipaddress,
                                                                                   self.harbor_cfg["harbor"]["http_port"]))
                    log.error(result)
                    exit(2)
        except Exception as e:
            log.error(e)
            exit(2)

    def _change_password(self):
        """
        只修改第一台Harbor的密码即可，第二台使用Habor配置文件中的密码，所以无需修改
        :return:
        """
        log.info(Helper().CHANGE_HARBOR_PASSWORD)
        try:
            url = "http://{IP}:{PORT}/api/v2.0/users/1/password".format(
                IP=self.master_harbor.ipaddress, PORT=self.harbor_cfg["harbor"]["http_port"])
            headers = {"Content-Type": "application/json"}
            data_dit = {"old_password": "Harbor12345", "new_password": "{}".format(self.harbor_cfg["harbor"]["password"])}
            result = requests.put(url=url, json=data_dit, headers=headers, auth=HTTPBasicAuth('admin', 'Harbor12345'))
            if result:
                log.info(Helper().CHANGE_HARBOR_PASSWORD_SUCCEED)
            else:
                log.error(Helper().CHANGE_HARBOR_PASSWORD_FAILED)
                log.error(result)
                exit(2)
        except Exception as e:
            log.error(Helper().CHECK_MIDDLEWARE_SERVICE_PORT_FAILED.format(self.master_harbor.ipaddress,
                                                                           self.harbor_cfg["harbor"]["http_port"]))
            log.error(e)
            exit(2)

    def registries(self):
        """
        两台Harbor互相配置仓库管理
        :return:
        """
        for num_id, ip in enumerate(self.harbor_server):
            if num_id == 0:
                harbor_ipaddress = self.harbor_server[1].ipaddress
                # url = "http://{}:{}/api/v2.0/registries".format(self.harbor_server[1].ipaddress, self.harbor_cfg["harbor"]["harbor_http_port"])
            else:
                harbor_ipaddress = self.harbor_server[0].ipaddress
                # url = "http://{}:{}/api/v2.0/registries".format(self.harbor_server[0].ipaddress, self.harbor_cfg["harbor"]["harbor_http_port"])
            url = "http://{}:{}/api/v2.0/registries".format(harbor_ipaddress,
                                                            self.harbor_cfg["harbor"]["harbor_http_port"])
            data = {
                "credential": {
                    "access_key": "admin",
                    "access_secret": "{}".format(self.harbor_cfg["harbor"]["password"]),
                    "type": "basic"
                },
                "name": "Harbor_slave",
                "url": "http://{}:{}".format(self.harbor_server[num_id].ipaddress,
                                             self.harbor_cfg["harbor"]["harbor_http_port"]),
                "insecure": False,
                "id": 100,
                "type": "harbor"
            }
            res = self.interface_res(url, data)
            if res.status_code != 201:
                log.error(Helper().HARBOR_REG_CONFIG_FAILED.format(harbor_ipaddress, res.status_code))
                exit(2)

    def interface_res(self, url, data):
        try:
            res = post(url, data=json.dumps(data), timeout=5,
                       auth=('admin', '{}'.format(self.harbor_cfg["harbor"]["password"])))
            return res
        except Exception as e:
            log.error(e)
            exit(2)

    def policies(self, model, policy_id=''):
        """
        配置Harbor复制管理，首次调用需要设置手动同步模式，后面手动调用手动出发同步接口，手动同步完毕后，在将模式改为触发同步
        :return:
        """
        for num_id, server in enumerate(self.harbor_server):
            if num_id == 0:
                harbor_ipaddress = self.harbor_server[1].ipaddress
            else:
                harbor_ipaddress = self.harbor_server[0].ipaddress
            url = "http://{}:{}/api/v2.0/replication/policies{}".format(harbor_ipaddress,
                                                                        self.harbor_cfg["harbor"]["harbor_http_port"], policy_id)
            data = {
                "name": "replication_to_salve1",
                "dest_registry": {
                    "id": 100,
                    "name": "Harbor_slave",
                    "type": "harbor",
                    "url": "http://{}:{}".format(self.harbor_server[num_id].ipaddress,
                                                 self.harbor_cfg["harbor"]["harbor_http_port"]),
                    "credential": {
                        "type": "basic",
                        "access_key": "admin",
                        "access_secret": "{}".format(self.harbor_cfg["harbor"]["password"])
                    },
                    "insecure": False,
                },
                "dest_namespace": "",
                        "trigger": {
                            "type": model,
                            "trigger_settings": {
                                "cron": ""
                            }
                        },
                        "id": 100,
                        "enabled": True,
                        "deletion": False,
                        "override": True,
                    }
            if policy_id == '':
                res = post(url, json.dumps(data), timeout=5,
                           auth=('admin', '{}'.format(self.harbor_cfg["harbor"]["password"])))
            else:
                res = put(url, json.dumps(data), timeout=5,
                          auth=('admin', '{}'.format(self.harbor_cfg["harbor"]["password"])))
            if res.status_code == 200 or res.status_code == 201:
                log.info(Helper().HARBOR_REPLICATION_SUCCEED.format(res.status_code))
            else:
                log.error(Helper().HARBOR_REPLICATION_FAILED.format(res.status_code))
                exit(2)

    def get_policies_id(self):
        """
        获取复制管理的唯一ID
        :return:
        """
        url = "http://{}:{}/api/v2.0/replication/policies?name=replication_to_salve1"\
            .format(self.master_harbor.ipaddress,
                    self.harbor_cfg["harbor"]["harbor_http_port"])
        try:
            res = get(url, timeout=5,
                      auth=('admin', '{}'.format(self.harbor_cfg["harbor"]["password"]))).json()[0]["id"]
            return res
        except Exception as e:
            log.error(e)

    def manual_sync(self):
        """
        触发手动同步
        :return:
        """
        data = {
            "policy_id": self.get_policies_id()
        }
        url = "http://{}:{}/api/v2.0/replication/executions"\
            .format(self.master_harbor.ipaddress,
                    self.harbor_cfg["harbor"]["harbor_http_port"])
        res = self.interface_res(url, data)
        if res.status_code != 201:
            log.error(Helper().HARBOR_SYNC_FAILED.format(res.status_code))
            exit(2)
        else:
            log.info(Helper().HARBOR_SYNC_SUCCEED.format(res.status_code))

    def _proxy_on_nginx(self):
        FileTemplate(self.harbor_cfg, self.harbor_nginx_template, self.harbor_nginx_tmp).fill()
        self.update_nginx_config()
        # self.generate_docker_compose_file(self.harbor_cfg)

    @status_me("basesystem")
    def install_harbor(self):
        self._generic_config()
        self._install_harbor()
        self._unpack_data()
        self._start()
        self._check()
        self._change_password()
        self._proxy_on_nginx()
        if len(self.harbor_server) > 1:
            self.registries()
            self.policies("manual")
            self.manual_sync()
            self.policies("event_based", '/100')


