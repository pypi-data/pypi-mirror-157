import logging

import RhcsQeSdk.core.cli.fabfile as fabfile
from RhcsQeSdk.core.cli.ceph.application import Application

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s"
)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)


class Pool:
    """
    This module provides CLI interface to manage pool operations of pool within ceph cluster via ceph osd pool.
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " pool"
        self.application = Application(self.base_cmd)

    def create(self, **kw):
        """
        The create command will create a pool with provided specifications.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
                pool_name(str): name of the pool.
                pg_num(int): total number of placement groups.
                pgp_num(int): total number of placement groups for placement purpose.
                pool_type(str): pool type can be erasure or replicated.
                crush_rule_name(str): The name of the crush rule for the pool. The rule MUST exist.
                expected_num_objects(int): The expected number of objects for the pool.
                erasure_code_profile(str): A profile when creating an erasure-coded pool and the associated CRUSH rule.

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        pool_name = kw.get("pool_name", "ceph")
        pg_number = kw.get("pg_num", "")
        pgp_number = kw.get("pgp_num", "")
        pool_type = kw.get("pool_type", "")
        crush_rule_name = kw.get("crush_rule_name", "")
        expected_num_objects = kw.get("expected_num_objects", "")
        cmd = f"{self.base_cmd} create {pool_name} {pg_number} {pgp_number} "

        if pool_type == "erasure":
            erasure_code_profile = kw.get("erasure_code_profile", "")
            cmd = (
                cmd
                + f"{pool_type} {erasure_code_profile} {crush_rule_name} {expected_num_objects}"
            )

        else:
            cmd = cmd + f"{pool_type} {crush_rule_name} {expected_num_objects}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def delete(self, **kw):
        """
        The delete command will delete a pool.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
                pool_name(str): name of the pool to be deleted.
                yes-i-really-mean-it(bool): whether to delete or not(Optional)

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        pool_name = kw.get("pool_name", "ceph")
        ending = kw.get("yes-i-really-really-mean-it", "")
        cmd = f"{self.base_cmd} delete {pool_name} {pool_name} --{ending}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def rename(self, **kw):
        """
        The rename command will rename a pool.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
                pool_name(str): current name of a pool.
                new_pool_name(str): new name to be given to the pool.

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return vlaue for that host's execution run.
        """
        kw = kw.get("kw")
        current_pool_name = kw.get("pool_name", "ceph")
        new_pool_name = kw.get("new_pool_name", "")
        cmd = f"{self.base_cmd} rename {current_pool_name} {new_pool_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def set_quota(self, **kw):
        """
        The command set-quota can be used to set the values of max_objects and max_bytes of a pool.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example:
            Supported Keys:
                pool_name(str): name of the pool.
                max_objects(str): to check whether object count has to be set.
                max_bytes(str): to check whether byte count has to be set.

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        pool_name = kw.get("pool_name", "ceph")
        max_objects = kw.get("max_objects", None)
        max_bytes = kw.get("max_bytes", None)
        cmd = f"{self.base_cmd} set-quota {pool_name} "

        if max_bytes and max_objects:
            cmd = cmd + f" max_objects max_objects {max_objects} max_bytes {max_bytes}"
        elif max_objects:
            cmd = cmd + f" max_objects {max_objects}"
        else:
            cmd = cmd + f" max_bytes {max_bytes}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def get_quota(self, **kw):
        """
        The command get-quota can be used to retrieve the values of max_objects and max_bytes of a pool.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
                pool_name(str): name of the pool.
                max_objects(str): to check whether object count has to be retrieved.
                max_bytes(str): to check whether byte count has to be retrieved.

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        pool_name = kw.get("pool_name", "ceph")
        max_objects = kw.get("max_objects", None)
        max_bytes = kw.get("max_bytes", None)
        cmd = f"{self.base_cmd} get-quota {pool_name} "

        if max_bytes and max_objects:
            cmd = cmd + f" max_objects max_objects {max_objects} max_bytes {max_bytes}"
        elif max_objects:
            cmd = cmd + f" max_objects {max_objects}"
        else:
            cmd = cmd + f" max_bytes {max_bytes}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def mksnap(self, **kw):
        """
        The command mksnap will make a snapshot in the pool specified by the user.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:

            pool_name(str): name of the pool.
            snap_name(str): name of the snapshot.

        Returns:
            Dict(str):
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        pool_name = kw.get("pool_name", "ceph")
        snap_name = kw.get("snap_name", "")
        cmd = f"{self.base_cmd} mksnap {pool_name} {snap_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def rmsnap(self, **kw):
        """
        The command rmsnap will remove a snap shot from the pool specified by the user.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
                pool_name(str): name of the pool.
                snap_name(str): name of the snapshot to be removed.

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        pool_name = kw.get("pool_name", "ceph")
        snap_name = kw.get("snap_name", "")
        cmd = f"{self.base_cmd} rmsnap {pool_name} {snap_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def get_(self, **kw):
        """
        The command get will retrun value of a key as specified by the user.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
                pool_name(str): name of the pool
                key(Union[str,int]): name of the property of an osd pool.

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        pool_name = kw.get("pool_name", "ceph")
        key = kw.get("key", None)
        cmd = f"{self.base_cmd} get {pool_name} {key}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def set_(self, **kw):
        """
        The command set will set a value to a particular key in pool.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
                pool_name(str): name of the pool.
                key(Union[str,int]): name of the property of an osd pool
                value(Union[str,int]): vlaue to be set against the key.

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        pool_name = kw.get("pool_name", "ceph")
        key = kw.get("key", None)
        value = kw.get("value", None)
        cmd = f"{self.base_cmd} set {pool_name} {key} {value}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
