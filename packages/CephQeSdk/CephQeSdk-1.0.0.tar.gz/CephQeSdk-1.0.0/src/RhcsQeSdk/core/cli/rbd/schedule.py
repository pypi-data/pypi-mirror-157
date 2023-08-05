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
    This module provides CLI interface to rbd trash purge schedule commands.
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " schedule"

    def add_(self, **kw):
        """Wrapper for rbd trash purge schedule add.

        Add trash purge schedule.
        Args:
        kw: Key value pair of method arguments
            Example::
            Supported keys:
                pool(str): pool name
                namespace(str): name of the namespace
                interval(str): schedule interval
                start-time: optional schedule start time
        Returns:
            Dict(str):
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")

        kw_copy = deepcopy(kw)
        interval = kw_copy.pop("interval", "")
        start_time = kw_copy.pop("start-time", "")
        cmd_args = core_utils.build_cmd_args(kw=kw_copy)

        cmd = f"{self.base_cmd} add {interval} {start_time}{cmd_args}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def ls(self, **kw):
        """Wrapper for rbd trash purge schedule ls.

        List trash purge schedule.
        Args:
        kw: Key value pair of method arguments
            Example::
            Supported keys:
                pool(str): pool name.
                namespace(str): name of the namespace.
                recursive(bool): list all schedules.
                format(str): output format (plain, json, or xml) [default: plain]
                pretty-format(bool): True
        Returns:
            Dict(str):
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd_args = core_utils.build_cmd_args(kw=kw)

        cmd = f"{self.base_cmd} ls{cmd_args}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def rm(self, **kw):
        """Wrapper for rbd trash purge schedule rm.

        Remove trash purge schedule.
        Args:
        kw: Key value pair of method arguments
            Example::
            Supported keys:
                pool(str): pool name.
                namespace(str): name of the namespace.
                interval(str): schedule interval
                start-time: optional schedule start time
        Returns:
            Dict(str):
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")

        kw_copy = deepcopy(kw)
        interval = kw_copy.pop("interval", "")
        start_time = kw_copy.pop("start-time", "")
        cmd_args = core_utils.build_cmd_args(kw=kw_copy)

        cmd = f"{self.base_cmd} rm {interval} {start_time}{cmd_args}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def status(self, **kw):
        """Wrapper for rbd trash purge schedule status.

        Show trash purge schedule status.
        Args:
        kw: Key value pair of method arguments
            Example::
            Supported keys:
                pool(str): pool name.
                namespace(str): name of the namespace.
                format(str): output format (plain, json, or xml) [default: plain]
                pretty-format(bool): True
        Returns:
            Dict(str):
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd_args = core_utils.build_cmd_args(kw=kw)

        cmd = f"{self.base_cmd} status{cmd_args}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
