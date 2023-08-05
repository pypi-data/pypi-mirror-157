import logging
from copy import deepcopy

import RhcsQeSdk.core.cli.fabfile as fabfile
from RhcsQeSdk.core.cli.rbd.purge import Purge
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


class Trash:
    """This module provides CLI interface to manage block device images from/in trash."""

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " trash"
        self.purge = Purge(self.base_cmd)

    def mv(self, **kw):
        """
        Moves an image to the trash.
        Args:
            kw(dict): Key/value pairs that needs to be provided to the installer
            Example::
            Supported keys:
                image_name(str) :  name of image to be moved to trash
                pool_name(str)  : name of the pool
                expires_at(str) : Expiration time to defer the image (optional)
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        kw_copy = deepcopy(kw)
        image_name = kw_copy.pop("image_name", "")
        pool_name = kw_copy.pop("pool_name", "")
        cmd = (
            self.base_cmd
            + f" mv {pool_name}/{image_name}"
            + core_utils.build_cmd_args(kw=kw_copy)
        )
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def rm(self, **kw):
        """
        Removes an image from the trash.
        Args:
            kw(dict): Key/value pairs that needs to be provided to the installer
            Example::
            Supported keys:
                image_id(int)  :  id of image to be removed from trash
                pool_name(str) : name of the pool
                force(bool)    :  To determine whether its a forced operation or not(optional)
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        kw_copy = deepcopy(kw)
        image_id = kw_copy.pop("image_id", "")
        pool_name = kw_copy.pop("pool_name", "")
        cmd = (
            self.base_cmd
            + f" rm {pool_name}/{image_id}"
            + core_utils.build_cmd_args(kw=kw_copy)
        )
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def restore(self, **kw):
        """
        Restores an image from the trash.
        Args:
            kw(dict): Key/value pairs that needs to be provided to the installer
            Example::
            Supported keys:
                image_id(int) :  id of image to be restored from trash
                pool_name(str) : name of the pool
                image(int) :  name of image to be renamed(Optional)
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        kw_copy = deepcopy(kw)
        image_id = kw_copy.pop("image_id", "")
        pool_name = kw_copy.pop("pool_name", "")
        cmd = (
            self.base_cmd
            + f" restore {pool_name}/{image_id}"
            + core_utils.build_cmd_args(kw=kw_copy)
        )
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def ls(self, **kw):
        """
        Lists imageids from the trash.
        Args:
            kw(dict): Key/value pairs that needs to be provided to the installer
            Example::
            Supported keys:
                pool_name(str) : name of the pool
                all(bool) : whether to list all trashed images(Optional)
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        kw_copy = deepcopy(kw)
        pool_name = kw_copy.pop("pool_name", "")
        cmd = self.base_cmd + f" ls {pool_name}" + core_utils.build_cmd_args(kw=kw_copy)
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
