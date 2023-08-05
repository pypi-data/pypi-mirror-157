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


class Label:
    """
    This module provides a command line interface (CLI) to ceph orch host label.
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " label"

    def add_(self, **kw):
        """
        To set a label to specified host.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              host_name(str): name of host.
              label(str): name of label.
        Returns:
          Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        hosts = kw.get("hosts", {})
        label = kw.get("label", "")
        cmd = self.base_cmd + f" add {hosts} {label}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def rm(self, **kw):
        """
        To remove a label from appropriate hosts.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              host_name(str): name of host.
              label(str): name of label.
        Returns:
          Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        host_name = kw.get("host_name")
        label = kw.get("label")
        cmd = self.base_cmd + f" rm {host_name} {label}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
