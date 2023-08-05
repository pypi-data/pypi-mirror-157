import logging

import RhcsQeSdk.core.cli.fabfile as fabfile

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s"
)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)


class Daemon:
    """
    This module provides a command line interface (CLI) to ceph orch daemon modules.
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " daemon"

    def add_(self, **kw):
        """
        Deploys daemons based on provided placement specification.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              service_name(str): name of service.
              placement(str): name of host to be deployed into.
        Returns:
          Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        service_name = kw.get("service_name")
        placement = kw.get("placement")
        cmd = self.base_cmd + f" add {service_name} --placement={placement}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def rm(self, **kw):
        """
        Removes a daemon from host.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              service_name(str): name of service.
              placement(str): name of host to be removed from.
        Returns:
          Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        service_name = kw.get("service_name")
        placement = kw.get("placement")
        cmd = self.base_cmd + f" rm {service_name} --placement={placement}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def restart(self, **kw):
        """
        Restarts a daemon on host.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              service_name(str): name of service.
        Returns:
          Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        service_name = kw.get("service_name")
        cmd = self.base_cmd + f" restart {service_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
