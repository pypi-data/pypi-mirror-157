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


class ErasureCodeProfile:
    """
    Subcommand erasure-code-profile is used for managing the erasure code profiles.
    It uses some additional subcommands.
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " erasure_code_profile"

    def get_(self, **kw):
        """
        Subcommand get gets erasure code profile <name>.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
                name(str)          :  erasure code profile name

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        name = kw.get("name")
        cmd = f"{self.base_cmd} get {name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def ls(self, **kw):
        """
        Subcommand ls lists all erasure code profiles.

        Args:
            None

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd = f"{self.base_cmd} ls"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def rm(self, **kw):
        """
        Subcommand rm removes erasure code profile <name>.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
                name(str)          :  erasure code profile name

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        name = kw.get("name")
        cmd = f"{self.base_cmd} rm {name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def set_(self, **kw):
        """
        Subcommand set creates erasure code profile <name> with [<key[=value]> …] pairs.
        Add a –force at the end to override an existing profile (IT IS RISKY).

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
                name(str)          :  erasure code profile name
                profile_list(list) :  list of profiles
                force(boolean)     :  True or False

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        kw_copy = deepcopy(kw)
        name = kw_copy.pop("name", "")
        profile_list = kw_copy.pop("profile_list", "")
        profile_str = " ".join(profile_list)
        cmd = f"{self.base_cmd} set {name} {profile_str}"
        cmd_args = core_utils.build_cmd_args(kw=kw_copy)
        cmd = cmd + cmd_args
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
