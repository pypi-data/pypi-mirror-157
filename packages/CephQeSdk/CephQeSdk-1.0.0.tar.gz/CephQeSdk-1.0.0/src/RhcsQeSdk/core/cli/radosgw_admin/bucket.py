import logging

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


class Bucket:
    """This module provides CLI interface to manage bucket operations."""

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " bucket"

    def list_(self, **kw):
        """List buckets, or, if bucket specified with --bucket=<bucket>, list its objects.
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
                bucket(str): takes name of the bucket(optional)
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " list" + core_utils.build_cmd_args(kw=kw)
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def limit_check(self, **kw):
        """Show bucket sharding stats.
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
                warnings-only(bool):  When specified, list only buckets nearing or over
                                                the current max objects per shard value.
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " limit check" + core_utils.build_cmd_args(kw=kw)
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def link(self, **kw):
        """Link bucket to specified user, if --bucket-new-name=<new-name>
        is specified then this command is used for renaming the bucket.
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
                bucket(str): takes name of the bucket
                bucket-new-name(str): takes new name of bucket(optional)
                uid(str):  takes the user-id
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " link" + core_utils.build_cmd_args(kw=kw)
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def unlink(self, **kw):
        """Unlink bucket from specified user.
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
                bucket(str): takes name of the bucket
                uid(str):  takes the user-id
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")

        uid = kw.get("uid")
        bucket_name = kw.get("bucket")
        cmd = self.base_cmd + f" unlink --bucket={bucket_name} --uid={uid}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def chown(self, **kw):
        """Change the ownership of the bucket to the new user.
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
                bucket(str): takes name of the bucket
                uid(str):  takes the user-id
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        uid = kw.get("uid")
        bucket_name = kw.get("bucket")
        cmd = self.base_cmd + f" chown --bucket={bucket_name} --uid={uid}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def stats(self, **kw):
        """Returns statistics of a specified bucket.
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
        cmd = self.base_cmd + f" stats --bucket={bucket_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def rm(self, **kw):
        """Remove a specified bucket.
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
                bucket(str): takes name of the bucket
                purge-objects(bool): When specified, the bucket removal will also purge all objects in it.
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " rm" + core_utils.build_cmd_args(kw=kw)
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def check(self, **kw):
        """Check bucket index.
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
                check-objects(bool): Rebuilds bucket index according to actual objects state.
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " check" + core_utils.build_cmd_args(kw=kw)
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def rewrite(self, **kw):
        """Rewrite all objects in the specified bucket.
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
        cmd = self.base_cmd + f" rewrite --bucket={bucket_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def radoslist(self, **kw):
        """List the rados objects that contain the data for all objects
        is the designated bucket, if –bucket=<bucket> is specified,
        or otherwise all buckets.
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
                bucket(str): takes name of the bucket(optional)
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " radoslist" + core_utils.build_cmd_args(kw=kw)
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def reshard(self, **kw):
        """Reshard a bucket.
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
                bucket(str): takes name of the bucket(optional)
                num-shards(int):  takes no. of shards
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        num_shard = kw.get("num-shards")
        bucket_name = kw.get("bucket")
        cmd = (
            self.base_cmd + f" reshard --bucket={bucket_name} --num-shards={num_shard}"
        )
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def sync_enable(self, **kw):
        """Enable bucket sync.
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
        cmd = self.base_cmd + f" sync enable --bucket={bucket_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def sync_disable(self, **kw):
        """Disable bucket sync.
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
        cmd = self.base_cmd + f" sync disable --bucket={bucket_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
