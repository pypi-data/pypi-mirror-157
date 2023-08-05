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


class Subscription:
    """
    This module provides CLI interface to manage pubsub subscription.
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " subscription"

    def get_(self, **kw):
        """
        This method is used to get a pubsub subscription definition.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              topic-name(str): The pubsub subscription name.
              tenant(str): The bucket notifications/pubsub topic name.

        Returns:
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        topic_name = kw.get("topic-name")
        tenant = kw.get("tenant")
        cmd = self.base_cmd + f" get --subscription={topic_name} --tenant={tenant}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def rm(self, **kw):
        """
        This method is used to remove a pubsub subscription.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              topic-name(str): The pubsub subscription name.
              tenant(str): The bucket notifications/pubsub topic name.

        Returns:
          Dict(str): A mapping of host strings to the given task’s return value for that host’s execution run.
        """
        kw = kw.get("kw")
        topic_name = kw.get("topic-name")
        tenant = kw.get("tenant")
        cmd = self.base_cmd + f" rm --subscription={topic_name} --tenant={tenant}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def pull(self, **kw):
        """
        This method is used to show events in a pubsub subscription.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              topic-name(str): The pubsub subscription name.
              tenant(str): The bucket notifications/pubsub topic name.
              last-marker(str): To resume if command gets interrupted.

        Returns:
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        topic_name = kw.get("topic-name")
        last_marker = kw.get("last-marker")
        tenant = kw.get("tenant")
        cmd = (
            self.base_cmd
            + f" pull --subscription={topic_name} --marker={last_marker} --tenant={tenant}"
        )
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def ack(self, **kw):
        """
        This method is used to ack (remove) an event in a pubsub subscription.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              topic-name(str): The pubsub subscription name.
              tenant(str): The bucket notifications/pubsub topic name.
              event-id(str): The event id in a pubsub subscription.

        Returns:
          Dict(str): A mapping of host strings to the given task’s return value for that host’s execution run.
        """
        kw = kw.get("kw")
        topic_name = kw.get("topic-name")
        event_id = kw.get("event-id")
        tenant = kw.get("tenant")
        cmd = (
            self.base_cmd
            + f" ack --subscription={topic_name} --event-id={event_id} --tenant={tenant}"
        )
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
