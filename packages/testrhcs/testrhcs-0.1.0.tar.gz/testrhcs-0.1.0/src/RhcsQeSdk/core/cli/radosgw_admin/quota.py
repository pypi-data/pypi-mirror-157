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


class Quota:
    """
    This module provides CLI interface for quota management on users and buckets
    owned by users of the object gateway service.
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " quota"

    def set_(self, **kw):
        """
        Sets quota parameters, before you enable it.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              quota-scope(str): Scope for quota in either bucket/user.
              uid(int): uid of an user.
              num-objects(int): maximum number of objects(Optional).
              max-size(int): Maximum number of bytes(Optional).
        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " set" + core_utils.build_cmd_args(kw=kw)
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def enable(self, **kw):
        """
        Enables quota on specific quota type.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              quota-scope(str): Scope for quota in either bucket/user.
              uid(int): uid of an user.
        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        quota_scope = kw.get("quota-scope")
        uid = kw.get("uid")
        cmd = self.base_cmd + f" enable --quota-scope={quota_scope} --uid={uid}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def disable(self, **kw):
        """
        Disables quota on specific quota type.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              quota-scope(str): Scope for quota in either bucket/user.
              uid(int): uid of an user.
        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        quota_scope = kw.get("quota-scope")
        uid = kw.get("uid")
        cmd = self.base_cmd + f" -disable --quota-scope={quota_scope} --uid={uid}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
