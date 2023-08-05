from __future__ import absolute_import
from __future__ import unicode_literals

import requests
from laipvt.interface.middlewareinterface import MiddlewareInterface
from laipvt.handler.confighandler import CheckResultHandler
from laipvt.handler.middlewarehandler import EtcdConfigHandler
from laipvt.sysutil.util import ssh_obj, log, status_me
from laipvt.helper.errors import Helper


class EtcdController(MiddlewareInterface):
	def __init__(self, result: CheckResultHandler, handler: EtcdConfigHandler, template: str):
		super(EtcdController, self).__init__(result, handler, template)
		self.etcd_cfg = EtcdConfigHandler().get_config_with_check_result()
		self.etcd_cfg["etcd"]["ipaddress"] = self.handler.cfg["ipaddress"]

	def _generic_config(self):
		if len(self.master_server) == 1:
			self.etcd_cfg["is_standalone"] = True
		elif len(self.master_server) == 3:
			self.etcd_cfg["is_standalone"] = False
		else:
			log.info(Helper().CLUSTER_REQUIRES_THREE)
			exit(2)
		for num_id in range(len(self.master_server)):
			self.etcd_cfg["etcd"]["etcd_num"] = "etcd%s" % (num_id + 1)
			self.etcd_cfg["etcd"]["ip"] = self.master_server[num_id].ipaddress
			self.generate_docker_compose_file(self.etcd_cfg)
			self._send_docker_compose_file(self.master_server[num_id])


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

	def _check(self):
		super().wait_for_service_start()
		for i in range(len(self.master_server)):
			try:
				requests.get(
					"http://{IP}:{PORT}/version".format(
						IP=self.master_server[i].ipaddress, PORT=self.etcd_cfg["etcd"]["http_port"]
					)
				)
				log.info(Helper().CHECK_MIDDLEWARE_SERVICE_PORT_SUCCEED.format(self.master_server[i].ipaddress,
																			   self.etcd_cfg["etcd"]["http_port"]))
			except Exception as e:
				log.info(Helper().CHECK_MIDDLEWARE_SERVICE_PORT_FAILED.format(self.master_server[i].ipaddress,
																			   self.etcd_cfg["etcd"]["http_port"]))
				log.error(e)
				exit(2)

	@status_me("middleware")
	def deploy_etcd(self):
		self._generic_config()
		self.start()
		self._check()

	def deploy(self):
		self.deploy_etcd()
