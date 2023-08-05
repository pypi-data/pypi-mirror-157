import copy
import logging

import RhcsQeSdk.core.cli.fabfile as fabfile
from RhcsQeSdk.core.utilities.metadata import Metadata
from RhcsQeSdk.core.utilities.test_config_run import ConfigRun
from RhcsQeSdk.core.utilities.utils import copy_admin_sshkeys, transfer_remote_files
from RhcsQeSdk.scripts.install_prereq import (
    ConfigureAnsibleInventory,
    ConfigureFirewall,
    SetUpSSHKeys,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s"
)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)


def run(kw):
    test_data = kw.get("test_data")
    cluster_name = kw.get("cluster_name")
    output = {"cluster_names": [], "rc": 1}
    if cluster_name:
        output["cluster_names"].append(cluster_name)
    for step in test_data.get("configs"):
        for role in step.get("role"):
            if len(role.split(":")) == 2:
                output["cluster_names"].append(role.split(":")[0])
    ceph_cluster_dict = kw.get("ceph_cluster_dict")
    metadata = Metadata()
    metadata.ceph_cluster_dict = ceph_cluster_dict
    env_config = {
        "username": "root",
        "password": "passwd",
        "parallel": True,
        "timeout": 300,
    }
    for step in test_data.get("configs"):
        installer = step.get("installer")
        if installer == "cephadm":
            logger.info("Installing prerequisite for cephadm installer")
            ips = []
            nodes = ceph_cluster_dict[cluster_name].get_nodes("installer")
            for node in nodes:
                ips.append(node.ip_address)
            env_config["hosts"] = ips
            cmds = [
                "yum install -y docker",
            ]
            for cmd in cmds:
                if not fabfile.run_command(cmd, env_config):
                    return output
        elif installer == "cephadm-ansible" or None:
            logger.info("Installing prerequisite for cephadm-ansible installer")
            nodes = ceph_cluster_dict[cluster_name].get_nodes()
            ips = []
            for node in nodes:
                ips.append(node.ip_address)
            env_config["hosts"] = ips
            base_path = "/usr/share/cephadm-ansible"
            base_cmd = "ansible-playbook -i"
            for tools_repository in [
                "ansible-2.9-for-rhel-8-x86_64-rpms",
                "rhceph-5-tools-for-rhel-8-x86_64-rpms",
            ]:
                cmd = f"subscription-manager repos --enable={tools_repository}"
                if not fabfile.run_command(cmd, env_config):
                    return output
            cmds = [
                "yum install -y ceph-common",
                "yum install -y cephadm",
                "yum install -y cephadm-ansible",
            ]
            for cmd in cmds:
                if not fabfile.run_command(cmd, env_config):
                    return output
            SetUpSSHKeys().run(
                cluster_name=cluster_name, ceph_cluster_dict=ceph_cluster_dict
            )
            ConfigureFirewall().run(env_config=env_config)
            ConfigureAnsibleInventory().run(
                cluster_name=cluster_name,
                ceph_cluster_dict=ceph_cluster_dict,
                installer=installer,
            )
            env_config_copy = copy.deepcopy(env_config)
            env_config_copy["username"] = "cephuser"
            env_config_copy["password"] = "cephuser"
            nodes = ceph_cluster_dict[cluster_name].get_nodes("installer")
            ips = []
            for node in nodes:
                ips.append(node.ip_address)
            env_config_copy["hosts"] = ips
            fabfile.run_command(
                f"{base_cmd} {base_path}/hosts {base_path}/cephadm-preflight.yml",
                env_config_copy,
            )
            nodes = ceph_cluster_dict[cluster_name].get_nodes("_admin")
            ips = []
            for node in nodes:
                ips.append(node.ip_address)
            env_config["hosts"] = ips
        if not ConfigRun(
            cluster_name, ceph_cluster_dict, is_redefine_args=True, is_root=True
        ).run_step(step, env_config):
            return output
    kw = {
        "cluster_name": cluster_name,
        "env_config": env_config,
        "ceph_cluster_dict": ceph_cluster_dict,
    }
    copy_admin_sshkeys(kw=kw)
    kw = {
        "source_role": f"{cluster_name}:_admin",
        "source_path": "/etc/ceph/ceph.conf",
        "destination_path": "/etc/ceph/ceph.conf",
        "destination_role": f"{cluster_name}:client",
        "cluster_name": cluster_name,
        "env_config": env_config,
        "ceph_cluster_dict": ceph_cluster_dict,
    }
    transfer_remote_files(kw=kw)
    kw["source_path"] = "/etc/ceph/ceph.client.admin.keyring"
    kw["destination_path"] = "/etc/ceph/ceph.client.admin.keyring"
    transfer_remote_files(kw=kw)
    output["rc"] = 0
    return output
