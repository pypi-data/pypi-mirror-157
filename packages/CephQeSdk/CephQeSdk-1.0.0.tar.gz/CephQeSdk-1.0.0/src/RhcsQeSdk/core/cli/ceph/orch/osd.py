import logging

from RhcsQeSdk.core.cli.ceph.orch.rm import Rm

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s"
)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)


class Osd:
    """This module provides CLI interface to ceph orch osd."""

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " osd"
        self.rm = Rm(self.base_cmd)
