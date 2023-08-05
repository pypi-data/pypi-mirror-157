import re


class RedefineArgs:
    def __init__(self):
        pass

    def get_args(self, **kw):
        kw = kw.get("kw")
        step = kw.get("step")
        cls = step.get("class").lower()
        method = step.get("method").lower()
        component = step.get("component").lower()
        redefine_method_name = f"{component}_{cls}_{method}"
        args = step.get("args")
        redefine_method = getattr(self, redefine_method_name, None)
        if redefine_method:
            args = redefine_method(kw=kw)
        return args

    def cephadm_cephadm_bootstrap(self, **kw):
        kw = kw.get("kw")
        step = kw.get("step")
        cluster_name = kw.get("cluster_name")
        ceph_cluster_dict = kw.get("ceph_cluster_dict")
        args = step.get("args")
        if args.get("registry-url"):
            args["registry-username"] = "qa@redhat.com"
            args["registry-password"] = "MTQj5t3n5K86p3gH"
        if args.get("mon-ip"):
            ips = [
                ceph_cluster_dict[cluster_name].get_nodes(args.get("mon-ip")).ip_address
            ]
        else:
            ips = []
            nodes = ceph_cluster_dict[cluster_name].get_nodes("mon")
            for node in nodes:
                ips.append(node.ip_address)
        args["mon-ip"] = " ".join(ips)
        return args

    def ceph_orch_apply(self, **kw):
        kw = kw.get("kw")
        step = kw.get("step")
        args = step.get("args")
        service_name = args.get("service_name")
        placement = args.pop("placement", {})
        cluster_name = kw.get("cluster_name")
        ceph_cluster_dict = kw.get("ceph_cluster_dict")
        if placement:
            if "label" in placement:
                args["label"] = placement["label"]
            if "nodes" in placement:
                sep = placement.get("sep", " ")
                nodes = placement.get("nodes", {})
                nodes_list = []
                for node in nodes:
                    for ceph_node in ceph_cluster_dict[cluster_name].get_nodes():
                        searches = re.findall(
                            rf"{node}?\d*", ceph_node.hostname, re.IGNORECASE
                        )
                        for ele in searches:
                            if ele == node:
                                nodes_list.append(ceph_node.hostname)
                nodes_str = f"{sep}".join(nodes_list)
                count = placement.get("count", "")
                if service_name == "rgw" and placement.get("count-per-host", ""):
                    count = placement.get("count-per-host", None)
                nodes_str = f"{count}{sep}{nodes_str}"
                args["nodes_str"] = nodes_str
        return args

    def ceph_host_add(self, **kw):
        kw = kw.get("kw")
        cluster_name = kw.get("cluster_name")
        ceph_cluster_dict = kw.get("ceph_cluster_dict")
        step = kw.get("step")
        args = step.get("args")
        hosts = args.pop("host_name", {})
        for node in ceph_cluster_dict[cluster_name].get_nodes():
            searches = re.findall(rf"{hosts}?\d*", node.hostname, re.IGNORECASE)
            for ele in searches:
                if ele == hosts:
                    hosts = node.hostname
        host_string = ""
        ip_address = [
            ceph_cluster_dict[cluster_name].get_node_by_hostname(hosts).ip_address
        ]
        ip_address = "".join(ip_address)
        host_string = host_string + f"{hosts} {ip_address}"
        args["host_string"] = host_string
        return args

    def ceph_label_add(self, **kw):
        kw = kw.get("kw")
        cluster_name = kw.get("cluster_name")
        ceph_cluster_dict = kw.get("ceph_cluster_dict")
        step = kw.get("step")
        args = step.get("args")
        hosts = args.pop("host_name", {})
        for node in ceph_cluster_dict[cluster_name].get_nodes():
            searches = re.findall(rf"{hosts}?\d*", node.hostname, re.IGNORECASE)
            for ele in searches:
                if ele == hosts:
                    args["hosts"] = node.hostname
        return args
