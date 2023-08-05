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


class Balancer:
    """
    This module provides CLI interface to manage ceph balancer operations.
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " balancer"

    def status(self, **kw):
        """Currently recorded mode, any plans, whether it's enabled are shown as part of the status command.
        Args:
                None
        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " status"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def mode(self, **kw):
        """Adjusts the mode.
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
                mode(str): takes the optimation method to use <upmap,crush-compat>
        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        mode = kw.get("mode")
        cmd = self.base_cmd + f" mode {mode}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def on(self, **kw):
        """Turns the balancer on.
        Args:
                None
        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " on"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def off(self, **kw):
        """Turns the balancer off.
        Args:
                None
        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " off"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def eval_balancer(self, **kw):
        """Evaluats the quality of the data distribution, either for the current
           PG distribution, or the PG distribution that would result after executing a plan.
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
                pool-name(str): takes the name of the pool (optional)
                verbose(bool): to get the greater detail for the evaluation (optional)
                plan-name(str): takes the name of the plan (optional)
        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " eval"
        pool_name = kw.get("pool-name")
        verbose = kw.get("verbose")
        plan_name = kw.get("plan-name")
        if pool_name:
            cmd = cmd + f" {pool_name}"
        elif plan_name:
            cmd = cmd + f" {plan_name}"
        elif verbose:
            cmd = cmd + "-verbose ..."
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def optimize(self, **kw):
        """This is used to optimize named <plan> based on the current mode.
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
                plan-name(str): takes the name of the plan
        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        plan_name = kw.get("plan-name")
        cmd = self.base_cmd + f" optimize {plan_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def show(self, **kw):
        """shows what the plan would do (basically a dump of cli commands to
               adjust weights etc).
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
                plan-name(str): takes the name of the plan
        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        plan_name = kw.get("plan-name")
        cmd = self.base_cmd + f" show {plan_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def ls(self, **kw):
        """Display all the plans.
        Args:
                None
        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " ls"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def rm(self, **kw):
        """Old plans can be discarded with this command.
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
                plan-name(str): takes the name of the plan
        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        plan_name = kw.get("plan-name")
        cmd = self.base_cmd + f" rm {plan_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def execute_balancer(self, **kw):
        """execute plan (and then discard it).
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
        Supported keys:
                plan-name(str): takes the name of the plan
        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        plan_name = kw.get("plan-name")
        cmd = self.base_cmd + f" execute {plan_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
