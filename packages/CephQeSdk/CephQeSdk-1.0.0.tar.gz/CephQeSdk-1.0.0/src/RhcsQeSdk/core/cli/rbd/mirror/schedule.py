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


class Schedule:
    """
    This module provides CLI interface to manage the mirror snapshot scheduling.
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " schedule"

    def add_(self, **kw):
        """
        This method is used to create a mirror-snapshot schedule.
        Args:
          kw(dict): Key/value pairs that needs to be provided to the installer
          Example:
            Supported keys:
              pool_name(str): name of the pool.
              image_name(str): name of the image.
              cluster(str): name of the cluster(Optional).
              start_time(str): can be specified using the ISO 8601 time format(Optional).

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        kw_copy = deepcopy(kw)
        image_name = kw_copy.pop("image_name")
        pool_name = kw_copy.pop("pool_name")
        interval = kw_copy.pop("interval")
        cmd_args = core_utils.build_cmd_args(kw=kw_copy)
        cmd = (
            self.base_cmd
            + " add"
            + f" --pool {pool_name} --image {image_name} {interval}"
            + cmd_args
        )
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def ls(self, **kw):
        """
        This method is used to list all snapshot schedules for a specific level (global, pool, or image).
        Args:
          kw(dict): Key/value pairs that needs to be provided to the installer
          Example:
            Supported keys:
              pool_name(str): name of the pool(Optional).
              image_name(str): name of the image(Optional).
              cluster(str): name of the cluster(Optional).
              recursive(bool): set this to true to list all schedules at the specified level and below.

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        cmd_args = core_utils.build_cmd_args(kw=kw)
        cmd = self.base_cmd + " ls" + cmd_args
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def status(self, **kw):
        """
        This method is used to view the status for when the next snapshots will be created for snapshot based mirroring.
        Args:
          kw(dict): Key/value pairs that needs to be provided to the installer
          Example:
            Supported keys:
              pool_name(str): name of the pool(Optional).
              image_name(str): name of the image(Optional).

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        cmd_args = core_utils.build_cmd_args(kw=kw)
        cmd = self.base_cmd + " status" + cmd_args
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def remove_(self, **kw):
        """
        This method is used to remove a mirror-snapshot schedule.
        Args:
          kw(dict): Key/value pairs that needs to be provided to the installer
          Example:
            Supported keys:
              pool_name(str): name of the pool.
              image_name(str): name of the image.
              cluster(str): name of the cluster(Optional).
              start_time(str): can be specified using the ISO 8601 time format(Optional).

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        kw_copy = deepcopy(kw)
        image_name = kw_copy.pop("image_name")
        pool_name = kw_copy.pop("pool_name")
        interval = kw_copy.pop("interval")
        cmd_args = core_utils.build_cmd_args(kw=kw_copy)
        cmd = (
            self.base_cmd
            + " remove"
            + f" --pool {pool_name} --image {image_name} {interval}"
            + cmd_args
        )
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
