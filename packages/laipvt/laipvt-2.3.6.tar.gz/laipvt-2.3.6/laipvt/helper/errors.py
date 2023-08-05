from __future__ import absolute_import
from __future__ import unicode_literals

import os
from laipvt.sysutil.gvalue import DEPLOY_LANGUAGE

class Error():
    def __init__(self):
        lang = os.environ.get("DEPLOY_LANGUAGE", DEPLOY_LANGUAGE)
        map = {
            "en": self.en,
            "cn": self.cn
        }
        try:
            map[lang]()
        except KeyError:
            self.cn()

    def cn(self):
        self.UNIMPLEMENT_ERROR = "未实现的方法: {}"
        self.USER_EXIT = "用户手动退出。程序结束"

    def en(self):
        self.UNIMPLEMENT_ERROR = "un implement function: {}"
        self.USER_EXIT = "user exit. quit process"

class PackageErrors(Error):
    def __init__(self):
        super(PackageErrors, self).__init__()

    def cn(self):
        self.PROJECT_ID_UNMATCH = "授权id与实际申请的项目不匹配"
        self.PROJECT_ID_INCORRECT = "授权id不正确"
        self.PACKAGE_ILLEGAL = "文件不合法，{}不存在"
        self.UNPACK_ERROR = "文件解压失败，错误信息: {}"
        self.PACK_ERROR = "文件打包失败，错误信息: {}"

    def en(self):
        self.PROJECT_ID_UNMATCH = "authorization id is unmatch with this project"
        self.PROJECT_ID_INCORRECT = "incorrect authorization id"
        self.PACKAGE_ILLEGAL = "file type illegal，{} is not exist"
        self.UNPACK_ERROR = "file unpack failed, error msg: {}"
        self.PACK_ERROR = "package file failed, error msg: {}"

class FileTypeErrors(Error):
    def __init__(self):
        super(FileTypeErrors, self).__init__()

    def cn(self):
        self.WRONG_FILE_TYPE = "不支持的文件类型"

    def en(self):
        self.WRONG_FILE_TYPE = "unsupported file type"

class RuntimeErrors(Error):
    def __init__(self):
        super(RuntimeErrors, self).__init__()

    def cn(self):
        self.SEND_FILE_ERROR = "发送文件{}, 到服务器: {} 失败。错误信息: {}"
        self.RUN_CMD_ERROR = "在服务器: {} 执行命令 {} 失败。错误信息: {}"

    def en(self):
        self.SEND_FILE_ERROR = "Failed send {} to server: {}. Error message: {}"
        self.RUN_CMD_ERROR = "Server: {}. Run command {} failed. Error message: {}"


