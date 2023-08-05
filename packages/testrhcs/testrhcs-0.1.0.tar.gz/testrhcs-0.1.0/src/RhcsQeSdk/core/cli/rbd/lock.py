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


class Lock:
    """
    This Class provides wrappers for rbd lock commands.
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " lock"

    def add_(self, kw):
        """
        This method is used to lock an image.
        Args:
          kw(dict): Key/value pairs that needs to be provided to the installer
          Example:
            Supported keys:
                pool_name(str): name of the pool.
                image_name(str): name of the image.
                lockid(str): id of the lock to image.
                image_spec(str): image specification

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        lockid = kw.get("lockid")
        kw_copy = deepcopy(kw)
        image_spec = kw_copy.pop("image_spec", "")
        cmd_args = core_utils.build_cmd_args(kw=kw_copy)

        cmd = self.base_cmd + " add" + f" {image_spec}{cmd_args} {lockid}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def ls(self, kw):
        """
        This method is used to show locks held on the image.
        Args:
          kw(dict): Key/value pairs that needs to be provided to the installer
          Example:
            Supported keys:
                pool_name(str): name of the pool.
                image_name(str): name of the image.
                image_spec(str): image specification

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        kw_copy = deepcopy(kw)
        image_spec = kw_copy.pop("image_spec", "")
        cmd_args = core_utils.build_cmd_args(kw=kw_copy)
        cmd = self.base_cmd + " ls" + f" {image_spec}{cmd_args}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def rm(self, kw):
        """Release a lock on an image.
        Args:
          kw(dict): Key/value pairs that needs to be provided to the installer
          Example:
            Supported keys:
                pool_name(str): name of the pool.
                image_name(str): name of the image.
                lock_name(str): name of the lock.
                lockid(str): id of lock.
                image_spec(str): image specification

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        kw_copy = deepcopy(kw)
        lockid = kw_copy.get("lockid")
        lock_name = kw_copy.get("lock_name")
        image_spec = kw_copy.pop("image_spec", "")
        cmd_args = core_utils.build_cmd_args(kw=kw_copy)
        cmd = self.base_cmd + " rm" + f" {image_spec}{cmd_args} {lockid} {lock_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
