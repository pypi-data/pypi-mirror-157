import logging
from copy import deepcopy

import RhcsQeSdk.core.cli.fabfile as fabfile
from RhcsQeSdk.core.cli.ceph.orch.label import Label
from RhcsQeSdk.core.cli.ceph.orch.maintanence import Maintanence
from RhcsQeSdk.core.utilities import core_utils

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s"
)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)


class Host:
    """
    This module provides a command line interface (CLI) to ceph orch host.
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " host"
        self.label = Label(self.base_cmd)
        self.maintanence = Maintanence(self.base_cmd)

    def ls(self, **kw):
        """
        Displays the current hosts and labels.
        Args:
            None
        Returns:
          Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " ls"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def add_(self, **kw):
        """
        To add new hosts to cluster.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
                host_name(str): name of host.
                labels(str): name of label.(Optional).
                ip_address(str): Ipaddress of host.

        Returns:
          Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        kw_copy = deepcopy(kw)
        host_string = kw_copy.pop("host_string")
        cmd_args = core_utils.build_cmd_args(kw=kw_copy)
        cmd = self.base_cmd + f" add {host_string}" + cmd_args
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def drain(self, **kw):
        """
        To drain all daemons from specified host.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
                host_name(str): name of host.
                force(bool): force drain.
        Returns:
          Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        host_name = kw.get("host_name", "")
        force = "--force" if kw.get("force") else ""
        cmd = self.base_cmd + f" drain {host_name} {force}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def rm(self, **kw):
        """
        To remove host.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
                host_name(str): name of host.
                force(bool): Whether its a forced operation or not(Optional).
                offline(bool): if a host is offline(Optional).

        Returns:
          Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        kw_copy = deepcopy(kw)
        host_name = kw_copy.pop("host_name", "")
        cmd = self.base_cmd + f" rm {host_name}" + core_utils.build_cmd_args(kw=kw_copy)
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
