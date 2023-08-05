import logging
from copy import deepcopy

import RhcsQeSdk.core.cli.fabfile as fabfile
from RhcsQeSdk.core.cli.rbd.config.config import Config
from RhcsQeSdk.core.cli.rbd.device import Device
from RhcsQeSdk.core.cli.rbd.feature import Feature
from RhcsQeSdk.core.cli.rbd.group.group import Group
from RhcsQeSdk.core.cli.rbd.image_meta import ImageMeta
from RhcsQeSdk.core.cli.rbd.journal import Journal
from RhcsQeSdk.core.cli.rbd.lock import Lock
from RhcsQeSdk.core.cli.rbd.migration import Migration
from RhcsQeSdk.core.cli.rbd.mirror.mirror import Mirror
from RhcsQeSdk.core.cli.rbd.namespace import Namespace
from RhcsQeSdk.core.cli.rbd.pool import Pool
from RhcsQeSdk.core.cli.rbd.snap import Snap
from RhcsQeSdk.core.cli.rbd.trash import Trash
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


class Rbd:
    """
    This module provides CLI interface to manage block device images in a cluster.
    """

    def __init__(self, base_cmd=""):
        self.base_cmd = f"{base_cmd}rbd"
        self.device = Device(self.base_cmd)
        self.mirror = Mirror(self.base_cmd)
        self.trash = Trash(self.base_cmd)
        self.snap = Snap(self.base_cmd)
        self.migration = Migration(self.base_cmd)
        self.pool = Pool(self.base_cmd)
        self.namespace = Namespace(self.base_cmd)
        self.image_meta = ImageMeta(self.base_cmd)
        self.journal = Journal(self.base_cmd)
        self.feature = Feature(self.base_cmd)
        self.config = Config(self.base_cmd)
        self.lock = Lock(self.base_cmd)
        self.group = Group(self.base_cmd)

    def create(self, **kw):
        """
        Creates a block device image.
        Args:
        kw(dict): Key/value pairs that needs to be provided to the installer
            Example::
            Supported keys:
                pool_name(str) : name of the pool into which image should be stored
                size(int)      : size of image in MegaBytes
                image_name(str):  name of image to be created
        Returns:
            Dict(str):
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        image_name = kw.get("image_name")
        size = kw.get("size")
        pool_name = kw.get("pool_name")
        cmd = self.base_cmd + f" create {image_name} --size {size} --pool {pool_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def ls(self, **kw):
        """
        Lists block device images within pool.
        Args:
        kw(dict): Key/value pairs that needs to be provided to the installer
            Example::
            Supported keys:
                pool_name(str)  : name of the pool(optional)
        Returns:
            Dict(str):
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        pool_name = kw.get("pool_name", "")
        cmd = self.base_cmd + f" ls {pool_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def list_(self, **kw):
        """
        Lists block device images.
        Args:
        kw(dict): Key/value pairs that needs to be provided to the installer
            None
        Returns:
            Dict(str):
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " list"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def info(self, **kw):
        """
        Retrieves information on the block device image.
        Args:
        kw(dict): Key/value pairs that needs to be provided to the installer
            Example::
            Supported keys:
                pool_name(str)  : name of the pool from which info should be retreived(optional)
                image_name(str) :  name of the image from which info should be retreived
        Returns:
            Dict(str):
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        image_name = kw.get("image_name")
        if kw.get("pool_name"):
            pool_name = kw.get("pool_name")
            cmd = self.base_cmd + f" --image {image_name} -p {pool_name} info"
        else:
            cmd = self.base_cmd + f" --image {image_name} info"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def status(self, **kw):
        """
        Retrieves current state of the block device image operation.
        Args:
        kw(dict): Key/value pairs that needs to be provided to the installer
            Example::
            Supported keys:
                target_name(str): The operation for which status should be known
        Returns:
            Dict(str):
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        target = kw.get("target_name")
        cmd = self.base_cmd + f" status {target}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def help(self, **kw):
        """
        Displays help for a particular rbd command and its subcommand.
        Args:
        kw(dict): Key/value pairs that needs to be provided to the installer
            Example::
            Supported keys:
                command(str): name of command
                sub-command(str): name of sub-command
        Returns:
            Dict(str):
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        command = kw.get("command")
        sub_command = kw.get("sub-command")
        cmd = self.base_cmd + f" help {command} {sub_command}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def map(self, **kw):
        """
        Maps or unmaps RBD for one or more RBD images.
        Args:
        kw(dict): Key/value pairs that needs to be provided to the installer
            Example::
            Supported keys:
                pool_name(str): Name of the pool(default is rbd)
                image_name(str): image name
                option(str): options to be passed
        Returns:
            Dict(str):
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        kw_copy = deepcopy(kw)
        image_name = kw_copy.pop("image_name", "")
        pool_name = kw_copy.pop("pool_name", "rbd")
        cmd = (
            self.base_cmd
            + f" map {pool_name}/{image_name}"
            + core_utils.build_cmd_args(kw=kw_copy)
        )
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def resize(self, **kw):
        """
        Resize the size of image.
        kw(dict): Key/value pairs that needs to be provided to the installer
            Example::
            Supported keys:
                image_name(str): name of the image on which resize should happen
                size (int)     :  updated size of image
        Returns:
            Dict(str):
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        image_name = kw.get("image_name")
        size = kw.get("size")
        cmd = self.base_cmd + f" resize --image {image_name} --size {size}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def rm(self, **kw):
        """
        Removes the block device image.
        kw(dict): Key/value pairs that needs to be provided to the installer
            Example::
            Supported keys:
                image_name(str) : name of the image that should be removed
                pool_name(str)  : name of the pool from which image should be retreived(optional)
        Returns:
            Dict(str):
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        image_name = kw.get("image_name")
        if kw.get("pool_name"):
            pool_name = kw.get("pool_name")
            cmd = self.base_cmd + f" rm {image_name} -p {pool_name}"
        else:
            cmd = self.base_cmd + f" rm {image_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def flatten(self, **kw):
        """
        Flattens the snapshot.
        kw(dict): Key/value pairs that needs to be provided to the installer
            Example::
            Supported keys:
                pool_name(str)      : name of the pool
                image_name(str)     : name of the image
                snap_name(str)      : name of the snapshot
        Returns:
            Dict(str):
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        image_name = kw.get("image_name")
        pool_name = kw.get("pool_name")
        cmd = self.base_cmd + f" flatten {pool_name}/{image_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def clone(self, **kw):
        """
        Clones the snapshot.
        kw(dict): Key/value pairs that needs to be provided to the installer
            Example::
            Supported keys:
                pool_name(str)         : name of the pool
                parent_image_name(str) : name of the parent image
                child_image_name(str)  : name of the child image
                snap_namestr)          : name of the snapshot
        Returns:
            Dict(str):
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        parent_image_name = kw.get("parent_image_name")
        child_image_name = kw.get("child_image_name")
        pool_name = kw.get("pool_name")
        snap_name = kw.get("snap_name")
        cmd = (
            self.base_cmd
            + f" clone {pool_name}/{parent_image_name}@{snap_name} {pool_name}/{child_image_name}"
        )
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def children(self, **kw):
        """
        Lists the children of a snapshot.
        kw(dict): Key/value pairs that needs to be provided to the installer
            Example::
            Supported keys:
                pool_name(str)  : name of the pool
                image_name(str) : name of the image
                snap_name(str)  : name of the snapshot
        Returns:
            Dict(str):
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        image_name = kw.get("image_name")
        pool_name = kw.get("pool_name")
        snap_name = kw.get("snap_name")
        cmd = self.base_cmd + f" children {pool_name}/{image_name}@{snap_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def bench(self, **kw):
        """
        This method is used to generate a series of IOs to the image and measure the IO throughput and latency.
        Args:
          kw(dict): Key/value pairs that needs to be provided to the installer
          Example:
            Supported keys:
              io-type(str): can be read | write | readwrite | rw.
              image_name(str): name of the image.
              pool_name(str): name of the pool.
        Returns:
            Dict(str):
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        kw_copy = deepcopy(kw)
        image_name = kw_copy.pop("image_name")
        pool_name = kw_copy.pop("pool_name")
        io_type = kw_copy.pop("io-type")
        cmd_args = core_utils.build_cmd_args(kw=kw_copy)
        cmd = (
            self.base_cmd
            + f" bench {image_name}/{pool_name} --io-type {io_type}"
            + cmd_args
        )
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
