from __future__ import absolute_import
from __future__ import unicode_literals

from redis.sentinel import Sentinel
from laipvt.interface.middlewareinterface import MiddlewareInterface
from laipvt.handler.middlewarehandler import RedisConfigHandler
from laipvt.handler.confighandler import CheckResultHandler
from laipvt.sysutil.template import FileTemplate
from laipvt.sysutil.util import path_join, log, status_me
from laipvt.helper.errors import Helper


class RedisController(MiddlewareInterface):
    def __init__(self, result: CheckResultHandler, handler: RedisConfigHandler, template: str):
        super(RedisController, self).__init__(result, handler, template)
        self.redis_conf_tmp = path_join("/tmp", "redis.conf")
        self.redis_conf_template = path_join(self.template, "config.tmpl")
        self.redis_conf_file = path_join(self.base_dir, "conf", "redis.conf")
        self.redis_stand_tmp = path_join("/tmp", "redis-sentinel.conf")
        self.redis_stand_template = path_join(self.template, "config-sentinel.tmpl")
        self.redis_stand_file = path_join(self.base_dir, "conf", "redis-sentinel.conf")
        self.redis_cfg = RedisConfigHandler().get_config_with_check_result()
        self.redis_cfg["redis"]["ipaddress"] =  self.handler.cfg["ipaddress"]

    def _generic_config(self):
        for num_id in range(len(self.master_server)):
            if num_id == 0:
                self.redis_cfg["redis"]["master_ip"] = self.master_server[num_id].ipaddress
                self.redis_cfg["redis"]["isslave"] = False
            else:
                self.redis_cfg["redis"]["isslave"] = True
            self.redis_cfg["sentinel_master_ip"] = self.master_server[num_id].ipaddress
            FileTemplate(self.redis_cfg, self.redis_conf_template, self.redis_conf_tmp).fill()
            FileTemplate(self.redis_cfg, self.redis_stand_template, self.redis_stand_tmp).fill()
            self.send_config_file(self.master_server[num_id], self.redis_conf_tmp, self.redis_conf_file)
            self.send_config_file(self.master_server[num_id], self.redis_stand_tmp, self.redis_stand_file)
            self.generate_docker_compose_file(self.redis_cfg)

    def _check(self) -> bool:
        super().wait_for_service_start()
        pool = []
        for host in self.master_server:
            redis_endpoint = (host.ipaddress, self.redis_cfg["redis"]["port_sentinel"])
            pool.append(redis_endpoint)
        try:
            key = "__XX_LAIYE_TEST"
            value = "XXXVALUEXXX"
            cli = Sentinel(pool)
            master = cli.master_for(
                self.redis_cfg["redis"]["master_name"],
                password=self.redis_cfg["redis"]["password"],
                db=15
                )
            if self.handler.cfg["deploy_type"] == "single" and master:
                log.info(Helper().CHECK_REDIS_SERVICE_SUCCEED)
                return True
            r = master.set(key, value)
            if r:
                slave = cli.slave_for(
                    self.redis_cfg["redis"]["master_name"],
                    password=self.redis_cfg["redis"]["password"],
                    db=15
                )
                if slave.get(key).decode() == value:
                    log.info(Helper().CHECK_REDIS_SERVICE_SUCCEED)
                    return True
        except Exception as e:
            log.error(Helper().CHECK_REDIS_SERVICE_FAILED.format(e))

    @status_me("middleware")
    def deploy_redis(self):
        if self.check_is_deploy(self.redis_cfg):
            self._generic_config()
            self.send_docker_compose_file()
            self.start()
            self._check()

    def deploy(self):
        self.deploy_redis()