class Helper(Error):
    def __init__(self):
        super(Helper, self).__init__()

    def cn(self):
        self.PRECHECK_FAILED = "未执行前置检查或前置检查失败"
        self.HTTPS_CERTS_ERROR = "使用https部署，选择的是客户提供证书，证书路径不正确"
        self.FILE_NOT_FOUND = "{}文件未找到"
        self.SKIP_STEP = "{}下的{}已经执行过，跳过当前步骤"
        self.RUN_STEP = "即将运行{}下的{}方法"
        self.EXCUTE_COMMAND = "主机: {}, 执行命令: {}"
        self.COMMAND_ERROR = "命令存在错误：{}"
        self.LOCAL_FILL = "渲染{}文件到{}"
        self.FILL_ERROR = "渲染{}文件失败，程序退出: {}"
        self.SEND_FILE = "分发文件{}到{}:{}"
        self.PULL_FILE = "拉取{}:{}到{}"
        self.CHECK_STATUS = "检查{}部署状态"
        self.KUBE_MASTER_INIT = "初始化master主节点"
        self.JOIN_MASTER_NODE = "加入master节点: {}"
        self.KUBE_JOIN_COMMAND_ERROR = "生成Node节点join命令失败: {} {}"
        self.INSTALL_ISTIO = "安装Istio组件"
        self.INSTALL_ISTIO_ERROR = "安装Istio组件错误"
        self.INSTALL_ROOK = "安装rook分布式存储: {}"
        self.CHECK_CEPH_STATUS = "检查rook-ceph集群部署状态，大概需要3-5分钟，请等待..."
        self.RENEN_KUBE_APISERVER_NGINX_CONFIG = "更新kube-apiserver地址到nginx代理"
        self.DECOMPRESS_HARBOR_DATA_ERROR = "Harbor Data数据解压或授权失败:{} {}"
        self.START_MIDDLEWARE_SERVICE = "启动{} {}服务"
        self.RESTART_MIDDLEWARE_SERVICE = "重启{} {}服务"
        self.RESET_MIDDLEWARE_SERVICE = "重置{} {}服务"
        self.START_MIDDLEWARE_SERVICE_ERROR = "启动失败: {} {}"
        self.CREATE_LOG_PATH = "创建服务日志目录及用户授权: {}"
        self.CHECK_MIDDLEWARE_SERVICE = "检查主机{}服务 {}:{}"
        self.CHECK_MIDDLEWARE_SERVICE_PORT_SUCCEED = "检查主机端口{}:{}访问正常"
        self.CHECK_MIDDLEWARE_SERVICE_PORT_FAILED = "检查主机端口{}:{}访问异常"
        self.CHANGE_HARBOR_PASSWORD = "修改Harbor登陆密码"
        self.CHANGE_HARBOR_PASSWORD_SUCCEED = "修改Harbor登陆密码成功"
        self.CHANGE_HARBOR_PASSWORD_FAILED = "Harbor密码修改失败,新密码至少包含1个大写字母、1个小写字母和1个数字"
        self.HARBOR_REG_CONFIG_FAILED = "主机{} Harbor仓库管理配置失败, 状态码:{}"
        self.HARBOR_REPLICATION_SUCCEED = "Harbor复制管理配置成功"
        self.HARBOR_REPLICATION_FAILED = "Harbor复制管理配置失败"
        self.HARBOR_SYNC_SUCCEED = "Harbor 同步镜像成功, 状态码{}"
        self.HARBOR_SYNC_FAILED = "Harbor 同步镜像失败, 状态码{}"
        self.CLUSTER_REQUIRES_THREE = "集群模式最少需要三台机器"
        self.CONFIG_MYSQL_BACKUP_CRON = "配置Mysql备份定时任务"
        self.CONFIG_MYSQL_BACKUP_CRON_SUCCEED = "配置Mysql备份定时任务成功"
        self.CONFIG_MYSQL_BACKUP_CRON_FAILED = "配置Mysql备份定时任务失败"
        self.CHECK_REDIS_SERVICE_SUCCEED = "检查Redis哨兵服务通过"
        self.CHECK_REDIS_SERVICE_FAILED = "检查Redis哨兵服务失败: {}"
        self.INIT_IDENTITY_MYSQL_DATA = "初始化mysql identity数据表"
        self.CREATE_BUCKET = "创建MinIO bucket: {}"
        self.INIT_SIBER_MONGO_DATA = "初始化 siber-mongo 数据"
        self.INIT_SIBER_MONGO_DATA_ERROR = "初始化siber-mongo数据错误: {}"
        self.SIBER_CHECK_INFO = "请检查集成测试平台 '私有部署定制化mage plan' 运行结果, \n 集成测试平台访问地址http://{}:88"
        self.PUSH_IMAGE = "将镜像push到私有仓库: {}"
        self.PUSH_IMAGE_ERROR = "镜像{}导入失败：{}"
        self.TAG_IMAGE = "更新镜像tag, 旧地址: {}, 新地址: {}, tag: {}"
        self.CREATE_NAMESPACE = "创建命名空间: {}"
        self.GET_LOCAL_PATH_PVC_ERROR = "获取local path pvc错误: {}"
        self.GET_NFS_NODE_IP_ERROR = "获取NFS服务的node IP失败: {}"
        self.CREATE_PVC_ERROR = "pvc创建失败，请检查"
        self.DEPLOY_SERVICE = "服务进程开始部署: {}"
        self.SERVICE_EXISTS = "服务进程在HELM部署记录中已经存在: {}"
        self.APPTEST_SUCCEED = "{}自动化测试通过: {}"
        self.APPTEST_FAILED = "{}自动化测试未通过: {}"
        self.LOGIN_TENANT = "登录租户管理平台,请稍后..."
        self.INIT_ENTUC_USER_SUCCEED = "用户中心初始化用户成功: {}"
        self.INIT_ENTUC_USER_FAILED = "用户中心初始化用户失败: {}"
        self.GET_ENTUC_USER_JSON_ERROR = "{} 不是一个josn格式文件,请检查初始化entuc用户的返回结果"
        self.CONFIG_CLIENTS_SUCCEED = "用户中心配置client成功: {}"
        self.CONFIG_CLIENTS_FAILED = "用户中心配置client失败: {}"
        self.PRINT_PROJECT_INFO = "部署完成，以下是项目服务访问地址"
        self.PROJECT_POD_CHECK_SUCCEED = "命名空间: {}, 检查pod启动状态成功"
        self.PROJECT_POD_CHECK_FAILED = "命名空间: {}, 检查pod启动状态失败"

    def en(self):
        self.PRECHECK_FAILED = "Pre-check not excecuted or failed."
        self.HTTPS_CERTS_ERROR = "HTTPS deployments using client certificate, however, the certificate path is incorrect."
        self.FILE_NOT_FOUND = "{} File not found."
        self.SKIP_STEP = "Step {} after {} has been executed. Skip the current step."
        self.RUN_STEP = "To run {} {} method"
        self.EXCUTE_COMMAND = "Host: {}, Execute command: {}."
        self.COMMAND_ERROR = "Command Error：{}."
        self.LOCAL_FILL = "Rendering {} to {}."
        self.FILL_ERROR = "Error rendering {} file: {}"
        self.SEND_FILE = "Send file {} to {}:{}"
        self.PULL_FILE = "Pull file {}:{} to {}"
        self.CHECK_STATUS = "Check {} deploy status."
        self.KUBE_MASTER_INIT = "Initialize Kubernetes master node."
        self.JOIN_MASTER_NODE = "Join master node: {}"
        self.KUBE_JOIN_COMMAND_ERROR = "Failed to generate node join command: {} {}."
        self.INSTALL_ISTIO = "Install Istio component."
        self.INSTALL_ISTIO_ERROR = "Install Istio component ERROR."
        self.INSTALL_ROOK = "Install Rook: {}"
        self.CHECK_CEPH_STATUS = "Check rook-ceph status，it will take around 3-5 mins，please wait..."
        self.RENEN_KUBE_APISERVER_NGINX_CONFIG = "Update Kube apiserver address to nginx proxy."
        self.DECOMPRESS_HARBOR_DATA_ERROR = "Harbor data decompression or change user permisson failed: {} {}"
        self.START_MIDDLEWARE_SERVICE = "Start {} {} Service."
        self.RESTART_MIDDLEWARE_SERVICE = "Restart {} {} Service."
        self.RESET_MIDDLEWARE_SERVICE = "Reset {} {} Service."
        self.START_MIDDLEWARE_SERVICE_ERROR = "Start Failed: {} {}."
        self.CREATE_LOG_PATH = "Create a service log directory and change permission mode: {}."
        self.CHECK_MIDDLEWARE_SERVICE = "check {} service {}:{}"
        self.CHECK_MIDDLEWARE_SERVICE_PORT_SUCCEED = "Check host port {}:{} access successful."
        self.CHECK_MIDDLEWARE_SERVICE_PORT_FAILED = "Check host port {}:{} access abnomal."
        self.CHANGE_HARBOR_PASSWORD = "Change Harbor login password."
        self.CHANGE_HARBOR_PASSWORD_SUCCEED = "Change Harbor login password succeed."
        self.CHANGE_HARBOR_PASSWORD_FAILED = "Change Harbor login password failed. New password contains at least 1 uppercase letter, 1 lowercase letter and 1 number."
        self.HARBOR_REG_CONFIG_FAILED = "Host{} Harbor registry configuration failed, status code:{}"
        self.HARBOR_REPLICATION_SUCCEED = "Harbor replication configuration succeed, status code:{}"
        self.HARBOR_REPLICATION_FAILED = "Harbor replication configuration failed, status code:{}"
        self.HARBOR_SYNC_SUCCEED = "Harbor sync images succeed, status code:{}"
        self.HARBOR_SYNC_FAILED = "Harbor sync images failed,status code:{}"
        self.CLUSTER_REQUIRES_THREE = "Cluster mode requires 3 machines."
        self.CONFIG_MYSQL_BACKUP_CRON = "configure backup crontab for mysql."
        self.CONFIG_MYSQL_BACKUP_CRON_SUCCEED = "Host {} configure mysql backup crontab succeed."
        self.CONFIG_MYSQL_BACKUP_CRON_FAILED = "Host {} configure mysql backup crontab failed."
        self.CHECK_REDIS_SERVICE_SUCCEED = "Check Redis Sentinel succeed."
        self.CHECK_REDIS_SERVICE_FAILED = "Check Redis Sentinel failed.: {}"
        self.INIT_IDENTITY_MYSQL_DATA = "Initialize MySQL identity data table."
        self.CREATE_BUCKET = "Create MinIO bucket: {}"
        self.INIT_SIBER_MONGO_DATA = "Initialize siber-mongo data."
        self.INIT_SIBER_MONGO_DATA_ERROR = "Initialize siber-mongo data error: {}"
        self.SIBER_CHECK_INFO = "Please check the results of the siber platform \n Siber platform access address: http://{}:88"
        self.PUSH_IMAGE = "push image to harbor registry: {}"
        self.PUSH_IMAGE_ERROR = "Import image {} failed：{}"
        self.TAG_IMAGE = "Update image tag, old path: {}, new path: {}, tag: {}"
        self.CREATE_NAMESPACE = "Create namespace: {}"
        self.GET_LOCAL_PATH_PVC_ERROR = "Get local path pvc ERROR: {}"
        self.GET_NFS_NODE_IP_ERROR = "GET NFS node IP ERROR: {}"
        self.CREATE_PVC_ERROR = "PVC create failed."
        self.DEPLOY_SERVICE = "The service process begins deploy: {}"
        self.SERVICE_EXISTS = "The service already exists in the HELM deployment record: {}"
        self.APPTEST_SUCCEED = "{} apptest succeed: {}"
        self.APPTEST_FAILED = "{} apptest failed: {}"
        self.LOGIN_TENANT = "Logging commander tenant, please wait..."
        self.INIT_ENTUC_USER_SUCCEED = "EntUC init user succeed: {}"
        self.INIT_ENTUC_USER_FAILED = "EntUC init user failed: {}"
        self.GET_ENTUC_USER_JSON_ERROR = "{} not a json file. check usercenter init user response."
        self.CONFIG_CLIENTS_SUCCEED = "Entuc configure client succeed: {}"
        self.CONFIG_CLIENTS_FAILED = "Entuc configure client failed: {}"
        self.PRINT_PROJECT_INFO = "Deploy Succeed！The following is the access address of the project service."
        self.PROJECT_POD_CHECK_SUCCEED = "Namespace: {}, check project pod start succeed."
        self.PROJECT_POD_CHECK_FAILED = "Namespace: {}, check project pod start failed."
