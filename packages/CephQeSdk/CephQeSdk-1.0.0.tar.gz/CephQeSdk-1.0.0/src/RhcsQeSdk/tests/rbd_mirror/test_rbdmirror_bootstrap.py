from RhcsQeSdk.core.utilities.test_config_run import ConfigRun
from RhcsQeSdk.core.utilities.utils import (
    create_file,
    read_from_file,
    sleep,
    write_to_file,
)


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
    steps = test_data.get("configs")
    step0_cluster_name = steps[0].get("role")[0].split(":")[0]
    output["cluster_names"].append(step0_cluster_name)
    ips = []
    nodes = ceph_cluster_dict[step0_cluster_name].get_nodes("client")
    for node in nodes:
        ips.append(node.ip_address)
    env_config = {
        "hosts": ips,
        "username": "cephuser",
        "password": "cephuser",
        "parallel": True,
    }
    kw = {
        "file_name": "bootstrap_token_master",
        "path": "/home/cephuser",
        "env_config": env_config,
    }
    create_file(kw=kw)
    if not ConfigRun(step0_cluster_name, ceph_cluster_dict).run_step(steps[0]):
        return output
    kw = {
        "sleep_time": 30,
    }
    sleep(kw=kw)

    kw = {
        "file_name": "bootstrap_token_master",
        "path": "/home/cephuser",
        "env_config": env_config,
    }
    token = list(read_from_file(kw=kw).values())[0]
    token_path = steps[1].get("args").get("token_path")
    step1_cluster_name = steps[1].get("role")[0].split(":")[0]
    role = steps[1].get("role")[0].split(":")[1]
    ips = []
    nodes = ceph_cluster_dict[step1_cluster_name].get_nodes(role)
    for node in nodes:
        ips.append(node.ip_address)
    env_config = {
        "hosts": ips,
        "username": "cephuser",
        "password": "cephuser",
        "parallel": True,
    }
    kw = {
        "file_name": "bootstrap_token_master",
        "path": "/home/cephuser",
        "env_config": env_config,
    }
    create_file(kw=kw)
    kw = {
        "content": token,
        "path": token_path,
        "env_config": env_config,
    }
    write_to_file(kw=kw)
    if not ConfigRun(step1_cluster_name, ceph_cluster_dict).run_step(steps[1]):
        return output

    kw = {
        "sleep_time": 30,
    }
    sleep(kw=kw)
    output["rc"] = 0
    output["cluster_names"].append(step1_cluster_name)
    return output
