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


class Rule:
    """
    This module provides CLI interface to implement CRUSH rules that defines
    how a Ceph client selects a bucket and OSD to store objects.
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " rule"

    def dump(self, **kw):
        """
        The command dump will dump a crush rule.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:

            crush_rule_name(str): name of the crush rule.

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run
        """
        kw = kw.get("kw")
        crush_rule_name = kw.get("crush_rule_name", "")
        cmd = self.base_cmd + f" dump {crush_rule_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def ls(self, **kw):
        """
        The command ls will list the crush rules.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:

            None

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " ls"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def rm(self, **kw):
        """
        The command rm removes a crush rule.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:

            crush_rule_name(str): name of the crush rule.

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run
        """
        kw = kw.get("kw")
        crush_rule_name = kw.get("crush_rule_name", "")
        cmd = self.base_cmd + f" rm {crush_rule_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def create_erasure(self, **kw):
        """
        The command create-erasure will create a crush rule for erasure coded pool with a profile.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:

            crush_rule_name(str): name of the crush rule.
            profile(str): type of profile.

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run
        """
        kw = kw.get("kw")
        crush_rule_name = kw.get("crush_rule_name", "")
        profile = kw.get("profile", "")
        cmd = self.base_cmd + f" create-erasure {crush_rule_name} {profile}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def create_simple(self, **kw):
        """
        The command create-simple will create a crush rule
        from the root and replicate it to a bucket type using
        a particular mode.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:

            crush_rule_name(str): name of the crush rule.
            root(str): location where the node has to be linked.
            bucket_type(str): type of the bucket.
            mode_type(str): type of the choose mode.(either firstn (default) or indep)

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run
        """
        kw = kw.get("kw")
        crush_rule_name = kw.get("crush_rule_name", "")
        root = kw.get("root", "")
        bucket_type = kw.get("bucket_type", "")
        mode_type = kw.get("mode_type", "firstn")
        cmd = (
            self.base_cmd
            + f" create-simple {crush_rule_name} {root} {bucket_type} {mode_type}"
        )
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
