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


class Role:
    """
    This module provides CLI interface to manage role operations.
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " role"

    def create(self, **kw):
        """Create a new AWS role for use with STS.
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
                role-name(str): takes name of the role
                path(str): path to role. The default value is a slash(/).(optioal)
                assume-role-policy-doc(str): The trust relationship policy document that grants an
                                             entity permission to assume the role.(optional)
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        kw_copy = deepcopy(kw)
        role_name = kw_copy.pop("role-name", "")
        cmd = (
            self.base_cmd
            + f" create --role-name={role_name}"
            + core_utils.build_cmd_args(kw=kw_copy)
        )
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def rm(self, **kw):
        """Remove a role.
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
                role-name(str): takes name of the role
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        role_name = kw.get("role-name")
        cmd = self.base_cmd + f" rm --role-name={role_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def get_(self, **kw):
        """Get a role.
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
                role-name(str): takes name of the role
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        role_name = kw.get("role-name")
        cmd = self.base_cmd + f" get --role-name={role_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def list_(self, **kw):
        """List the roles with specified path prefix.
        Args:
          kw(dict): Key/value pairs that needs to be provided to the installer
          Example:
          Supported keys:
                path-prefix(str): Path prefix for filtering roles. If this is not specified,
                                  all roles are listed.(optional)
        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " list" + core_utils.build_cmd_args(kw=kw)
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def modify(self, **kw):
        """Modify the assume role policy of an existing role.
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
                role-name(str): takes name of the role
                assume-role-policy-doc(str): The trust relationship policy document that grants an
                                             entity permission to assume the role.
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        role_name = kw.get("role-name")
        trust_policy_document = kw.get("assume-role-policy-doc")
        cmd = (
            self.base_cmd
            + f" modify --role-name={role_name} --assume-role-policy-doc={trust_policy_document}"
        )
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
