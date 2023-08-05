import logging
from copy import deepcopy

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


class Zonegroup:
    """
    This module provides CLI interface for zone-group management of the object gateway service.
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " zonegroup"

    def create(self, **kw):
        """
        To create a zonegroup, specify a zonegroup name.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
        Example:
          Supported keys:
            rgw-zonegroup(str) : Takes the zone group name as an input.
            default(bool) : True to create default zone , False for non-default zone.
            rgw-realm(str): Takes the realm name as input.

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        kw_copy = deepcopy(kw)
        zonegroup_name = kw_copy.pop("rgw-zonegroup", "")
        cmd_args = core_utils.build_cmd_args(kw=kw_copy)
        cmd = self.base_cmd + f" create --rgw-zonegroup={zonegroup_name}" + cmd_args
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def add_(self, **kw):
        """
        To add a zone, specify a zone name and the zonegroup name under which zone must be added.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
        Example:
          Supported keys:
            rgw-zonegroup(str) : Takes the zone group name as an input.
            rgw-zone(str) : Takes the zone name as an input.

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        zonegroup_name = kw.get("rgw-zonegroup")
        zone_name = kw.get("rgw-zone")
        cmd = (
            self.base_cmd
            + f" add --rgw-zonegroup={zonegroup_name} --rgw-zone={zone_name}"
        )
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def default(self, **kw):
        """
        To make a zone group as a default one specify the zonegroup name.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
        Example:
          Supported keys:
            rgw-zonegroup(str) : Takes the zone group name as an input.

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        zonegroup_name = kw.get("rgw-zonegroup")
        cmd = self.base_cmd + f" default --rgw-zonegroup={zonegroup_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def get_(self, **kw):
        """
        To get a zonegroup info, specify a zonegroup name.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
        Example:
          Supported keys:
            rgw-zonegroup(str) : Takes the zone group name as an input.

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        zonegroup_name = kw.get("rgw-zonegroup")
        cmd = self.base_cmd + f" get --rgw-zonegroup={zonegroup_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def rename(self, **kw):
        """
        To rename a zonegroup, specify a new zonegroup name.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
        Example:
          Supported keys:
            rgw-zonegroup(str) : Takes the zonegroup name as an input.
            zonegroup-new-name(str) : Takes the new zonegroup name as an input.

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        zonegroup_name = kw.get("rgw-zonegroup")
        new_zonegroup_name = kw.get("zonegroup-new-name")
        cmd = (
            self.base_cmd
            + f" rename --rgw-zonegroup={zonegroup_name} --zonegroup-new-name={new_zonegroup_name}"
        )
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def set_(self, **kw):
        """
        Defining a zone group consists of creating a JSON object.
        specifying at least the required settings name, api_name, is_master:
        Note: You can only have one master zone group.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
        Example:
          Supported keys:
            infile(str) : Takes the Json file you created as an input.

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        infile = kw.get("infile")
        cmd = self.base_cmd + f" set --infile={infile}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def delete(self, **kw):
        """
        To remove a zonegroup, specify a zonegroup name.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
        Example:
          Supported keys:
            rgw-zonegroup(str) : Takes the zone group name as an input.

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        zonegroup_name = kw.get("rgw-zonegroup")
        cmd = self.base_cmd + f" delete --rgw-zonegroup={zonegroup_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def remove_(self, **kw):
        """
        This method is used to remove a zone from a zonegroup.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
        Example:
          Supported keys:
            rgw-zonegroup(str) : Takes the zone group name as an input.
            rgw-zone(str) : Takes the zone name as an input.

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run.
        """
        kw = kw.get("kw")
        zonegroup_name = kw.get("rgw-zonegroup")
        rgw_zone = kw.get("rgw-zone")
        cmd = (
            self.base_cmd
            + f" remove --rgw-zonegroup={zonegroup_name} --rgw-zone={rgw_zone}"
        )
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def modify(self, **kw):
        """
        This method is used to modify an existing zone group’s settings.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
        Example:
          Supported keys:
            rgw-zonegroup(str) : Takes the zone group name as an input.
            master(bool): True to create default zone, False for non-default zonegroup.

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        zonegroup_name = kw.get("rgw-zonegroup")
        master = kw.get("master")
        if master:
            cmd = self.base_cmd + f" modify --rgw-zonegroup={zonegroup_name} --master"
        else:
            cmd = self.base_cmd + f" modify --rgw-zonegroup={zonegroup_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def list_(self, **kw):
        """
        A Ceph cluster contains a list of zone groups. To list the zone groups.
        Args:
          None

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " list"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def placement_add(self, **kw):
        """
        This method is used to add a placement target id to a zonegroup.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
        Example:
          Supported keys:
            rgw-zonegroup(str) : Takes the zone group name as an input.
            placement-id(str): Takes a placement name as an input.

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        zonegroup_name = kw.get("rgw-zonegroup")
        placement_id = kw.get("placement-id")
        cmd = (
            self.base_cmd
            + f" placement add --rgw-zonegroup {zonegroup_name} --placement-id {placement_id}"
        )
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def placement_list(self, **kw):
        """
        This method will list placement targets.
        Args:
          None

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " placement list"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def placement_modify(self, **kw):
        """
        This method will list placement target's settings.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
        Example:
          Supported keys:
            tags(list):The list of tags for zonegroup placement modify command.
            tags-add(list):The list of tags to add for zonegroup placement modify command.
            tags-rm(list): The list of tags to remove for zonegroup placement modify command.

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        tags = kw.get("tags")
        tags_add = kw.get("tags-add")
        tags_rm = kw.get("tags-rm")
        cmd = (
            self.base_cmd
            + f" placement modify --tags={tags} --tags-add={tags_add} --tags-rm={tags_rm}"
        )
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def placement_default(self, **kw):
        """
        This method is used to set a zonegroup’s default placement target.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
        Example:
          Supported keys:
            rgw-zonegroup(str) : Takes the zone group name as an input.
            placement-id(str): Takes a placement name as an input.

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        zonegroup_name = kw.get("rgw-zonegroup")
        placement_id = kw.get("placement-id")
        cmd = (
            self.base_cmd
            + f" placement default --rgw-zonegroup {zonegroup_name} --placement-id {placement_id}"
        )
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
