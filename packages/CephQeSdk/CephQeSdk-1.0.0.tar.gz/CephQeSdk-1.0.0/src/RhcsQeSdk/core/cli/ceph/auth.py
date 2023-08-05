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


class Auth:
    """
    This module provides CLI interface to manage authentication keys via ceph auth.
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " auth"

    def add_(self, **kw):
        """
        Subcommand add adds authentication info for a particular entity
        from input file, or random key if no input is given
        and/or any caps specified in the command.

        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
              entity (str):      takes the class attribute entity if nothing specified
              caps (dict):       dictionary of capabilties
                                 {
                                    <daemon> : "allow [r|w|x|*|...] [pool={pool-name}] [namespace={namespace-name}"
                                    ...
                                 }
                                 eg:
                                 {
                                    "mon" : "allow r"
                                    "osd" : "allow rw pool=liverpool"
                                 }
              input_file(str):   path to keyring(Optional)

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        entity = kw.get("entity")
        caps_dict = kw.get("caps", {})
        caps = ""
        for daemon, cap in caps_dict.items():
            caps = caps + f" {daemon} {cap}"
        caps.strip()
        input_file = kw.get("input_file")
        if input_file:
            input_file = f"-i {input_file}"
        cmd = self.base_cmd + f" add {entity} {caps} {input_file}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def caps(self, **kw):
        """
        Subcommand caps updates caps for name from caps specified in the command.

        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
              entity (str):      takes the class attribute entity if nothing specified
              caps (dict):       dictionary of capabilties
                                 {
                                    <daemon> : "allow [r|w|x|*|...] [pool={pool-name}] [namespace={namespace-name}"
                                    ...
                                 }
                                 eg:
                                 {
                                    "mon" : "allow r"
                                    "osd" : "allow rw pool=liverpool"
                                 }

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        entity = kw.get("entity")
        caps_dict = kw.get("caps", {})
        caps = ""
        for daemon, cap in caps_dict.items():
            caps = caps + f" {daemon} {cap}"
        caps.strip()
        cmd = self.base_cmd + f" caps {entity} {caps}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def del_(self, **kw):
        """
        Subcommand del deletes all caps for name.

        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
              entity (str): takes the class attribute entity if nothing specified

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        entity = kw.get("entity")
        cmd = self.base_cmd + f" del {entity}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def export(self, **kw):
        """
        Subcommand export writes keyring for requested entity, or master keyring if none given.

        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
              entity (str): takes the class attribute entity if nothing specified

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        entity = kw.get("entity")
        cmd = self.base_cmd + f" export {entity}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def get_(self, **kw):
        """
        Subcommand get writes keyring file with requested key.

        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
              entity (str): takes the class attribute entity if nothing specified

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        entity = kw.get("entity")
        cmd = self.base_cmd + f" get {entity}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def get_key(self, **kw):
        """
        Subcommand get writes keyring file with requested key.

        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
              entity (str): takes the class attribute entity if nothing specified
              filename(str): Name of keyring file(Optional)

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        entity = kw.get("entity")
        filename = kw.get("filename")
        cmd = self.base_cmd + f" get-key {entity}"
        if filename:
            cmd = cmd + f" -i {filename}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def get_or_create(self, **kw):
        """
        Subcommand get-or-create adds authentication info for a particular entity from input file,
        or random key if no input given and/or any caps specified in the command.
        Subcommand get-or-create-key gets or adds key for name from system/caps pairs specified in the command.
        If key already exists, any given caps must match the existing caps for that key.

        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
              entity (str):      takes the class attribute entity if nothing specified
              caps (dict):       dictionary of capabilties
                                 {
                                    <daemon> : "allow [r|w|x|*|...] [pool={pool-name}] [namespace={namespace-name}"
                                    ...
                                 }
                                 eg:
                                 {
                                    "mon" : "allow r"
                                    "osd" : "allow rw pool=liverpool"
                                 }
              input_file(str):   input path to keyring
              output_file(str):  to save the output to a file

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        entity = kw.get("entity")
        caps_dict = kw.get("caps", {})
        caps = ""
        for daemon, cap in caps_dict.items():
            caps = caps + f" {daemon} {cap}"
        caps.strip()
        input_file = kw.get("input_file", "")
        output_file = kw.get("output_file", "")
        if input_file:
            input_file = f"-i {input_file}"
        if output_file:
            output_file = f"-o {output_file}"
        cmd = (
            self.base_cmd + f" get-or-create {entity} {caps} {input_file} {output_file}"
        )
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def import_(self, **kw):
        """
        Subcommand import imports one or more users from the specified keyring.

        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
              input_file(str): path to keyring

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        input_file = kw.get("input_file")
        cmd = self.base_cmd + f" import -i {input_file}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def ls(self, **kw):
        """
        Subcommand ls lists out all users in your cluster.

        Args:
            None
        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd = "ceph auth ls"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def print_key(self, **kw):
        """
        Subcommand print_key displays requested key to the standard output.

        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
              entity (str):      takes the class attribute entity if nothing specified

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        entity = kw.get("entity")
        cmd = self.base_cmd + f" print-key {entity}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
