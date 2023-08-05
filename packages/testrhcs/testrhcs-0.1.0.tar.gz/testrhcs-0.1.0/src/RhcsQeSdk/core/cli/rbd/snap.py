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


class Snap:
    """
    This module provides CLI interface to manage snapshots from images in pool.
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " snap"

    def create(self, **kw):
        """
        Creates a snapshot.
        kw(dict): Key/value pairs that needs to be provided to the installer
            Example::
            Supported keys:
                pool_name(str)  : name of the pool
                snap_name(str)  : name of the snapshot
                image_name(str) : name of the image
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        image_name = kw.get("image_name")
        snap_name = kw.get("snap_name")
        pool_name = kw.get("pool_name")
        cmd = self.base_cmd + f" create {pool_name}/{image_name}@{snap_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def ls(self, **kw):
        """
        Lists snapshots.
        Args:
        kw(dict): Key/value pairs that needs to be provided to the installer
            Example::
            Supported keys:
                pool_name(str) : name of the pool
                image_name(str): name of the image
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        image_name = kw.get("image_name")
        pool_name = kw.get("pool_name")
        cmd = self.base_cmd + f" ls {pool_name}/{image_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def rollback(self, **kw):
        """
        Rollback a snapshot.
        Args:
        kw(dict): Key/value pairs that needs to be provided to the installer
            Example::
            Supported keys:
                pool_name(str)  : name of the pool
                snap_name(str)  : name of the snapshot
                image_name(str) : name of the image
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        image_name = kw.get("image_name")
        pool_name = kw.get("pool_name")
        snap_name = kw.get("snap_name")
        cmd = self.base_cmd + f" rollback {pool_name}/{image_name}@{snap_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def rm(self, **kw):
        """
        Removes the snapshot.
        Args:
        kw(dict): Key/value pairs that needs to be provided to the installer
            Example::
            Supported keys:
                pool_name(str)  : name of the pool
                snap_name(str)  : name of the snapshot
                image_name(str) : name of the image
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        image_name = kw.get("image_name")
        pool_name = kw.get("pool_name")
        snap_name = kw.get("snap_name")
        cmd = self.base_cmd + f" rm {pool_name}/{image_name}@{snap_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def purge(self, **kw):
        """
        Purges the snapshot.
        Args:
        kw(dict): Key/value pairs that needs to be provided to the installer
            Example::
            Supported keys:
                pool_name(str)  : name of the pool
                image_name(str) : name of the image
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        image_name = kw.get("image_name")
        pool_name = kw.get("pool_name")
        cmd = self.base_cmd + f" purge {pool_name}/{image_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def protect(self, **kw):
        """
        Protects the snapshot.
        Args:
        kw(dict): Key/value pairs that needs to be provided to the installer
            Example::
            Supported keys:
                pool_name(str)  : name of the pool
                snap_name(str)  : name of the snapshot
                image_name(str) : name of the image
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        image_name = kw.get("image_name")
        pool_name = kw.get("pool_name")
        snap_name = kw.get("snap_name")
        cmd = self.base_cmd + f" protect {pool_name}/{image_name}@{snap_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def unprotect(self, **kw):
        """
        Unprotects the snapshot.
        Args:
        kw(dict): Key/value pairs that needs to be provided to the installer
            Example::
            Supported keys:
                pool_name(str)  : name of the pool
                image_name(str) : name of the image
                snap_name(str)  : name of the snapshot
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        image_name = kw.get("image_name")
        pool_name = kw.get("pool_name")
        snap_name = kw.get("snap_name")
        cmd = self.base_cmd + f" unprotect {pool_name}/{image_name}@{snap_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
