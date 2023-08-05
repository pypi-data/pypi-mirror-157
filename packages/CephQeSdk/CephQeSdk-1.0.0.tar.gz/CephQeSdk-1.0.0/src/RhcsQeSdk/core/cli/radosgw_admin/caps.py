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


class Caps:
    """
    This module provides CLI interface for commands used for administrative capabilities
    via radosgw-admin caps command.
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " caps"

    def add_(self, **kw):
        """Add user capabilities.
        Args:
                uid(str) : User id
                caps(str) : List of caps (e.g., “usage=read, write; user=read”).
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        uid = kw.get("uid", "")
        caps = kw.get("caps", "")
        cmd = self.base_cmd + f" add --uid={uid} --caps={caps}"
        logger.info(f"Running commmand {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def rm(self, **kw):
        """Remove user capabilities.
        Args:
                uid(str) : User id
                caps(str) : List of caps (e.g., “usage=read, write; user=read”).
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        uid = kw.get("uid", "")
        caps = kw.get("caps", "")
        cmd = self.base_cmd + f" rm --uid={uid} --caps={caps}"
        logger.info(f"Running commmand {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
