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


class Bi:
    """
    This module provides CLI interface to manage bucket index operations.
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " bi"

    def list_(self, **kw):
        """List raw bucket index entries.
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
                bucket(str): takes name of the bucket
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        bucket_name = kw.get("bucket")
        cmd = (
            self.base_cmd + f" list --bucket={bucket_name} > {bucket_name}.list.backup"
        )
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def purge(self, **kw):
        """Purge bucket index entries.
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
                bucket(str): takes name of the bucket
                bucket-id(str): takes old bucket ID
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        bucket_name = kw.get("bucket")
        old_bucket_id = kw.get("bucket-id")
        cmd = (
            self.base_cmd + f" purge --bucket={bucket_name} --bucket-id={old_bucket_id}"
        )
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
