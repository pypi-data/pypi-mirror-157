"""Contains utils required for sdk layer.

Methods in this module to be used for sdk layer only.
"""
import logging
from copy import deepcopy

from RhcsQeSdk.core.cli import fabfile
from RhcsQeSdk.core.utilities.metadata import Metadata

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s"
)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(stream_handler)


def build_cmd_args(seperator=None, **kw):
    """This method checks from the dictionary the optional arguments
    if present it adds them in "cmd" and returns cmd.
    Args:
        kw(dict) -> Takes a dictionary as an input.
        seperator(bool) -> True if key and value needs to be separated with an =.
    Returns:
        cmd(str): Returns a command string.

    eg:
        Args:
            seperator: None
            kw={"uid":"<uid>", "purge-keys": True, "purge-data":True}
        Returns:
            " --uid <uid> --purge-keys --purge-data"
    """
    kw = kw.get("kw")
    cmd = ""
    if kw is None:
        return ""
    for k, v in kw.items():
        if kw[k] and str(k) != "env_config" and str(k) != "cluster_name":
            if v is True:
                cmd = cmd + f" --{k}"
            else:
                if not seperator:
                    cmd = cmd + f" --{k} {v}"
                else:
                    cmd = cmd + f" --{k}={v}"
    return cmd


def parse_host_name(host_name, cluster_name):
    """
    This method parses hostname based on clustername.
    Args:
        hostname(str) -> name of node.
        cluster_name(str) -> name of cluster.
    Returns:
        hosts(list): Returns a list of node names.
    """
    ceph = Metadata().__dict__.get("ceph")
    if host_name == "all":
        return ceph.ceph_node.get_vm_nodes(cluster_name)
    else:
        nodes_list = ceph.ceph_role.get_nodenames_by_role(host_name, cluster_name)
        return " ".join(nodes_list)


def copy_admin_sshkeys(**kw):
    """
    This method distributes cephadm public keys to other nodes.
    Args:
        kw(dict) -> Takes a dictionary as an input.
    Returns:
        Dict(str)
        A mapping of host strings of the given task's return value for that host's execution run.
    """
    kw = kw.get("kw")
    env_config_copy = deepcopy(kw.get("env_config"))
    env_config_copy["username"] = "root"
    env_config_copy["password"] = "passwd"
    ceph_cluster_dict = kw.get("ceph_cluster_dict")
    cluster_name = kw.get("cluster_name")
    ips = []
    nodes = ceph_cluster_dict[cluster_name].get_nodes("_admin")
    for node in nodes:
        ips.append(node.ip_address)
    env_config_copy["hosts"] = ips
    out = fabfile.run_command("cat /etc/ceph/ceph.pub", env_config_copy)
    out = list(out.values())[0]
    ceph_pub_key = f"\n{out}"
    ips = []
    nodes = ceph_cluster_dict[cluster_name].get_nodes()
    for node in nodes:
        ips.append(node.ip_address)
    for ip in ips:
        env_config_copy["hosts"] = ip
        fabfile.run_command(
            f"echo -e '{ceph_pub_key}' >> .ssh/authorized_keys", env_config_copy
        )
    nodes = ceph_cluster_dict[cluster_name].get_nodes()
    for i in range(len(nodes)):
        env_config_copy["hosts"] = nodes[i].ip_address
        logger.info("Updating fqdnhostnames to shortnames")
        fabfile.run_command(f"hostname {nodes[i].hostname}", env_config_copy)
