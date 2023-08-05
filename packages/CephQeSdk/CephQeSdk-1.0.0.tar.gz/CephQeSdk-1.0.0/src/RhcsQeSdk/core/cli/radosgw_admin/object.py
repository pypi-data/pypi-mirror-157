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


class Object:
    """
    This module provides CLI interface to manage object operations for radosgw-admin.
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " object"

    def rm(self, **kw):
        """Remove an object from a bucket.
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
                object(str): takes name of the object
                bucket(str): takes name of the bucket
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        object_name = kw.get("object")
        bucket_name = kw.get("bucket")
        cmd = self.base_cmd + f" rm --object={object_name} --bucket={bucket_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def stat(self, **kw):
        """Stat an object for its metadata.
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
                object(str): takes name of the object
                bucket(str): takes name of the bucket
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        object_name = kw.get("object")
        bucket_name = kw.get("bucket")
        cmd = self.base_cmd + f" stat --bucket={bucket_name} --object={object_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def unlink(self, **kw):
        """Unlink object from bucket index.
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
                object(str): takes name of the object
                bucket(str): takes name of the bucket
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        object_name = kw.get("object")
        bucket_name = kw.get("bucket")
        cmd = self.base_cmd + f" unlink --bucket={bucket_name} --object={object_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def rewrite(self, **kw):
        """Rewrite the specified object.
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
                object(str): takes name of the object
                bucket(str): takes name of the bucket
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        object_name = kw.get("object")
        bucket_name = kw.get("bucket")
        cmd = self.base_cmd + f" rewrite --bucket={bucket_name} --object={object_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def expire_stale(self, **kw):
        """Run expired objects cleanup.
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
        self.base_cmd = self.base_cmd + "s"
        bucket_name = kw.get("bucket")
        if kw.get("list"):
            cmd = self.base_cmd + f" expire-stale list --bucket {bucket_name}"
        elif kw.get("rm"):
            cmd = self.base_cmd + f" expire-stale rm --bucket {bucket_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
