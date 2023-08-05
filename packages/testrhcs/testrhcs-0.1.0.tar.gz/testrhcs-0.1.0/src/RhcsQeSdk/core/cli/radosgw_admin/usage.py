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


class Usage:
    """
    This module provides CLI interface to manage the usage information for user of object gateway service.
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " usage"

    def show(self, **kw):
        """
        This method is used to show the usage information (with user and date range).
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              uid(str): The radosgw user ID.
              start-date(str): The start date in the format yyyy-mm-dd.
              end-date(str): The end date in the format yyyy-mm-dd.
              show-log-entries(bool): Enable/disable dump of log entries on log show.

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        kw_copy = deepcopy(kw)
        uid = kw_copy.pop("uid", "")
        cmd = (
            self.base_cmd + f" show --uid={uid}" + core_utils.build_cmd_args(kw=kw_copy)
        )
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def trim(self, **kw):
        """
        This method is used to trim usage information (with user and date range).
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              uid(str): The radosgw user ID.
              start-date(str): The start date in the format yyyy-mm-dd.
              end-date(str): The end date in the format yyyy-mm-dd.

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        kw_copy = deepcopy(kw)
        uid = kw_copy.pop("uid", "")
        cmd = (
            self.base_cmd + f" trim --uid={uid}" + core_utils.build_cmd_args(kw=kw_copy)
        )
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
