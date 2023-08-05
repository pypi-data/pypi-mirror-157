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


class Module:
    """
    This module provides CLI interface to use mgr modules.
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " module"

    def ls(self, **kw):
        """
        This method is used to see which modules are available, and which are currently enabled.
        Args:
          kw(dict): Key/value pairs that needs to be provided to the installer
          Example:
            Supported keys:
              format(str): used to view detailed metadata about disabled modules.(Optional)

        Returns:
          Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd_args = core_utils.build_cmd_args(kw=kw)
        cmd = self.base_cmd + " ls" + cmd_args
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def enable(self, **kw):
        """
        This method is used to enable modules.
        Args:
          kw(dict): Key/value pairs that needs to be provided to the installer
          Example:
            Supported keys:
              module(str): name of the module.

        Returns:
          Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        module = kw.get("module")
        cmd = self.base_cmd + " enable" + f" {module}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def disable(self, **kw):
        """
        This method is used to disable modules.
        Args:
          kw(dict): Key/value pairs that needs to be provided to the installer
          Example:
            Supported keys:
              module(str): name of the module.

        Returns:
          Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        module = kw.get("module")
        cmd = self.base_cmd + " disable" + f" {module}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
