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


class User:
    """
    This module provides CLI interface for user management of the Ceph Object Storage service.
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " user"

    def create(self, **kw):
        """Create a new user.
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
                Example::
                        Supported keys:
                                display-name(str): takes name of the user
                                uid(str): takes the user-id
                                email(str): takes the email address of the user(optional)
                                key-type(str): type of key(optional)
                                access-key(str): takes the access key(optional)
                                secret: takes the secret key(optional)
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """

        cmd = self.base_cmd + " create" + core_utils.build_cmd_args(kw=kw)
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def modify(self, **kw):
        """Modify a user. Typical modifications are to keys and secrets, email addresses,
                display names and access levels.
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
                Example::
                Supported keys:
                        uid(str): takes the user-id
                        display-name(str): takes name of the user
                        email(str): takes the email address of the user(optional)
                        key-type(str): type of key(optional)
                        access-key(str): takes the access key(optional)
                        secret|secret-key: takes the secret key(optional)
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " modify" + core_utils.build_cmd_args(kw=kw)
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def info(self, **kw):
        """Display information of a user, and any potentially available subusers and keys.
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
                Supported keys::
                        uid(str):  takes the user-id
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        uid = kw.get("uid")
        cmd = self.base_cmd + f" info --uid={uid}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def rename(self, **kw):
        """Renames a user.
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
                Supported keys::
                        uid(str):  takes the user-id
                        new-uid(str): takes ID of the new user.
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        uid = kw.get("uid")
        new_uid = kw.get("new-uid")
        cmd = self.base_cmd + f" rename --uid={uid} --new-uid={new_uid}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def rm(self, **kw):
        """Remove a user.
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
                Supported keys::
                        uid(str):  takes the user-id
                        purge-data(bool): This option purges all data associated to the UID(optional)
                        purge-keys(bool): This option purges all keys associated to the UID(optional)
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " rm" + core_utils.build_cmd_args(kw=kw)
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def suspend(self, **kw):
        """Suspend a user.
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
                Supported keys::
                        uid(str):  takes the user-id
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        uid = kw.get("uid")
        cmd = self.base_cmd + f" suspend --uid={uid}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def enable(self, **kw):
        """Re-enable user after suspension.
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
                Supported keys::
                        uid(str):  takes the user-id
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        uid = kw.get("uid")
        cmd = self.base_cmd + f" enable --uid={uid}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def check(self, **kw):
        """Check user info.
        Args:
                None
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " check"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def stats(self, **kw):
        """Show user stats as accounted by quota subsystem.
        Args:
                kw(dict): Key/value pairs that needs to be provided to the installer
        Example::
                Supported keys::
                        uid(str):  takes the user-id
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        uid = kw.get("uid")
        cmd = self.base_cmd + f" stats --uid={uid} --sync-stats"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def list_(self, **kw):
        """List all users.
        Args:
                None
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " list"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
