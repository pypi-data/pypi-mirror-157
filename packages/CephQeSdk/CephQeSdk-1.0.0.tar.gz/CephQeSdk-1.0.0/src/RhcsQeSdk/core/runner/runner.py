import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s"
)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)

file_handler = logging.FileHandler("startup.log", mode="a")
file_handler.setLevel(logging.ERROR)

file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class Runner:
    """Purpose of this module is to provide environment information such as clustername, hosts, nodename, roles etc
    to run ceph cli commands.
    """

    def __init__(
        self,
        cluster_name,
        roles,
        method,
        must_method,
        kwargs,
        ceph_cluster_dict,
        parallel,
        step_output,
        is_root=False,
        env_config=None,
    ):
        self.step_output = step_output
        self.ceph_cluster_dict = ceph_cluster_dict
        self.method = method
        self.kwargs = kwargs
        self.roles = roles
        self.parallel = parallel
        if not self.roles:
            self.roles = ["client"]
        self.must_method = must_method
        self.cluster_name = cluster_name
        ips = []
        for role in roles:
            if len(role.split(":")) == 2:
                cluster_and_role = role.split(":")
                cluster_name = cluster_and_role[0]
                role = cluster_and_role[1]
            else:
                cluster_name = self.cluster_name
                role = role
            nodes = ceph_cluster_dict[cluster_name].get_nodes(role)
            for node in nodes:
                ips.append(node.ip_address)
        self.hosts = ips
        self.cluster_name = cluster_name
        self.is_root = is_root
        self.env_config = env_config
        self.set_environment_for_run()

    def set_environment_for_run(self):
        """
        Sets environment variables to run a command through fabfile.
        Args:
            None

        Returns:
            None
        """
        if not self.env_config:
            self.env_config = {
                "hosts": self.hosts,
                "username": "cephuser",
                "password": "cephuser",
                "parallel": self.parallel,
            }
        if self.is_root:
            self.env_config["username"] = "root"
            self.env_config["password"] = "passwd"

    def run(self):
        """
        Runs a command in must methods[must_pass | must_fail | must_raise].
        Args:
            None

        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        out = self.must_method(
            function=self.method,
            kw_args=self.kwargs,
            env_config=self.env_config,
            cluster_name=self.cluster_name,
            step_output=self.step_output,
        )
        return out
