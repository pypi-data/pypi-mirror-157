from __future__ import absolute_import
from __future__ import unicode_literals

import os
import time
from laipvt.handler.confighandler import CheckResultHandler, ServerHandler
from laipvt.handler.packagehandler import KubePackageHandler
from laipvt.handler.kubehandler import KubeConfigHandler
from laipvt.sysutil.util import path_join, ssh_obj, log, status_me
from laipvt.helper.errors import Helper

from laipvt.sysutil.template import FileTemplate
from laipvt.model.cmd import KubeModel
from laipvt.sysutil.command import BASH_RUN, CP_KUBEADM, KUBE_INIT, CREATE_KUBE_DIR, CP_KUBE_CONFIG, \
    KUBECTL_COMPLETION, KUBECTL_APPLY, KUBEADM_TOKEN_CREATE, TAR_KUBE_CRETS, UNTAR_KUBE_CRETS, ADD_MASTER_SUFFIX, \
    TAINT_MASTER, HELM_PATH, TILLER_PATH, TILLER_SERVICE_PATH, CHMOD_EXECUTE, SYSTEMCTL_DAEMON_RELOAD, SYSTEMCTL_START, \
    SYSTEMCTL_ENABLE, ISTIOCTL_PATH, ISTIOCTL_INSTALL, CHECK_ISTIO, KUBECTL_CREATE, CHECK_RUNNING_CMD, \
    GET_ROOK_CEPH_DASHBOARD_PASSWORD_CMD, CREATE_NS


