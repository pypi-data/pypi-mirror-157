from __future__ import absolute_import
from __future__ import unicode_literals

import requests
from laipvt.interface.middlewareinterface import MiddlewareInterface
from laipvt.handler.confighandler import CheckResultHandler
from laipvt.handler.middlewarehandler import RabbitmqConfigHandler
from laipvt.sysutil.util import ssh_obj, log, path_join, status_me
from laipvt.sysutil.template import FileTemplate
from laipvt.model.server import ServerModel
from laipvt.helper.errors import Helper


class RabbitmqController(MiddlewareInterface):
    def __init__(self, result: CheckResultHandler, handler: RabbitmqConfigHandler, template: str):
        super(RabbitmqController, self).__init__(result, handler, template)
        self.rabbitmq_cfg = RabbitmqConfigHandler().get_config_with_check_result()
        self.rabbitmq_conf_tmp = path_join("/tmp", "rabbitmq.config")
        self.rabbitmq_conf_template = path_join(self.template, "config.tmpl")
        self.rabbitmq_conf_file = path_join(self.base_dir, "config/rabbitmq.conf")
        if self.rabbitmq_cfg["rabbitmq"]["is_deploy"]:
            self.rabbitmq_cfg["rabbitmq"]["ipaddress"] = self.handler.cfg["ipaddress"]
        self.rabbitmq_service_file_template = path_join(self.template, "rabbitmq_service.tmpl")
        self.rabbitmq_service_file_dest = path_join("/tmp", "rabbitmq_service.yaml")
        self.rabbitmq_service_file_remote = path_join(self.base_dir, "svc", "rabbitmq_service.yaml")

    def _generic_config(self):
        if len(self.master_server) == 1:
            self.rabbitmq_cfg["is_standalone"] = True

        elif len(self.master_server) == 3:
            self.rabbitmq_cfg["is_standalone"] = False
        else:
            log.info(Helper().CLUSTER_REQUIRES_THREE)
            exit(2)

        for num_id in range(len(self.master_server)):
            self.rabbitmq_cfg["rabbitmq"]["NODENAME"] = "rabbit@saas-rabbitmq-0%s" % (num_id + 1)
            self.rabbitmq_cfg["rabbitmq"]["HOSTNAME"] = "saas-rabbitmq-0%s" % (num_id + 1)
            FileTemplate(self.rabbitmq_cfg, self.rabbitmq_conf_template, self.rabbitmq_conf_tmp).fill()
            self.generate_docker_compose_file(self.rabbitmq_cfg)
            self._send_docker_compose_file(self.master_server[num_id])
            self.send_config_file(self.master_server[num_id], self.rabbitmq_conf_tmp, self.rabbitmq_conf_file)


    def _send_docker_compose_file(self, host):
        log.info(Helper().SEND_FILE.format(self.docker_compose_file_tmp, host.ipaddress, self.docker_compose_file))
        ssh_cli = ssh_obj(ip=host.ipaddress, user=host.username, password=host.password, port=host.port)
        try:
            ssh_cli.put(self.docker_compose_file_tmp, self.docker_compose_file)
        except Exception as e:
            log.error(e)
            exit(2)
        finally:
            ssh_cli.close()

    def init_rabbitmq_cluster(self):
        flag = False
        for server in self.master_server[1:]:
            ssh_cli = ssh_obj(ip=server.ipaddress, user=server.username, password=server.password, port=server.port)
            results = ssh_cli.run_cmd("docker exec rabbitmq rabbitmqctl stop_app")
            log.info("stop_app: {} {}".format(results["stdout"], results["stderr"]))
            results = ssh_cli.run_cmd("docker exec rabbitmq rabbitmqctl reset")
            log.info("reset: {} {}".format(results["stdout"], results["stderr"]))
            results = ssh_cli.run_cmd("docker exec rabbitmq rabbitmqctl join_cluster rabbit@saas-rabbitmq-01")
            log.info("join_cluster: {} {}".format(results["stdout"], results["stderr"]))
            results = ssh_cli.run_cmd("docker exec rabbitmq rabbitmqctl start_app")
            log.info("start_app: {} {}".format(results["stdout"], results["stderr"]))

            if flag:
                set_policy_cmd = """docker exec rabbitmq rabbitmqctl set_policy mirror_queue "^" '{"ha-mode":"all", "ha-sync-mode":"automatic"}' """
                results = ssh_cli.run_cmd(set_policy_cmd)
                if results["code"] != 0:
                    log.error("{} {}".format(results["stdout"], results["stderr"]))
                    exit(2)
            flag = True
            ssh_cli.close()

    def _check(self):
        super().wait_for_service_start()
        for i in range(len(self.master_server)):
            try:
                requests.get(
                    "http://{IP}:{PORT}".format(
                        IP=self.master_server[i].ipaddress, PORT=self.rabbitmq_cfg["rabbitmq"]["manage_port"]
                    )
                )
                log.info(Helper().CHECK_MIDDLEWARE_SERVICE_PORT_SUCCEED.format(self.master_server[i].ipaddress,
                                                                               self.rabbitmq_cfg["rabbitmq"]["manage_port"]))
            except Exception as e:
                log.info(Helper().CHECK_MIDDLEWARE_SERVICE_PORT_FAILED.format(self.master_server[i].ipaddress,
                                                                              self.rabbitmq_cfg["rabbitmq"]["manage_port"]))
                log.error(e)
                exit(2)
        if not self.rabbitmq_cfg["is_standalone"]:
            self.init_rabbitmq_cluster()

    def create_rabbitmq_service_kubernetes(self):
        server = ServerModel(self.harbor_server)
        FileTemplate(self.rabbitmq_cfg, self.rabbitmq_service_file_template, self.rabbitmq_service_file_dest).fill()
        server.send_file(self.rabbitmq_service_file_dest, self.rabbitmq_service_file_remote)

        cmd = "kubectl apply -f {}".format(self.rabbitmq_service_file_remote)
        ssh_cli = ssh_obj(ip=self.harbor_server[0].ipaddress, user=self.harbor_server[0].username,
                          password=self.harbor_server[0].password, port=self.harbor_server[0].port)
        results = ssh_cli.run_cmd(cmd)
        if results["code"] != 0:
            log.error("{} {}".format(results["stdout"], results["stderr"]))
            exit(2)

    @status_me("middleware")
    def deploy_rabbitmq(self):
        if self.check_is_deploy(self.rabbitmq_cfg):
            self._generic_config()
            self.start()
            self._check()
        self.create_rabbitmq_service_kubernetes()

    def deploy(self):
        self.deploy_rabbitmq()
