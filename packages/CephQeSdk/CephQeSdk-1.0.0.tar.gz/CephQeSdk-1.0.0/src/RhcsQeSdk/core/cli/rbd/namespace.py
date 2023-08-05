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


class Namespace:

    """
    This Class provides wrappers for rbd namespace commands.
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " namespace"

    def create(self, **kw):
        """Wrapper for rbd namespace create.

        Create an rbd image namespace inside specified pool.
        Args:
        kw: Key value pair of method arguments
            Example::
            Supported keys:
                pool_spec(str): pool specification <pool-name>[/<namespace>]
                namespace(str): name of the namespace
                pool(str): pool name
        Returns:
            Dict(str):
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")

        kw_copy = deepcopy(kw)
        pool_spec = kw_copy.pop("pool_spec", "")
        cmd_args = core_utils.build_cmd_args(kw=kw_copy)

        cmd = f"{self.base_cmd} create {pool_spec}{cmd_args}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def list_(self, **kw):
        """Wrapper for rbd namespace list.

        List RBD image namespaces.
        Args:
        kw: Key value pair of method arguments
            Example::
            Supported keys:
                pool_spec(str): pool specification.
                pool(str): pool name
                format(str): output format (plain, json, or xml) [default: plain]
                pretty-format(bool): True
        Returns:
            Dict(str):
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")

        kw_copy = deepcopy(kw)
        pool_spec = kw_copy.pop("pool_spec", "")
        cmd_args = core_utils.build_cmd_args(kw=kw_copy)

        cmd = f"{self.base_cmd} list {pool_spec}{cmd_args}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def remove_(self, **kw):
        """Wrapper for rbd namespace remove.

        Remove an RBD image namespace.
        Args:
        kw: Key value pair of method arguments
            Example::
            Supported keys:
                pool_spec(str): pool specification <pool-name>[/<namespace>]
                namespace(str): name of the namespace
                pool(str): pool name
        Returns:
            Dict(str):
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")

        kw_copy = deepcopy(kw)
        pool_spec = kw_copy.pop("pool_spec", "")
        cmd_args = core_utils.build_cmd_args(kw=kw_copy)

        cmd = f"{self.base_cmd} remove {pool_spec}{cmd_args}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
