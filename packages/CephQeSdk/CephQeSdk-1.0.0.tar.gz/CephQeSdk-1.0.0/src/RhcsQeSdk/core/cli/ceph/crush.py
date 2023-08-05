import logging

import RhcsQeSdk.core.cli.fabfile as fabfile
from RhcsQeSdk.core.cli.ceph.rule import Rule

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s"
)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)


class Crush:
    """The module provides CLI interface to implement CRUSH commands that determine
    how to store and retrieve data."""

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " crush"
        self.rule = Rule(self.base_cmd)

    def add_(self, **kw):
        """
        The command add will add or update a crushmap position
        for an osd with a particular weight in a specific location.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:

            osd_name(str): name of the osd.
            crush_weight(double): crush weight for osd.
            bucket_type(str): type of the bucket.

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        osd_name = kw.get("osd_name", "")
        crush_weight = kw.get("crush_weight", 0.0)
        bucket_type = kw.get("bucket_type", "")
        cmd = self.base_cmd + f" add {osd_name} {crush_weight} {bucket_type}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def add_bucket(self, **kw):
        """
        A bucket is a node/location of physical hardware.
        The command add-bucket will add a bucket instance to the CRUSH hierarchy.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:

            bucket_name(str): name of the bucket.
            bucket_type(str): type of the bucket.

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        bucket_name = kw.get("bucket_name", "")
        bucket_type = kw.get("bucket_type", "root")
        cmd = self.base_cmd + f" add-bucket {bucket_name} {bucket_type}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def create_or_move(self, **kw):
        """
        The command create-or-move creates entry or moves entry for an osd with weight to a specified location.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:

            osd_name(str): name of the osd.
            crush_weight(double): crush weight for osd.
            bucket_type(str): type of the bucket.

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        osd_name = kw.get("osd_name", "")
        crush_weight = kw.get("crush_weight", 0.0)
        bucket_type = kw.get("bucket_type", "")
        cmd = self.base_cmd + f" create-or-move {osd_name} {crush_weight} {bucket_type}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def dump(self, **kw):
        """
        The command dump will dump a crush map.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:

            None

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " dump"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def get_tunable(self, **kw):
        """
        The command get-tunable will retrieve the get-tunable straw_calc_version.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:

            None

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " get-tunable straw_calc_version"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def link(self, **kw):
        """
        The command link will link existing entry for a node under a location.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:

            node_name(str): name of the node.
            bucket_type(str): type of the bucket.

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        node_name = kw.get("node_name", "")
        bucket_type = kw.get("bucket_type", "")
        cmd = self.base_cmd + f" link {node_name} {bucket_type}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def move(self, **kw):
        """
        The command move will move existing entry for a node under a location.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:

            osd_name(str): name of the osd.
            bucket_type(str): type of the bucket.

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        osd_name = kw.get("osd_name", "")
        bucket_type = kw.get("bucket_type", "")
        cmd = self.base_cmd + f" move {osd_name} {bucket_type}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def remove_(self, **kw):
        """
        The remove command will remove an osd from the crush map.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:

            osd_name(str): name of the osd.
            ancestor_name(str): name of the ancestor node.

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        osd_name = kw.get("osd_name", "")
        ancestor_name = kw.get("ancestor_name", "")
        cmd = self.base_cmd + f" remove {osd_name} {ancestor_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def rename_bucket(self, **kw):
        """
        The command rename-bucket will change source name of a bucket to the specified name.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:

            source_name(str): source name of a bucket.
            destination_name(str): destination name of the bucket.

        Returns:
             Dict(str)
             A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        source_name = kw.get("source_name", "")
        destination_name = kw.get("destination_name", "")
        cmd = self.base_cmd + f" rename-bucket {source_name} {destination_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def reweight(self, **kw):
        """
        The command reweight adjust the osd crush weight in the crush map.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:

            osd_name(str): name of the osd.
            crush_weight(double): crush weight for osd.

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        osd_name = kw.get("osd_name", "")
        crush_weight = kw.get("crush_weight", 0.0)
        cmd = self.base_cmd + f" reweight {osd_name} {crush_weight}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def reweight_all(self, **kw):
        """
        The command reweight-all recalculates weights for the tree to ensure they sum correctly.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:

            None

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " reweight-all"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def reweight_subtree(self, **kw):
        """
        The command reweight-subtree will change all leaf items beneath a node to a weight in a crush map.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:

            osd_name(str): name of the osd.
            crush_weight(double): crush weight for osd leaf items.

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        osd_name = kw.get("osd_name", "")
        crush_weight = kw.get("crush_weight", 0.0)
        cmd = self.base_cmd + f" reweight-subtree {osd_name} {crush_weight}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def set_(self, **kw):
        """
        The command set if used alone will set crush map from input file.
        Else it will update an osd weight in a particular location.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:

            osd_name(str): name of the osd.
            crush_weight(double): crush weight for osd.
            bucket_type(str): type of the bucket.

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        osd_name = kw.get("osd_name", "")
        crush_weight = kw.get("crush_weight", 0.0)
        bucket_type = kw.get("bucket_type", "")
        cmd = self.base_cmd + f" set {osd_name} {crush_weight} {bucket_type}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def set_tunable(self, **kw):
        """
        The command set-tunable will set crush tunable to a value.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:

            value(int): value to be set against the crush tunable.

        Returns:
            Dict(str)
        A mapping of hosts strings to the given task's return value for that host's execution run.
        """
        value = kw.get("value", 0)
        cmd = self.base_cmd + f" set-tunable straw_calc_version {value}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def tunables(self, **kw):
        """
        The command tunables will tune the CRUSH to a known profile.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:

            profile(str): The profile to which the CRUSH is to be tuned.

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        profile = kw.get("profile", "")
        cmd = self.base_cmd + f" tunables {profile}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def show_tunables(self, **kw):
        """
        The command show-tunables will display current crush tunables.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:

            None

        Returns:
            Dict(str)
        A mapping of hosts strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " show-tunables"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def unlink(self, **kw):
        """
        The command unlink will unlink a node from a crush map.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:

            osd_name(str): name of the osd.
            ancestor_name(str): name of ancestor node(optional).

        Returns:
            Dict(str)
        A mapping of hosts strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        osd_name = kw.get("osd_name", "")
        ancestor_name = kw.get("ancestor_name", "")
        cmd = self.base_cmd + f" unlink {osd_name} {ancestor_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
