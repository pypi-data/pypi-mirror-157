import logging

import RhcsQeSdk.core.cli.fabfile as fabfile
from RhcsQeSdk.core.cli.ceph.auth import Auth
from RhcsQeSdk.core.cli.ceph.balancer import Balancer
from RhcsQeSdk.core.cli.ceph.cephadm import CephAdm
from RhcsQeSdk.core.cli.ceph.config import Config
from RhcsQeSdk.core.cli.ceph.config_key import ConfigKey
from RhcsQeSdk.core.cli.ceph.health import Health
from RhcsQeSdk.core.cli.ceph.mds import Mds
from RhcsQeSdk.core.cli.ceph.mgr import Mgr
from RhcsQeSdk.core.cli.ceph.mon import Mon
from RhcsQeSdk.core.cli.ceph.orch.orch import Orch
from RhcsQeSdk.core.cli.ceph.osd import Osd

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s"
)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)


class Ceph:
    """This module provides CLI interface for deployment and maintenance of ceph cluster."""

    def __init__(self, base_cmd=""):
        self.base_cmd = f"{base_cmd}ceph"
        self.config = Config(self.base_cmd)
        self.osd = Osd(self.base_cmd)
        self.auth = Auth(self.base_cmd)
        self.cephadm = CephAdm(self.base_cmd)
        self.orch = Orch(self.base_cmd)
        self.health = Health(self.base_cmd)
        self.balancer = Balancer(self.base_cmd)
        self.configkey = ConfigKey(self.base_cmd)
        self.mds = Mds(self.base_cmd)
        self.mon = Mon(self.base_cmd)
        self.mgr = Mgr(self.base_cmd)

    def version(self, **kw):
        """
        The command version will display the mon daemon version.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:

            None

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " version"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def status(self, **kw):
        """
        This method is used to show cluster status.
        Args:
          None
        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " status"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def quorum_status(self, **kw):
        """
        This method is used to report the status of monitor quorum.
        Args:
          None
        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " quorum_status"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def daemon(self, **kw):
        """Submit admin-socket commands.
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
                daemon-name(str): takes name of the daemon
                path-to-socket-file(str): takes path to the socket file
                command(str): takes input the command
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        daemon_name = kw.get("daemon-name", "")
        path_to_socket_file = kw.get("path-to-socket-file", "")
        command = kw.get("command", "")
        cmd = self.base_cmd + f" daemon {daemon_name}{path_to_socket_file} {command}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def log(self, **kw):
        """Log supplied text to the monitor log.
        Args:
            kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
                logtext(str): takes the logtext
                command(str): takes input the command
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        logtext = kw.get("logtext", "")
        command = kw.get("command", "")
        cmd = self.base_cmd + f" log {command} [{logtext}]"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def df(self, **kw):
        """
        The command df will display the cluster's free space status.
        Args:
            detail(str): to show more information about the cluster.
        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " df" + (" detail" if kw.get("detail") else "")
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
