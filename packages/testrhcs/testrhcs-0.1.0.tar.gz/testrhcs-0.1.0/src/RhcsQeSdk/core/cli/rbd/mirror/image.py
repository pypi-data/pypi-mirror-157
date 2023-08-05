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


class Image:
    """This module provides CLI interface to manage rbd mirror image commands."""

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " image"

    def demote(self, **kw):
        """Wrapper for rbd mirror image demote.

        Args:
            kw: Key value pair of method arguments
        Example::
        Supported keys:
            image_spec: poolname/[namespace]/imagename
            pool_name: Name of the pool.
            namespace: Name of the namespace.
            image: Name of the image.
        Returns:
            Dict(str):
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")

        kw_copy = deepcopy(kw)
        image_spec = kw_copy.pop("image_spec", "")
        cmd_args = core_utils.build_cmd_args(kw=kw_copy)

        cmd = f"{self.base_cmd} demote {image_spec}{cmd_args}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def disable(self, **kw):
        """Wrapper for rbd mirror image disable.

        Args
            kw: Key value pair of method arguments

        Example::
        Supported keys:
            image_spec: poolname/[namespace]/imagename
            pool_name: Name of the pool.
            namespace: Name of the namespace.
            image: Name of the image.
        Returns:
            Dict(str):
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")

        kw_copy = deepcopy(kw)
        image_spec = kw_copy.pop("image_spec", "")
        cmd_args = core_utils.build_cmd_args(kw=kw_copy)

        cmd = f"{self.base_cmd} disable {image_spec}{cmd_args}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def enable(self, **kw):
        """Wrapper for rbd mirror image enable.

        Args
            kw: Key value pair of method arguments
            Example::
            Supported keys:
                image_spec: poolname/[namespace]/imagename
                pool_name: Name of the pool.
                namespace: Name of the namespace.
                image: Name of the image.
                mode: Mode of mirroring(journal/snapshot) [default: journal]
        Returns:
            Dict(str):
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")

        kw_copy = deepcopy(kw)
        image_spec = kw_copy.pop("image_spec", "")
        mode = kw_copy.pop("mode", "")
        cmd_args = core_utils.build_cmd_args(kw=kw_copy)

        cmd = f"{self.base_cmd} enable {image_spec} {mode}{cmd_args}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def promote(self, **kw):
        """Wrapper for rbd mirror image promote.

        Args:
            kw: Key value pair of method arguments
            Example::
            Supported keys:
                image_spec: poolname/[namespace]/imagename
                pool_name: Name of the pool.
                namespace: Name of the namespace.
                image: Name of the image.
                force(bool): True - To promote image forcefully
        Returns:
            Dict(str):
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")

        kw_copy = deepcopy(kw)
        image_spec = kw_copy.pop("image_spec", "")
        cmd_args = core_utils.build_cmd_args(kw=kw_copy)

        cmd = f"{self.base_cmd} promote {image_spec}{cmd_args}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def resync(self, **kw):
        """Wrapper for rbd mirror image resync.

        Args:
            kw: Key value pair of method arguments
            Example::
            Supported keys:
                image_spec: poolname/[namespace]/imagename
                pool_name: Name of the pool.
                namespace: Name of the namespace.
                image: Name of the image.
        Returns:
            Dict(str):
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")

        kw_copy = deepcopy(kw)
        image_spec = kw_copy.pop("image_spec", "")
        cmd_args = core_utils.build_cmd_args(kw=kw_copy)

        cmd = f"{self.base_cmd} resync {image_spec}{cmd_args}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def snapshot(self, **kw):
        """Wrapper for rbd mirror image snapshot.

        Args:
            kw: Key value pair of method arguments
            Example::
            Supported keys:
                image_spec: poolname/[namespace]/imagename
                pool_name: Name of the pool.
                namespace: Name of the namespace.
                image: Name of the image.
        Returns:
            Dict(str):
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")

        kw_copy = deepcopy(kw)
        image_spec = kw_copy.pop("image_spec", "")
        cmd_args = core_utils.build_cmd_args(kw=kw_copy)

        cmd = f"{self.base_cmd} snapshot {image_spec}{cmd_args}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def status(self, **kw):
        """Wrapper for rbd mirror image status.

        Args:
            kw: Key value pair of method arguments
            Example::
            Supported keys:
                format: output format (plain, json, or xml) [default: plain]
                pretty-format: true - pretty formatting (json and xml)
                image_spec: poolname/[namespace]/imagename
                pool_name: Name of the pool.
                namespace: Name of the namespace.
                image: Name of the image.
        Returns:
            Dict(str):
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")

        kw_copy = deepcopy(kw)
        image_spec = kw_copy.pop("image_spec", "")
        cmd_args = core_utils.build_cmd_args(kw=kw_copy)

        cmd = f"{self.base_cmd} status {image_spec}{cmd_args}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
