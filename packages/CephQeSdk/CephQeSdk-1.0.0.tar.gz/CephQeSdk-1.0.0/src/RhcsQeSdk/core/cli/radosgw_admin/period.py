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


class Period:
    """
    This module provides CLI interface for period management for object gateway service.
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " period"

    def rm(self, **kw):
        """
        This method is used to remove a period.
        Args:
          period(str) : Period Id of a specific period.

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        period_id = kw.get("period")
        cmd = self.base_cmd + f" rm --period={period_id}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def get_(self, **kw):
        """
        This method is used to get the info of specific period.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              period(str) : Period Id of a specific period.

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        period_id = kw.get("period")
        cmd = self.base_cmd + f" get --period={period_id}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def get_current(self, **kw):
        """
        This method is used to get the current period info.
        Args:
          None

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " get-current"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def pull(self, **kw):
        """
        This method is used to pull a period.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              url(str) : url to the master zone.
              access-key(str) : The secondary zones will require them to authenticate with the master zone.
              secret-key(str): The secondary zones will require them to authenticate with the master zone.

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        url = kw.get("url")
        access_key = kw.get("access-key")
        secret_key = kw.get("secret-key")
        cmd = (
            self.base_cmd
            + f" pull --url={url} --access-key={access_key} --secret={secret_key}"
        )
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def push(self, **kw):
        """
        This method is used to push a period.
        Args:
          None

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " push"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def list_(self, **kw):
        """
        This method is used to list all periods.
        Args:
          None

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " list"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def update_(self, **kw):
        """
        This method is used to update the staging period.
        Args:
          None

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " update"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def commit(self, **kw):
        """
        This method is used to commit the staging period.
        Args:
          rgw-realm(str): Takes the realm name as input.

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        rgw_realm = kw.get("rgw-realm")
        cmd = self.base_cmd + f" update --rgw-realm={rgw_realm} --commit"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