class KubeInterface:
    def __init__(self, result: CheckResultHandler, kube: KubePackageHandler.parse, *args, **kwargs):
        self.result = result
        self.kube_config = KubeConfigHandler(result, *args, **kwargs).get()
        self.info = kube
        self.base_dir = path_join(result.deploy_dir, "kubernetes")

        self.kube_admin_file_template = path_join(self.info.templates, "admin.tmpl")
        self.kube_admin_file = path_join(self.info.templates, "admin.conf")

        self.hosts_file_template = path_join(self.info.templates, "hosts.tmpl")
        self.hosts_file = path_join(self.info.templates, "hosts")

        self.system_init_template = path_join(self.info.templates, "init_env.tmpl")
        self.system_init_file = path_join(self.info.templates, "init_env.sh")

        self.flannel_template = path_join(self.info.templates, "kube-flannel.tmpl")
        self.flannel_file = path_join(self.info.templates, "kube-flannel.yaml")

        self.nvidia_plugin_template = path_join(self.info.templates, "nvidia-device-plugin.tmpl")
        self.nvidia_plugin_file = path_join(self.info.templates, "nvidia-device-plugin.yaml")

        self.istio_template = path_join(self.info.plugin.istio, "service/istio-private-deploy.tmpl")
        self.istio_file = path_join(self.info.plugin.istio, "service/istio-private-deploy.yaml")

        self.local_tmp = path_join(os.path.dirname(self.info.templates), "tmp")

        self.master = result.servers.get_role_obj("master")[0]
        self.master_servers = result.servers.get_role_obj("master")
        self.all_servers = result.servers.get_role_obj("master")
        self.servers = result.servers.get()

        self.network_plugin_file = path_join(
            self.info.plugin.network,
            "{}.yaml".format(self.kube_config["network_plugin"])
        )

        self.pki_tar_name = "pki.tar.gz"
        self.remote_pki_path = path_join("/etc/kubernetes", self.pki_tar_name)
        self.kubeconfig_file = "/etc/kubernetes/admin.conf"
        self.kubeconfig_local = "~/.kube/config"
        self.kube_config.update(self.result.__dict__)
        self.rook_ceph_dir = path_join(self.info.plugin.rook, "cluster/examples/kubernetes/ceph/")
        self.rook_ceph_remote_path = path_join(self.base_dir, "ceph")
        self.local_path_provisioner_dir = path_join(self.info.plugin.rook, "cluster/examples/kubernetes/local-path-provisioner/")
        self.local_path_provisioner_remote_path = path_join(self.base_dir, "local-path-provisioner/")
        self.rook_nfs_dir = path_join(self.info.plugin.rook, "cluster/examples/kubernetes/nfs/")
        self.rook_nfs_remote_path = path_join(self.base_dir, "nfs")


    def _exec_command_to_host(self, cmd, server: ServerHandler, check_res=True):
        log.info(Helper().EXCUTE_COMMAND.format(server.ipaddress, cmd))
        if isinstance(cmd, list):
            ssh_cli = ssh_obj(ip=server.ipaddress, user=server.username, password=server.password, port=server.port)
            res_list = ssh_cli.run_cmdlist(cmd)
            ssh_cli.close()
            if check_res:
                for res in res_list:
                    if res["code"] != 0:
                        log.error("{} {}".format(res["stdout"], res["stderr"]))
                        exit(2)
            return res_list
        if isinstance(cmd, str):
            ssh_cli = ssh_obj(ip=server.ipaddress, user=server.username, password=server.password, port=server.port)
            res = ssh_cli.run_cmd(cmd)
            ssh_cli.close()
            if check_res:
                if res["code"] != 0:
                    log.error("{} {}".format(res["stdout"], res["stderr"]))
                    exit(2)
            return res
        else:
            log.error(Helper().COMMAND_ERROR.format(cmd))
            exit(2)

    @status_me("basesystem")
    def create_namespace(self):
        # 临时解决istio vs 命名空间问题
        vs_namespaces = ["commander", "notice", "usercenter", "creativity", "entcmd", "internet", "istio-system",
                         "mid", "proxy", "rpa-collaboration"]
        for ns in vs_namespaces:
            log.info(Helper().CREATE_NAMESPACE.format(ns))
            cmd = CREATE_NS.format(ns)
            self._exec_command_to_host(cmd=cmd, server=self.master, check_res=False)

    def _generate_file(self, template_file, dest_file):
        log.info(Helper().LOCAL_FILL.format(template_file, dest_file))
        FileTemplate(self.kube_config, template_file, dest_file).fill()
        if not os.path.isfile(dest_file):
            error_msg = "Error"
            log.error(Helper().FILL_ERROR.format(template_file, error_msg))
            exit(2)
        return True

    def _send_file(self, src, dest, role=""):
        l = []
        if role:
            for server in self.servers:
                if server.role.check(role):
                    l.append(server)
        else:
            l = self.servers
        for server in l:
            log.info(Helper().SEND_FILE.format(src, server.ipaddress, dest))
            ssh_cli = ssh_obj(ip=server.ipaddress, user=server.username, password=server.password, port=server.port)
            try:
                ssh_cli.put(src, dest)
            except Exception as e:
                log.error(e)
                exit(2)
            finally:
                ssh_cli.close()

    def _get_file(self, src, dest, server: ServerHandler):
        log.info(Helper().PULL_FILE.format(server.ipaddress, src, dest))
        if not os.path.isdir(os.path.dirname(dest)):
            os.makedirs(os.path.dirname(dest))
        ssh_cli = ssh_obj(ip=server.ipaddress, user=server.username, password=server.password, port=server.port)
        try:
            ssh_cli.get(src, dest)
        except Exception as e:
            log.error(e)
            exit(2)
        finally:
            ssh_cli.close()

    def _check_pod_status(self, namespace, pod_label, retry_count, retry_time_interval):
        log.info(Helper().CHECK_STATUS.format(pod_label))
        # 重试 x 次，每次间隔x秒，如果还是不成功就报错
        counter = 0
        succeed = False
        while not succeed and counter < retry_count:
            time.sleep(retry_time_interval)
            check_cmd = CHECK_RUNNING_CMD.format(namespace, pod_label)
            res = self._exec_command_to_host(cmd=check_cmd, server=self.master, check_res=True)
            res_list = res["stdout"].split(" ")
            # 判断返回全部是Running状态
            if len(set(res_list)) == 1 and res_list[0] == "Running":
                succeed = True
            else:
                succeed = False
                counter += 1
        return succeed

    @status_me("basesystem")
    def add_hosts(self):
        self._generate_file(template_file=self.hosts_file_template, dest_file=self.hosts_file)
        self._send_file(self.hosts_file, "/etc/hosts")

    # @status_me("basesystem")
    # def install_rpms(self):
    #     self._send_file(self.info["k8s-rpms"], path_join(self.base_dir, "k8s-rpms"))
    #     cmd_list = [
    #         # "rpm -ivUh {}/*.rpm --force --nodeps".format(path_join(self.base_dir, "k8s-rpms")),
    #         CP_KUBEADM.format(path_join(self.base_dir, "k8s-rpms"))
    #     ]
    #     for server in self.servers:
    #         self._exec_command_to_host(cmd=cmd_list, server=server, check_res=False)

    @status_me("basesystem")
    def system_prepare(self):
        self._generate_file(template_file=self.system_init_template, dest_file=self.system_init_file)
        self._send_file(self.system_init_file, path_join(self.base_dir, "init_env.sh"))
        cmd = BASH_RUN.format(path_join(self.base_dir, "init_env.sh"))
        for server in self.servers:
            log.info(Helper().EXCUTE_COMMAND.format(server.ipaddress, path_join(self.base_dir, "init_env.sh")))
            self._exec_command_to_host(cmd=cmd, server=server)

    @status_me("basesystem")
    def init_primary_master(self):
        log.info(Helper().KUBE_MASTER_INIT)
        self._generate_file(template_file=self.kube_admin_file_template, dest_file=self.kube_admin_file)
        self._send_file(self.kube_admin_file, path_join(self.base_dir, "admin.conf"))
        cmd = KUBE_INIT.format(path_join(self.base_dir, "admin.conf"))
        self._exec_command_to_host(cmd=cmd, server=self.master)

    @status_me("basesystem")
    def cp_kube_config(self):
        cmd = [
            CREATE_KUBE_DIR,
            CP_KUBE_CONFIG
        ]
        for server in self.all_servers:
            self._exec_command_to_host(cmd=cmd, server=server, check_res=False)

    @status_me("basesystem")
    def kube_completion(self):
        cmd = KUBECTL_COMPLETION
        self._exec_command_to_host(cmd=cmd, server=self.master)

    @status_me("basesystem")
    def install_network_plugin(self):
        self._generate_file(template_file=self.flannel_template, dest_file=self.flannel_file)
        self._send_file(self.flannel_file, path_join(self.base_dir, "kube-flannel.yaml"))
        cmd = KUBECTL_APPLY.format(path_join(self.base_dir, "kube-flannel.yaml"))
        self._exec_command_to_host(cmd=cmd, server=self.master)

    @status_me("basesystem")
    def install_nvidia_device_plugin(self):
        self._generate_file(template_file=self.nvidia_plugin_template, dest_file=self.nvidia_plugin_file)
        self._send_file(self.nvidia_plugin_file, path_join(self.base_dir, "nvidia-device-plugin.yaml"))
        cmd = KUBECTL_APPLY.format(path_join(self.base_dir, "nvidia-device-plugin.yaml"))
        self._exec_command_to_host(cmd=cmd, server=self.master)

    def get_kube_admin_join_command(self) -> str:
        cmd = KUBEADM_TOKEN_CREATE.format(path_join(self.base_dir, "admin.conf"))
        res = self._exec_command_to_host(cmd=cmd, server=self.master)

        if res["code"] == 0 and "kubeadm join" in res["stdout"]:
            return res["stdout"].strip().split("\n")[-1]
        else:
            log.error(Helper().KUBE_JOIN_COMMAND_ERROR.format(res["stdout"], res["stderr"]))
            exit(2)

    @status_me("basesystem")
    def join_master(self):
        # 1、连接master-01，打包需要拷贝的证书配置，拉到本地
        cmd = TAR_KUBE_CRETS.format(self.remote_pki_path)
        self._exec_command_to_host(cmd=cmd, server=self.master)
        self._get_file(src=self.remote_pki_path, dest=path_join(self.local_tmp, self.pki_tar_name), server=self.master)

        other_masters = []
        for server in self.master_servers:
            if server.ipaddress != self.master.ipaddress:
                other_masters.append(server)

        join_cmd = self.get_kube_admin_join_command()
        for i, server in enumerate(other_masters):
            self._send_file(src=path_join(self.local_tmp, self.pki_tar_name), dest=self.remote_pki_path)
            cmd = UNTAR_KUBE_CRETS.format(self.remote_pki_path)
            self._exec_command_to_host(cmd=cmd, server=server)

            log.info(Helper().JOIN_MASTER_NODE.format(server.ipaddress))
            node_name = "master-0{}".format(i + 2)
            cmd = ADD_MASTER_SUFFIX.format(join_cmd, node_name)
            self._exec_command_to_host(cmd=cmd, server=server)

    @status_me("basesystem")
    def join_node(self):
        node = list(set(self.result.servers.get_role_ip("node")) - set(self.result.servers.get_role_ip("master")))
        if len(node) <= 3:
            for i, server in enumerate(self.result.servers.get_role_obj("master")):
                node_name = "master-0{}".format(i + 1)
                cmd = TAINT_MASTER.format(node_name)
                self._exec_command_to_host(cmd=cmd, server=self.master)
        if len(node) > 0:
            for index, server in enumerate(self.result.servers.get_role_obj("node")):
                if server.ipaddress in node:
                    cmd = self.get_kube_admin_join_command() + " --node-name=node-{}".format(str(index + 1).zfill(2))
                    self._exec_command_to_host(cmd=cmd, server=server)

    def check_cluster_status(self) -> bool:
        kube = KubeModel()
        status = kube.get_node_status()
        print(status)
        for i in status:
            if i["node_status"] != "Ready":
                return False
        return True

    @status_me("basesystem")
    def install_helm(self):
        self._send_file(src=path_join(self.info.plugin.helm, "bin/helm"), dest=HELM_PATH)
        self._send_file(src=path_join(self.info.plugin.helm, "bin/tiller"), dest=TILLER_PATH)
        self._send_file(
            src=path_join(self.info.plugin.helm, "service/tiller.service"),
            dest=TILLER_SERVICE_PATH
        )
        cmd_list = [
            CHMOD_EXECUTE.format(HELM_PATH), CHMOD_EXECUTE.format(TILLER_PATH),
            SYSTEMCTL_DAEMON_RELOAD, SYSTEMCTL_START.format("tiller.service"), SYSTEMCTL_ENABLE.format("tiller.service")
        ]
        self._exec_command_to_host(cmd=cmd_list, server=self.master, check_res=True)

    def _restart_coredns(self):
        cmd = "kubectl -n kube-system rollout restart deployment coredns"
        self._exec_command_to_host(cmd=cmd, server=self.master, check_res=True)


    @status_me("basesystem")
    def install_istio(self):
        self._restart_coredns()
        self._send_file(src=path_join(self.info.plugin.istio, "bin/istioctl"), dest=ISTIOCTL_PATH)
        self._generate_file(template_file=self.istio_template, dest_file=self.istio_file)
        istio_remote_file = path_join(self.base_dir, "istio-private-deploy.yaml")
        self._send_file(src=self.istio_file, dest=istio_remote_file)

        cmd = CHMOD_EXECUTE.format(ISTIOCTL_PATH)
        self._exec_command_to_host(cmd=cmd, server=self.master, check_res=True)

        log.info(Helper().INSTALL_ISTIO)
        install_cmd = ISTIOCTL_INSTALL.format(path_join(self.base_dir, "istio-private-deploy.yaml"))
        self._exec_command_to_host(cmd=install_cmd, server=self.master, check_res=True)

        time.sleep(30)
        check_cmd = CHECK_ISTIO
        res = self._exec_command_to_host(cmd=check_cmd, server=self.master, check_res=True)
        try:
            if int(res["stdout"]) != 21:
                log.error(Helper().INSTALL_ISTIO_ERROR)
                exit(2)
        except Exception:
            log.error(Helper().INSTALL_ISTIO_ERROR)
            exit(2)


    def _generate_send_rook_file(self):
        self.rook_ceph_operator_template = path_join(self.rook_ceph_dir, "operator.tmpl")
        self.rook_ceph_operator_file = path_join(self.rook_ceph_dir, "operator.yaml")
        self._generate_file(template_file=self.rook_ceph_operator_template, dest_file=self.rook_ceph_operator_file)

        if len(self.servers) < 3:
            self.rook_ceph_cluster_template = path_join(self.rook_ceph_dir, "cluster-test.tmpl")
        else:
            self.rook_ceph_cluster_template = path_join(self.rook_ceph_dir, "cluster.tmpl")
        self.rook_ceph_cluster_file = path_join(self.rook_ceph_dir, "cluster.yaml")
        self._generate_file(template_file=self.rook_ceph_cluster_template, dest_file=self.rook_ceph_cluster_file)

        self.rook_ceph_tools_template = path_join(self.rook_ceph_dir, "toolbox.tmpl")
        self.rook_ceph_tools_file = path_join(self.rook_ceph_dir, "toolbox.yaml")
        self._generate_file(template_file=self.rook_ceph_tools_template, dest_file=self.rook_ceph_tools_file)

        # 发送rook-ceph 目录文件
        self.rook_ceph_remote_path = path_join(self.base_dir, "ceph")
        self._send_file(src=self.rook_ceph_dir, dest=self.rook_ceph_remote_path)

    def _install_rook_crds(self):
        self.rook_ceph_crds = path_join(self.rook_ceph_dir, "crds.yaml")
        install_crds_cmd = KUBECTL_CREATE.format(path_join(self.rook_ceph_remote_path, "crds.yaml"))
        self._exec_command_to_host(cmd=install_crds_cmd, server=self.master, check_res=False)

    def _install_rook_common(self):
        self.rook_ceph_common = path_join(self.rook_ceph_dir, "common.yaml")
        install_common_cmd = KUBECTL_CREATE.format(path_join(self.rook_ceph_remote_path, "common.yaml"))
        self._exec_command_to_host(cmd=install_common_cmd, server=self.master, check_res=False)

    def _install_rook_operator(self):
        install_operator_cmd = KUBECTL_CREATE.format(path_join(self.rook_ceph_remote_path, "operator.yaml"))
        self._exec_command_to_host(cmd=install_operator_cmd, server=self.master, check_res=False)
        # 重试 10 次，每次间隔6秒，如果还是不成功就报错
        counter = 0
        succeed = False
        while not succeed and counter < 10:
            time.sleep(6)
            res = self._exec_command_to_host(cmd=CHECK_RUNNING_CMD.format("rook-ceph", "rook-ceph-operator"),
                                             server=self.master, check_res=True)
            if res["stdout"].strip() == "Running":
                succeed = True
            else:
                succeed = False
                counter += 1
        if not succeed:
            log.error("operator部署未成功，请检查。")
            exit(2)

    def _install_rook_ceph(self):
        install_cluster_cmd = KUBECTL_CREATE.format(path_join(self.rook_ceph_remote_path, "cluster.yaml"))
        res = self._exec_command_to_host(cmd=install_cluster_cmd, server=self.master, check_res=True)

        if res["code"] != 0 or "created" not in res["stdout"]:
            log.error("部署ceph cluster失败，请检查：kubectl -n rook-ceph get pod")
            exit(2)

    def _install_rook_tools(self):
        self.rook_ceph_tools = path_join(self.rook_ceph_dir, "toolbox.yaml")
        install_cmd = KUBECTL_CREATE.format(path_join(self.rook_ceph_remote_path, "toolbox.yaml"))
        self._exec_command_to_host(cmd=install_cmd, server=self.master, check_res=False)

    def _check_rook_ceph_cluster(self):
        log.info(Helper().CHECK_CEPH_STATUS)
        check_list = ["csi-cephfsplugin", "csi-cephfsplugin-provisioner",
                      "csi-rbdplugin", "csi-rbdplugin-provisioner",
                      "rook-ceph-mgr","rook-ceph-mon", "rook-ceph-osd",
                      "rook-ceph-tools"]

        # 重试 20 次，每次间隔20秒，如果还是不成功就报错
        counter = 0
        succeed = False
        while not succeed and counter < 20:
            time.sleep(20)
            for i in check_list:
                check_cmd = CHECK_RUNNING_CMD.format("rook-ceph", i)
                res = self._exec_command_to_host(cmd=check_cmd, server=self.master, check_res=True)
                res_list = res["stdout"].split(" ")
                # 判断返回全部是Running状态
                if len(set(res_list)) == 1 and res_list[0] == "Running":
                    succeed = True
                else:
                    succeed = False
                    counter += 1
                    break
        if not succeed:
            log.error("rook-ceph集群部署失败，请检查")
            exit(2)

    def _dashboard_external(self):
        self.rook_ceph_http = path_join(self.rook_ceph_dir, "dashboard-external-http.yaml")
        install_cmd = KUBECTL_CREATE.format(path_join(self.rook_ceph_remote_path, "dashboard-external-http.yaml"))
        self._exec_command_to_host(cmd=install_cmd, server=self.master, check_res=False)
        self.rook_ceph_http = path_join(self.rook_ceph_dir, "dashboard-external-https.yaml")
        install_cmd = KUBECTL_CREATE.format(path_join(self.rook_ceph_remote_path, "dashboard-external-https.yaml"))
        self._exec_command_to_host(cmd=install_cmd, server=self.master, check_res=False)
        res = self._exec_command_to_host(cmd=GET_ROOK_CEPH_DASHBOARD_PASSWORD_CMD, server=self.master, check_res=False)
        log.info(res["stdout"])

    def _install_storageclass(self):
        if len(self.servers) < 3:
            install_cmd = KUBECTL_CREATE.format(path_join(self.rook_ceph_remote_path, "filesystem-test.yaml"))
        else:
            install_cmd = KUBECTL_CREATE.format(path_join(self.rook_ceph_remote_path, "filesystem.yaml"))
        self._exec_command_to_host(cmd=install_cmd, server=self.master, check_res=False)

        if not self._check_pod_status(namespace="rook-ceph", pod_label="rook-ceph-mds",
                                      retry_count=6, retry_time_interval=10):
            log.error("pod启动失败,请检查启动状态")
            exit(2)

        install_cmd = KUBECTL_CREATE.format(path_join(self.rook_ceph_remote_path, "storageclass.yaml"))
        self._exec_command_to_host(cmd=install_cmd, server=self.master, check_res=False)

    def _install_local_path_storage(self):
        self.local_path_provisioner_template = path_join(self.local_path_provisioner_dir, "local-path-storage.tmpl")
        self.local_path_provisioner_file = path_join(self.local_path_provisioner_dir, "local-path-storage.yaml")
        self._generate_file(template_file=self.local_path_provisioner_template, dest_file=self.local_path_provisioner_file)

        # 发送目录文件
        self.local_path_provisioner_remote_path = path_join(self.base_dir, "local-path-provisioner")
        self._send_file(src=self.local_path_provisioner_dir, dest=self.local_path_provisioner_remote_path)

        install_cmd = KUBECTL_CREATE.format(path_join(self.local_path_provisioner_remote_path, "local-path-storage.yaml"))
        self._exec_command_to_host(cmd=install_cmd, server=self.master)

        if not self._check_pod_status(namespace="rook-nfs", pod_label="local-path-provisioner",
                                      retry_count=6, retry_time_interval=10):
            log.error("pod启动失败,请检查启动状态")
            exit(2)

    def _install_rook_nfs(self):
        self.rook_nfs_operator_template = path_join(self.rook_nfs_dir, "operator.tmpl")
        self.rook_nfs_operator_file = path_join(self.rook_nfs_dir, "operator.yaml")
        self._generate_file(template_file=self.rook_nfs_operator_template, dest_file=self.rook_nfs_operator_file)

        # 发送rook-ceph 目录文件
        self.rook_nfs_remote_path = path_join(self.base_dir, "nfs")
        self._send_file(src=self.rook_nfs_dir, dest=self.rook_nfs_remote_path)

        install_cmd = KUBECTL_CREATE.format(path_join(self.rook_nfs_remote_path, "crds.yaml"))
        self._exec_command_to_host(cmd=install_cmd, server=self.master, check_res=False)

        install_cmd = KUBECTL_CREATE.format(path_join(self.rook_nfs_remote_path, "operator.yaml"))
        self._exec_command_to_host(cmd=install_cmd, server=self.master, check_res=False)

        if not self._check_pod_status(namespace="rook-nfs-system", pod_label="rook-nfs-operator", retry_count=6, retry_time_interval=10):
            log.error("pod启动失败,请检查启动状态")
            exit(2)

        install_cmd = KUBECTL_CREATE.format(path_join(self.rook_nfs_remote_path, "psp.yaml"))
        self._exec_command_to_host(cmd=install_cmd, server=self.master, check_res=False)

        install_cmd = KUBECTL_CREATE.format(path_join(self.rook_nfs_remote_path, "rbac.yaml"))
        self._exec_command_to_host(cmd=install_cmd, server=self.master, check_res=False)

        install_cmd = KUBECTL_CREATE.format(path_join(self.rook_nfs_remote_path, "nfs.yaml"))
        self._exec_command_to_host(cmd=install_cmd, server=self.master, check_res=False)

        if not self._check_pod_status(namespace="rook-nfs", pod_label="rook-nfs", retry_count=6, retry_time_interval=20):
            log.error("pod启动失败,请检查启动状态")
            exit(2)

        install_cmd = KUBECTL_CREATE.format(path_join(self.rook_nfs_remote_path, "sc.yaml"))
        self._exec_command_to_host(cmd=install_cmd, server=self.master, check_res=False)

    @status_me("basesystem")
    def install_rook(self):
        if self.result.config.use_external_disk:
            log.info(Helper().INSTALL_ROOK.format("rook-ceph"))
            self._generate_send_rook_file()
            self._install_rook_crds()
            self._install_rook_common()
            self._install_rook_operator()
            self._install_rook_ceph()
            self._install_rook_tools()
            self._check_rook_ceph_cluster()
            self._dashboard_external()
            self._install_storageclass()
        else:
            log.info(Helper().INSTALL_ROOK.format("rook-nfs"))
            self._install_local_path_storage()
            self._install_rook_nfs()


    @status_me("basesystem")
    def install_chaosblade(self):
        if os.path.exists(self.info.plugin.chaosblade):
            self.chaosblade_src = path_join(self.info.plugin.chaosblade)
            self.chaosblade_dest = "/usr/local/chaosblade"

            self.chaosblade_service_src = path_join(self.info.plugin.chaosblade, "chaosblade.service")
            self.chaosblade_service_remote = "/usr/lib/systemd/system/chaosblade.service"
            self._send_file(src=self.chaosblade_service_src, dest=self.chaosblade_service_remote)
            self._send_file(src=self.chaosblade_src, dest=self.chaosblade_dest)

            cmd_list = [
                SYSTEMCTL_DAEMON_RELOAD,
                SYSTEMCTL_START.format("chaosblade.service"),
                SYSTEMCTL_ENABLE.format("chaosblade.service")
            ]
            self._exec_command_to_host(cmd=cmd_list, server=self.master, check_res=True)
