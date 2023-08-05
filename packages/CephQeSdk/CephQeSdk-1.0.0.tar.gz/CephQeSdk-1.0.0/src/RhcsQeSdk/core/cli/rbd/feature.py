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


class Feature:
    """
    This module provides CLI interface to manage enabling and disabling image features.
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " feature"

    def enable(self, **kw):
        """
        This method is used to enable a image feature.
        Args:
          kw(dict): Key/value pairs that needs to be provided to the installer
          Example:
            Supported keys:
              pool_name(str): name of the pool.
              image_name(str): name of the image.
              feature_name(str): name of the feature.

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        image_name = kw.get("image_name")
        pool_name = kw.get("pool_name")
        feature_name = kw.get("feature_name")
        cmd = self.base_cmd + " enable" + f" {pool_name}/{image_name} {feature_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def disable(self, **kw):
        """
        This method is used to disable a image feature.
        Args:
          kw(dict): Key/value pairs that needs to be provided to the installer
          Example:
            Supported keys:
              pool_name(str): name of the pool.
              image_name(str): name of the image.
              feature_name(str): name of the feature.

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        image_name = kw.get("image_name")
        pool_name = kw.get("pool_name")
        feature_name = kw.get("feature_name")
        cmd = self.base_cmd + " disable" + f" {pool_name}/{image_name} {feature_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
