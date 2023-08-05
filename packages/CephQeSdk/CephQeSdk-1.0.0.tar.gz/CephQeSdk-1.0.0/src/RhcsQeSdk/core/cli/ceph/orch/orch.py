import logging
from copy import deepcopy

import RhcsQeSdk.core.cli.fabfile as fabfile
from RhcsQeSdk.core.cli.ceph.orch.daemon import Daemon
from RhcsQeSdk.core.cli.ceph.orch.host import Host
from RhcsQeSdk.core.cli.ceph.orch.osd import Osd
from RhcsQeSdk.core.cli.ceph.orch.upgrade import Upgrade
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


class Orch:
    """
    This module provides a command line interface (CLI) to ceph orch.
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " orch"
        self.host = Host(self.base_cmd)
        self.daemon = Daemon(self.base_cmd)
        self.osd = Osd(self.base_cmd)
        self.upgrade = Upgrade(self.base_cmd)

    def status(self, **kw):
        """
        Displays the status of orchestrator.
        Args:
            None
        Returns:
          Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " status"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def ls(self, **kw):
        """
        Lists the status of one of the services running in the Ceph cluster.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              service_type(str): type of service(mon, osd, mgr, mds, rgw)(Optional).
              service_name(str): name of host(Optional).
              export(bool): Whether to export the service specifications knows to the orchestrator(Optional).
              format(str): the type to be formatted(yaml)(Optional).
              refresh(bool): Whether to refresh or not(Optional).
        Returns:
          Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " ls" + core_utils.build_cmd_args(kw=kw)
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def ps(self, **kw):
        """
        Lists daemons known to orchestrator.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              daemon_type(str): type of daemon(mon, osd, mgr, mds, rgw)(Optional).
              daemon_id(int): id of daemon(mon, osd, mgr, mds, rgw)(Optional).
              hostname(str): name of host(Optional).
              service_name(str): name of service(Optional).
              format(str): the type to be formatted(yaml)(Optional).
              refresh(bool): Whether to refresh or not(Optional).
        Returns:
          Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " ps" + core_utils.build_cmd_args(kw=kw)
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def apply(self, **kw):
        """
        Applies the configuration to hosts.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              service-name(str): name of service.
              hosts(list): name of host(Optional).
              placement(dict): Placement on hosts(Optional).
              count(int): No of hosts to be applied(Optional)
        Returns:
          Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        kw_copy = deepcopy(kw)
        service_name = kw_copy.pop("service_name", "")
        cmd = f"{self.base_cmd} apply {service_name}"
        nodes_str = kw_copy.pop("nodes_str", "")
        label = kw_copy.pop("label", "")
        if label:
            cmd = cmd + f" --placement='label:{label}'"
        if nodes_str:
            cmd = cmd + f"{nodes_str}"
        cmd = cmd + core_utils.build_cmd_args(kw=kw_copy)
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def rm(self, **kw):
        """
        Removes a service.
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
        cmd = self.base_cmd + f" rm {service_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def set_(self, **kw):
        """
        Sets/unsets a module to configure as backend.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              Module(str): Module to configure as backend.
        Returns:
          Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        module = kw.get("module") if kw.get("module") else ""
        cmd = self.base_cmd + f" set backend {module}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def start(self, **kw):
        """
        Starts a service.
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
        cmd = self.base_cmd + f" start {service_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def stop(self, **kw):
        """
        Stops a service.
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
        cmd = self.base_cmd + f" stop {service_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def restart(self, **kw):
        """
        Restarts a service.
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

    def reconfig(self, **kw):
        """
        Reconfigs a service.
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
        cmd = self.base_cmd + f" reconfig {service_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def redeploy(self, **kw):
        """
        Redeploys a service.
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
        cmd = self.base_cmd + f" redeploy {service_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
