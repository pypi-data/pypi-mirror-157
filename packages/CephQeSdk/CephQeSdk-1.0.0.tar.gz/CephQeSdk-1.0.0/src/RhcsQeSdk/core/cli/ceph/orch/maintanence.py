import logging
from copy import deepcopy

import RhcsQeSdk.core.cli.fabfile as fabfile
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


class Maintanence:
    """
    This module provides a command line interface (CLI) to ceph orch host maintanence modules.
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " maintanence"

    def enter(self, **kw):
        """
        To place a host in maintanence mode.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
                host_name(str): name of host.
                force(bool): Whether its a forced operation or not(Optional).
        Returns:
          Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        kw_copy = deepcopy(kw)
        host_name = kw_copy.get("host_name")
        cmd = (
            self.base_cmd
            + f" enter {host_name}"
            + core_utils.build_cmd_args(kw=kw_copy)
        )
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def exit(self, **kw):
        """
        To unset a host in maintanence mode.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
                host_name(str): name of host.
        Returns:
          Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        host_name = kw.get("host_name")
        cmd = self.base_cmd + f" exit {host_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
