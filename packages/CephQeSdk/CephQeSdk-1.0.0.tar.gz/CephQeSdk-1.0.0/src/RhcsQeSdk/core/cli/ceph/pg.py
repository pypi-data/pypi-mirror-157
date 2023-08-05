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


class Pg:
    """
    This module provides CLI iderface used for managing the placement groups in OSDs.
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " pg"

    def dump(self, **kw):
        """Inerface to get the statistics for the placement groups in your cluster.
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
                format(str): Valid formats are plain and json (optional)
        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " dump" + core_utils.build_cmd_args(kw=kw)
        logger.info(f"Running commmand {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def map_(self, **kw):
        """To get the placement group map for a particular placement group.
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
                pg_id(str): id of the placement group
        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        pg_id = kw.get("pg_id", "")
        cmd = self.base_cmd + " map" + f" {pg_id}"
        logger.info(f"Running commmand {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def scrub(self, **kw):
        """To scrub a placement group, execute the following.
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
                pg_id(str): id of the placement group
        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        pg_id = kw.get("pg_id", "")
        cmd = self.base_cmd + " scrub" + f" {pg_id}"
        logger.info(f"Running commmand {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def debug(self, **kw):
        """Subcommand debug shows debug info about pgs.
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
                option(str): unfound_objects_exist|degraded_pgs_exist
        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        option = kw.get("option", "")
        cmd = self.base_cmd + " debug" + f"{option}"
        logger.info(f"Running commmand {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def deep_scrub(self, **kw):
        """Subcommand deep-scrub starts deep-scrub on <pgid>.
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
                pg_id(str): id of the placement group
        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        pgid = kw.get("pgid", "")
        cmd = self.base_cmd + " deep-scrub" + f" {pgid}"
        logger.info(f"Running commmand {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def dump_pools_json(self, **kw):
        """Subcommand dump_pools_json shows pg pools info in json only.
        Args:
                None
        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " dump_pools_json"
        logger.info(f"Running commmand {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def getmap(self, **kw):
        """Subcommand getmap gets binary pg map to -o/stdout.
        Args:
                None
        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " getmap"
        logger.info(f"Running commmand {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def repair(self, **kw):
        """Subcommand repair starts repair on <pgid>.
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
                pg_id(str): id of the placement group
        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        pgid = kw.get("pgid", "")
        cmd = self.base_cmd + " repair" + f" {pgid}"
        logger.info(f"Running commmand {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def stat(self, **kw):
        """Subcommand stat shows placement group status.
        Args:
                None
        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " stat"
        logger.info(f"Running commmand {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def dump_json(self, **kw):
        """Subcommand dump_json shows human-readable version of pg map in json only.
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
                option(str): all|summary|sum|delta|pools|osds|pgs|pgs_brief
        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        option = kw.get("option", "")
        cmd = self.base_cmd + " dump_json" + f" {option}"
        logger.info(f"Running commmand {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def dump_stuck(self, **kw):
        """Subcommand dump_stuck shows information about stuck pgs.
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
                option(str): inactive|unclean|stale|undersized|degraded
                id(int): id of the placement group
        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        option = kw.get("option", "")
        id = kw.get("id", "")
        cmd = self.base_cmd + " dump_stuck" + f" {option} {id}"
        logger.info(f"Running commmand {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def ls(self, **kw):
        """Subcommand ls lists pg with specific pool, osd, state.
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
                pg_state(str): state of placement group
                id|osd.id(str): id of the osd
        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        pg_state = kw.get("pg-state", "")
        id = kw.get("id", "")
        cmd = self.base_cmd + " ls" + f" {id} {pg_state}"
        logger.info(f"Running commmand {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def ls_by_osd(self, **kw):
        """Subcommand ls-by-osd lists pg on osd [osd].
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
                osdname(str): name of the osd
                id|osd.id(str): id of the osd
                pg_state(str): state of the placement group
        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        osdname = kw.get("osdname", "")
        id = kw.get("id", "")
        pg_state = kw.get("pg-state", "")
        cmd = self.base_cmd + " ls-by-osd" + f" {osdname} {id} {pg_state}"
        logger.info(f"Running commmand {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def ls_by_pool(self, **kw):
        """Subcommand ls-by-pool lists pg with pool = [poolname].
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
                poolstr(str): name of the pool
                id(str): id of the placement group
                pg_state(str): state of the placement group
        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        pg_state = kw.get("pg-state", "")
        poolstr = kw.get("poolstr", "")
        id = kw.get("id", "")
        cmd = self.base_cmd + " ls-by-pool" + f" {poolstr} {id} {pg_state}"
        logger.info(f"Running commmand {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def ls_by_primary(self, **kw):
        """Subcommand ls-by-primary lists pg with primary = [osd].
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
                osdname(str): name of the osd
                id|osd.id(str): id of the osd
                pg_state(str): state of the placement group
        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        osdname = kw.get("osdname", "")
        id = kw.get("id", "")
        pg_state = kw.get("pg-state", "")
        cmd = self.base_cmd + " ls-by-primary" + f" {osdname} {id} {pg_state}"
        logger.info(f"Running commmand {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
