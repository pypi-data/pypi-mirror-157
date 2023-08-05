"""Module for fabric operations."""
import logging

from fabric.api import env, execute, put, run, settings, sudo

from RhcsQeSdk.core.utilities.metadata import Metadata

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s"
)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)

file_handler = logging.FileHandler("startup.log", mode="a")
file_handler.setLevel(logging.ERROR)

file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class CommandException(Exception):  # Should be your Exception
    pass


class FabricException(Exception):
    pass


def run_command(cmd, config=None):
    """
    Execute a command on given list of remote machines using Fabric.

    Attributes:
        cmd(str): Command to execute in remote node
        config(Dict): dictionary of environmental attributes to run command in fabfile env.

    Returns:
        list(str)
        out: output after execution of command
    """
    # If you don't want to abort for specific exception and handle it with an implementation by keeping warn_only=False
    env.abort_exception = FabricException

    config = config or Metadata().env_config
    env.hosts = config.get("hosts")
    env.user = config.get("username", "")
    env.password = config.get("password", "")
    env.timeout = config.get("timeout", 10)  # default is 10s
    env.key_filename = ""
    env.connection_attempts = config.get("connection_attempts", 1)  # default is 1
    env.keepalive = config.get("keepalive", 0)  # for long_running and default is 0
    env.parallel = config.get("parallel", False)
    env.use_shell = config.get("use_shell", False)
    env.host_string = config.get("hosts")
    env.shell = config.get("shell", False)
    with settings(warn_only=True, combine_stderr=False):
        if env.parallel:
            out = execute(execute_run_cmd, cmd, config)
            for ip, result in out.items():
                parse_output(result, cmd)
            return out
        else:
            output_dict = dict()
            logger.info(f"Running {cmd}")
            if config.get("sudo"):
                output_dict["ip"] = parse_output(sudo(cmd))
            else:
                output_dict["ip"] = parse_output(run(cmd))
            return output_dict


def execute_run_cmd(cmd, config=None):
    """
    Execute a command as a metatask on given list of remote machines using Fabric
    in parallel.

    Attributes:
        cmd(str): Command to execute in remote node
        config(Dict): dictionary of environmental attributes to run command in fabfile env.

    Returns:
        list(str)
        out: output after execution of command
    """
    logger.info(f"Running {cmd}")
    if config.get("sudo"):
        with settings(
            warn_only=True, combine_stderr=False, sudo_user="root", sudo_prefix="sudo"
        ):
            return sudo(cmd)
    else:
        with settings(warn_only=True, combine_stderr=False):
            return run(cmd)


def execute_put_cmd(source_path, destination_path, config=None):
    """
    Downloads a file as a metatask on given list of remote machines using Fabric
    in parallel.

    Attributes:
        source_path(str): source path of content to be transferred.
        destination_path(str): destination path of content into which should be transferred.
        config(Dict): dictionary of environmental attributes to run command in fabfile env.

    Returns:
        list(str)
        out: output after execution of command
    """
    if config.get("sudo"):
        with settings(
            warn_only=True, combine_stderr=False, sudo_user="root", sudo_prefix="sudo"
        ):
            return put(source_path, destination_path, use_sudo=True)
    else:
        with settings(warn_only=True, combine_stderr=False):
            out = put(source_path, destination_path)
            parse_output(out)
            return out


def put_command(source_path, destination_path, config):
    """
    To overwrite remote files on given list of remote machines using Fabric in serial.

    Attributes:
        cmd(str): Command to execute in remote node

    Returns:
        list(str)
        out: output after execution of command
    """
    # If you don't want to abort for specific exception and handle it with an implementation by keeping warn_only=False
    env.abort_exception = FabricException

    env.hosts = config.get("hosts")
    env.user = config.get("username", "cephuser")
    env.password = config.get("password", "cephuser")
    env.timeout = config.get("timeout", 10)  # default is 10s
    env.key_filename = ""
    env.connection_attempts = config.get("connection_attempts", 1)  # default is 1
    env.keepalive = config.get("keepalive", 0)  # for long_running and default is 0
    env.parallel = config.get("parallel", False)
    env.host_string = config.get("hosts")
    with settings(warn_only=True, combine_stderr=False):
        if env.parallel:
            return execute(execute_put_cmd, source_path, destination_path, config)
        else:
            output_dict = dict()
            if config.get("sudo"):
                output_dict["ip"] = parse_output(
                    put(source_path, destination_path, use_sudo=True)
                )
            else:
                output_dict["ip"] = parse_output(put(source_path, destination_path))
            return output_dict


def parse_output(result, cmd=None):
    """
    Parses output and error from result of command.

    Attributes:
        cmd(str): Command to execute in remote node
        result(str): Result of command execution.

    Returns:
        list(str)
        result: output after execution of command

    Raises:
        Exception
    """
    return result
