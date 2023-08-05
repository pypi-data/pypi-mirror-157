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


class Topic:
    """
    This module provides CLI interface for topic management of object gateway service.
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " topic"

    def list_(self, **kw):
        """
        This method is used to list bucket notifications/pubsub topics.
        Args:
        kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              tenant(str): The bucket notifications/pubsub topic name.

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " list" + core_utils.build_cmd_args(kw=kw)
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def get_(self, **kw):
        """
        This method is used to get a bucket notifications/pubsub topic.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              topic-name(str): The pubsub subscription name.
              tenant(str): The bucket notifications/pubsub topic name.

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        kw_copy = deepcopy(kw)
        topic_name = kw_copy.pop("topic-name", "")
        cmd = (
            self.base_cmd
            + f" get --topic={topic_name}"
            + core_utils.build_cmd_args(kw=kw_copy)
        )
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def rm(self, **kw):
        """
        This method is used to remove a bucket notifications/pubsub topic.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              topic-name(str): The pubsub subscription name.
              tenant(str): The bucket notifications/pubsub topic name.

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        kw_copy = deepcopy(kw)
        topic_name = kw_copy.pop("topic-name", "")
        cmd = (
            self.base_cmd
            + f" rm --topic={topic_name}"
            + core_utils.build_cmd_args(kw=kw_copy)
        )
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
