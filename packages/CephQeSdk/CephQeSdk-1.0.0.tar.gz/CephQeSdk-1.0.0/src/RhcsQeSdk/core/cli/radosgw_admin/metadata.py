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


class Metadata:
    """
    This module provides CLI interface for commands via radosgw-admin metadata.
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " metadata"

    def get_(self, **kw):
        """Get metadata info.
        Args:
                bucket(str) :  Holds a mapping between bucket name and bucket instance id.
                bucket.instance(str) : Holds bucket instance information.
                user(str) : Holds user information.
                key(str) : Holds Metadata key
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        cmd = self.base_cmd + " get"
        kw = kw.get("kw")
        bucket = kw.get("bucket", "")
        bucket_instance = kw.get("bucket.instance", "")
        user = kw.get("user", "")
        metadata_key = kw.get("key", "")
        if bucket:
            cmd = cmd + f" bucket:{bucket}"
        elif bucket_instance:
            cmd = cmd + f" bucket.instance:{bucket_instance}"
        elif user:
            cmd = cmd + f" user:{user}"
        elif metadata_key:
            cmd = cmd + f" --metadata-key={metadata_key}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def put_(self, **kw):
        """Put metadata info.
        Args:
                user-id(str) : User ID
                bucket-id(str) : Bucket ID
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        cmd = self.base_cmd + " put"
        kw = kw.get("kw")
        user_id = kw.get("user-id", "")
        bucket_id = kw.get("bucket-id", "")
        if user_id:
            cmd = cmd + f" user:{user_id}"
        elif bucket_id:
            cmd = cmd + f" bucket:{bucket_id}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def rm(self, **kw):
        """Remove metadata info.
        Args:
                bucket(str) :  Holds a mapping between bucket name and bucket instance id.
                bucket.instance(str) : Holds bucket instance information.
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        cmd = self.base_cmd + " rm"
        kw = kw.get("kw")
        bucket = kw.get("bucket", "")
        bucket_instance = kw.get("bucket.instance", "")
        if bucket:
            cmd = cmd + f" bucket:{bucket}"
        elif bucket_instance:
            cmd = cmd + f" bucket.instance:{bucket_instance}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def list_(self, **kw):
        """List metadata info.
        Args:
                option(str) : bucket | bucket.instance | user
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        option = kw.get("option", "")
        cmd = self.base_cmd + " list" + f" {option}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
