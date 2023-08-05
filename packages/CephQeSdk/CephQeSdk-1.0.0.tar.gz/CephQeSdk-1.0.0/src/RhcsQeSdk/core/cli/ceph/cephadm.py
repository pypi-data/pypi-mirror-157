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


class CephAdm:
    """
    This module provides a command line interface (CLI) to ceph cephadm.
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " cephadm"

    def generate_key(self, **kw):
        """
        Generates a new SSH key.
        Args:
            None
        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " generate-key"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def get_pub_key(self, **kw):
        """
        Retrieves a public portion of the SSH key .
        Args:
            None
        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        output_file = kw.get("output_file")
        cmd = f"{self.base_cmd} get-pub-key > {output_file}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def clear_key(self, **kw):
        """
        Deletes a currently stored SSH key.
        Args:
            None
        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " clear-key"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def set_user(self, **kw):
        """
        Sets user to perform all cephadm operations.
        Args:
            None
        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " set-user"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def set_ssh_config(self, **kw):
        """
        Imports a customized configuration file that will be stored by the monitor.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              ssh_config_file(str): SSH customized configuration file.
        Returns:
        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        ssh_config_file = kw.get("ssh_config_file")
        cmd = self.base_cmd + f" set-ssh-config -i {ssh_config_file}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def clear_ssh_config(self, **kw):
        """
        Removes a customized SSH config and revert back to the default behavior.
        Args:
            None
        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " clear-ssh-config"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
