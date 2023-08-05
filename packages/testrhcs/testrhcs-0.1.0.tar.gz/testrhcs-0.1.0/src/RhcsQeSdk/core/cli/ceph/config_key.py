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


class ConfigKey:
    """
    This module provides CLI interface to implement ceph config-key commands.
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " config-key"

    def rm(self, **kw):
        """
        The command rm will remove a configuration key.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:

            key(str): name of the configuration key to be deleted.

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        key = kw.get("key", "")
        cmd = self.base_cmd + f" rm {key}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def ls(self, **kw):
        """
        The command ls will list the configuration keys.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:

            None

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " ls"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def get_(self, **kw):
        """
        The command get will retrieve the value attached to a configuration key.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:

            key(str): name of the key whose value is to be retrieved.

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        key = kw.get("key", "")
        cmd = self.base_cmd + f" get {key}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def set_(self, **kw):
        """
        The command set will set a value against a configuration key.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:

            key(str): name of the configuration key.
            value(int): value to be set against the key.

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        key = kw.get("key", "")
        value = kw.get("value", "")
        cmd = self.base_cmd + f" set {key} {value}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def dump(self, **kw):
        """
        The command dump will dump configuration keys and values.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:

            None

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " dump"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def exists(self, **kw):
        """
        The command exists will check if a configuration key exists or not.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:

            key(str): name of the configuration key.

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        key = kw.get("key", "")
        cmd = self.base_cmd + f" exists {key}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
