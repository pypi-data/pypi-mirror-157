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


class Mon:
    """
    This module provides CLI interface for the management of monitor configuration and administration.
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " mon"

    def add_(self, **kw):
        """
        This method is used to add new monitor named with a specified name at a specified address.
        Args:
          kw(Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported Keys:
              name(str) : Name of the monitor.
              addr(str) : IP Address (Host) on which Monitor daemon to be deployed.

        Returns:
          Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        name = kw.get("name")
        addr = kw.get("addr")
        cmd = self.base_cmd + f" add {name} {addr}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def dump(self, **kw):
        """
        This method is used to dump the formatted monmap.
        Args:
          None

        Returns:
          Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.

        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " dump"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def getmap(self, **kw):
        """
        This method is used to get the monmap.
        Args:
          kw(Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported Keys:
              MONMAP(str): This key is used to store the path of monmap.

        Returns:
          Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        monmap = kw.get("MONMAP")
        cmd = self.base_cmd + f" getmap -o {monmap}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def remove_(self, **kw):
        """
        This method is used to remove monitor.
        Args:
          kw(Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported Keys:
              name(str) : Name of the monitor.

        Returns:
          Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        name = kw.get("name")
        cmd = self.base_cmd + f" remove {name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def stat(self, **kw):
        """
        This method is used to summarize the monitor status.
        Args:
          None

        Returns:
          Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " stat"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
