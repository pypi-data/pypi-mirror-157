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


class Key:
    """
    This module provides CLI interface to implement radosgw-admin user key commands.
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " key"

    def create(self, **kw):
        """
        The command create will create a user key.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:

            user_id(str): user id of a particular user.
            key_type(str): key_type of the user.(s3 for user and swift for subuser)

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run
        """
        kw = kw.get("kw")
        user_id = kw.get("user_id", "")
        key_type = kw.get("key_type", "")
        cmd = self.base_cmd + " create "
        if key_type == "s3":
            cmd = (
                cmd
                + f"--uid={user_id} --key-type={key_type} --gen-access-key --gen-secret"
            )
        else:
            cmd = (
                cmd
                + f"--subuser={user_id}:swift --key-type={key_type} --gen-access-key --gen-secret"
            )
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def rm(self, **kw):
        """
        The command rm will remove a user key.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:

            user_id(str): user id of a particular user.
            access_key(str): the access key for a specific user.

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run
        """
        kw = kw.get("kw")
        user_id = kw.get("user_id", "")
        access_key = kw.get("access_key", "")
        cmd = self.base_cmd + f" rm --uid={user_id} --access-key {access_key}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
