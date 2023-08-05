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


class Blocklist:
    """
    Subcommand blocklist manage blocklisted clients. It uses some additional subcommands.
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " blocklist"

    def add_(self, **kw):
        """
        Subcommand add adds <addr> to blocklist (optionally until <expire> seconds from now)

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
                add:
                  entity_addr(str) : address of the entity
                  expiry(float) : expiry seconds from now(optional)

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        entity_addr = kw.get("entity_addr")
        expiry = kw.get("expiry")
        cmd = f"{self.base_cmd} add {entity_addr}"
        if expiry:
            cmd = cmd + f" {expiry}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def ls(self, **kw):
        """
        Subcommand ls show blocklisted clients

        Args:
            None

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd = f"{self.base_cmd} ls"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def rm(self, **kw):
        """
        Subcommand rm remove <addr> from blocklist

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
                add:
                  entity_addr(str) : address of the entity

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        entity_addr = kw.get("entity_addr")
        cmd = f"{self.base_cmd} rm {entity_addr}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
