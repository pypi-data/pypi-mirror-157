import os
import time
import getpass
from laipvt.sysutil.gvalue import CHECK_FILE, LOG_TO_TTY
from laipvt.sysutil.ssh import SSHConnect
from laipvt.sysutil.log import Logger
from laipvt.handler.confighandler import CheckResultHandler
from laipvt.sysutil.util import path_join, log, get_yaml_config


class RecoverMysql:
	""" 恢复mysql """

	def __init__(self):
		self.check_result_file = CHECK_FILE
		self.check_result = CheckResultHandler(self.check_result_file)
		self.deploy_dir = self.check_result.deploy_dir
		self.mysql_dir = path_join(self.deploy_dir, "mysql")
		self.container_name = get_yaml_config(path_join(self.mysql_dir, "docker-compose.yml"))["services"]["mysqlmgr"][
			"container_name"]
		self.log = Logger(
			tty=os.environ.get("LOG_TO_TTY", LOG_TO_TTY)
		).get()
		self.master_ip = input("请输入当前Mgr集群主节点地址: ")
		self.slive_ip = input("请输入当前Mgr集群要恢复的节点地址: ")
		if self.master_ip == self.slive_ip:
			log.error("主节点与恢复节点地址不应一致")
			exit(2)
		self.mysql_pass = input("请输入mysql密码: ")
		self.mysql_port = input("请输入mysql端口: ")
		self.service_username = input("请输入登陆入服务器用户: ")
		self.service_password = getpass.getpass("请输入登陆入服务器密码(已隐藏): ********")
		self.service_ssh = input("请输入SSH端口号: ")
		self.slive_client = f"mysql -uroot -p{self.mysql_pass}  -h{self.slive_ip} -P{self.mysql_port}"
		self.master_client = f"mysql -uroot -p{self.mysql_pass}  -h{self.master_ip} -P{self.mysql_port}"
		self.find_master = "'select MEMBER_HOST, MEMBER_PORT,MEMBER_STATE from " \
		                   "performance_schema.replication_group_members m inner " \
		                   "join performance_schema.global_status g on m.MEMBER_ID=g.VARIABLE_VALUE  and VARIABLE_NAME = " \
		                   "\"group_replication_primary_member\";'"
		self.start_mgr = f"'CHANGE MASTER TO MASTER_USER=\"rpl_user\", MASTER_PASSWORD=\"{self.mysql_pass}\" FOR CHANNEL " \
		                 "\"group_replication_recovery\"; set global group_replication_allow_local_disjoint_gtids_join=on;" \
		                 "start group_replication;'"
		self.count_mgr = "'select count(*) from performance_schema.replication_group_members where MEMBER_STATE = " \
		                 "\"ONLINE\";' "

		self.reset_slave = "'reset master;set sql_log_bin=0;flush privileges;set sql_log_bin=1;'"

		self.count_proxsql = "mysql -uadmin -padmin --prompt='proxysql> ' -P6032 -h127.0.0.1 -e 'select * from " \
		                     "runtime_mysql_servers';"

	def check_disk(self):
		several = self.master_ip, self.slive_ip
		for ip in several:
			cmd1 = f"du -sm {self.mysql_dir} |awk '{{print $1}}'"
			data_size = self.sshclient(cmd1, ip)["stdout"].replace("\n", "").replace("\r", "")
			cmd2 = f"df -m {self.mysql_dir}|tail -n 1 |awk '{{print $4}}'"
			disk_size = self.sshclient(cmd2, ip)["stdout"].replace("\n", "").replace("\r", "")
			if int(float(data_size)) * 3 < int(float(disk_size)):
				log.info(f"{ip}节点目录{self.mysql_dir}共占用{data_size}MB，数据盘共剩余{disk_size}MB")
			else:
				log.info(f"{ip}节点目录{self.mysql_dir}共占用{data_size}MB, 数据盘共剩余{disk_size}MB,磁盘空间不够，请清理磁盘空间...")
				exit(2)

	def rename_dir(self, dir_path):
		cmd = f"mv -f {dir_path} {path_join(self.mysql_dir, 'mysql_data_bak')}"
		return cmd

	def backup_data(self):
		cmd = f"docker exec -i {self.container_name} mysqldump  --set-gtid-purged=ON --single-transaction   --all-databases " \
		      f"-u{'root'} -p{self.mysql_pass} -h {self.master_ip} -P{self.mysql_port} > {self.mysql_dir}/recover.sql"
		cmd2 = f"docker exec -i {self.container_name} mysqldump --databases --routines  sys  --set-gtid-purged=off -u{'root'}" \
		       f" -p{self.mysql_pass} -h {self.master_ip} -P{self.mysql_port} > {self.mysql_dir}/recover_function.sql"
		res = self.sshclient(cmd, self.master_ip)
		res1 = self.sshclient(cmd2, self.master_ip)
		if res["code"] == 0 and res1["code"] == 0:
			log.info("数据备份成功...")
		else:
			log.error(f"备份命令：{cmd}")
			log.error("数据备份失败，请检查")
			log.error(res["stdout"])
			exit(2)

	def ask_master(self):
		cmd = f"{self.master_client} -e {self.find_master}"
		res = self.sshclient(cmd, self.master_ip)
		log.info(res)
		for res1 in res["stdout"].split('\n'):
			if any(digital.isdigit() for digital in res1):
			# if '.' in res1:
				res1 = res1.split()
				log.info(res1)
				if res1[0] == self.master_ip and res1[1] == self.mysql_port and res1[2] == "ONLINE":
					log.info(f"Master主节点正常: {res1}...")
				else:
					log.error("Master节点异常或master主节点地址填写错误")
					exit(2)
			else:
				pass

	def rename_mysql_dir(self):
		# try:
		# self.sshclient(shutil.move(path_join(self.mysql_dir, "data"), path_join(self.mysql_dir, "data_bak")), self.slive_ip)
		local_path = path_join(self.mysql_dir, "data")
		# srcpath = path_join(self.mysql_dir, "data_bak")
		# cmd = "mv {local_path} {srcpath}".format(local_path=local_path, srcpath=srcpath)
		# log.info(cmd)
		res = self.sshclient(self.rename_dir(local_path), self.slive_ip)
		if res["code"] != 0:
			log.error(res["stdout"])
			log.error("数据目录移动失败，请检查...")
			exit(2)

	# except Exception as e:
	# 	log.error(e)
	# 	exit(2)

	def remove_mysql(self):
		cmd = f"docker rm -f {self.container_name}"
		res = self.sshclient(cmd, self.slive_ip)
		if res["code"] == 0:
			log.info(f"{self.slive_ip}节点{self.container_name}容器已删除...")
		else:
			log.error(res["stdout"])
			exit(2)

	def start_mysql(self):
		mysql_compose = f"{self.deploy_dir}/{'mysql'}/{'docker-compose.yml'}"
		cmd = f"docker-compose -f {mysql_compose} up -d "
		self.sshclient(cmd, self.slive_ip)
		log.info(f"{self.slive_ip}节点mysql容器启动成功，等待60s...")
		time.sleep(60)

	def pre_mysql(self):
		# cmd = f"{self.slive_client} -e 'reset master;set sql_log_bin=0;flush privileges;set sql_log_bin=1;'"
		cmd = f"{self.slive_client} -e {self.reset_slave}"
		self.sshclient(cmd, self.slive_ip)

	def import_data(self):
		cmd = f"{self.slive_client}  < {self.mysql_dir}/recover.sql"
		res = self.sshclient(cmd, self.master_ip)
		if res["code"] == 0:
			log.info("备份数据导入成功...")
		else:
			log.error("备份数据导入失败，请检查")
			log.error(res["stdout"])
			exit(2)

	def import_funtion(self):
		cmd = f"{self.slive_client}   < {self.mysql_dir}/recover_function.sql"
		res = self.sshclient(cmd, self.master_ip)
		if res["code"] != 0:
			log.error("函数导入失败，请检查")
			log.error(res["stdout"])
			exit(2)

	def start_slavemgr(self):
		cmd = f"{self.slive_client} -e {self.start_mgr}"
		res = self.sshclient(cmd, self.slive_ip)
		if res["code"] == 0:
			log.info(f"{self.slive_ip} 节点Mgr启动成功...")
		else:
			log.error(f"{self.slive_ip} 节点Mgr启动失败,请检查")
			log.error(res["stdout"])
			exit(2)

	def check_mgrmembers(self):
		cmd = f"{self.slive_client} -e {self.count_mgr}"
		res = self.sshclient(cmd, self.slive_ip)
		log.info(res["stdout"].split())
		if res["stdout"].split()[-1] == "3":
			log.info("Mysql mgr集群正常,ONLINE节点数为3...")
			log.info(f"请登陆mysql中手动检查确认ONLINE数为3,命令: {cmd}")
			log.info(f"请登陆proxysql中手动确认集群正常,命令: {self.count_proxsql}")
			log.info(
				f"\033[1;35m 如确认集群正常确认无问题后！！！，请将节点 {self.slive_ip}  {path_join(self.mysql_dir, 'data_bak')} "
				f"备份文件清理，避免占用磁盘空间\033[0m!")
		else:
			log.error(f"Mysql mgr集群异常，请检查{res['stderr']}")
			exit(2)

	def flush(self):
		cmd = f"{self.slive_client} -e 'flush privileges;'"
		self.sshclient(cmd, self.slive_ip)

	def sshclient(self, cmd, ip):
		ssh_cli = SSHConnect(hostip=ip, username=self.service_username, password=self.service_password,
		                     port=self.service_ssh)
		self.log.info(f"{ip} 执行 {cmd} 命令")
		res = ssh_cli.run_cmd(cmd)
		ssh_cli.close()
		return res


if __name__ == '__main__':
	mysql = RecoverMysql()
	mysql.check_disk()
	mysql.ask_master()
	mysql.backup_data()
	mysql.rename_mysql_dir()
	mysql.remove_mysql()
	mysql.start_mysql()
	mysql.pre_mysql()
	mysql.import_data()
	mysql.import_funtion()
	mysql.start_slavemgr()
	mysql.flush()
	mysql.check_mgrmembers()
