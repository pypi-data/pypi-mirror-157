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


class Application:
    """This module provides CLI interface to add annotation to a pool via ceph osd pool application."""

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " application"

    def disable(self, **kw):
        """
        The disable command will disable a client application from conducting I/O operations on a pool.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:

                pool_name(str): name of the pool.
                app(str): component of ceph (cephfs, rgw, rbd).
                yes-i-really-mean-it(bool): whether to disable or not(Optional)

        Returns:
            Dict(str):
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        pool_name = kw.get("pool_name", "ceph")
        app = kw.get("app", "")
        ending = kw.get("--yes-i-really-mean-it", "")
        cmd = f"{self.base_cmd} disable {pool_name} {app} {ending}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def set_(self, **kw):
        """
        To set client application metadata on a pool.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:

                pool_name(str): name of the pool.
                app(str): component of ceph (cephfs, rbd, rgw).
                key(Union[str,int]): name of the property of an osd pool.
                value(Union[str,int]): value to be set against the key.

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        pool_name = kw.get("pool_name", "ceph")
        app = kw.get("app", "")
        key = kw.get("key", None)
        value = kw.get("value", None)
        cmd = f"{self.base_cmd} set {pool_name} {app} {key} {value}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def rm(self, **kw):
        """
        Removes the key-value pair for the given key in the given application of the
        given pool.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:

                pool_name(str): name of the pool.
                app(str): component of ceph (cephfs, rbd, rgw).
                key(Union[str,int]): name of the property of an osd pool.

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        pool_name = kw.get("pool_name", "ceph")
        app = kw.get("app", "")
        key = kw.get("key", None)
        cmd = f"{self.base_cmd} rm {pool_name} {app} {key}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def get_(self, **kw):
        """
        Displays the value for the given key that is associated with the given
        application of the given pool.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:

                pool_name(str): name of the pool.
                app(str): component of ceph (cephfs, rbd, rgw).
                key(Union[str,int]): name of the property of an osd pool.

        Returns:
            Dict(str):
            A mappping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        pool_name = kw.get("pool_name", "ceph")
        app = kw.get("app", "")
        key = kw.get("key", None)
        cmd = f"{self.base_cmd} get {pool_name} {app} {key}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def enable(self, **kw):
        """
        The enable command will enable a client application to conduct I/O operations on a pool.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:

                pool_name(str): name of the pool.
                app(str): component of ceph (cephfs, rgw, rbd).
                yes-i-really-mean-it(bool): whether to disable or not(Optional)

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for taht host's execution run.
        """
        kw = kw.get("kw")
        pool_name = kw.get("pool_name", "ceph")
        app = kw.get("app", "")
        ending = kw.get("yes-i-really-mean-it", "")
        cmd = f"{self.base_cmd} enable {pool_name} {app} {ending}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
