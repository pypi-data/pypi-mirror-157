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


class Tier:
    """Subcommand tier is used for managing tiers. It uses some additional subcommands."""

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " tier"

    def add_(self, **kw):
        """
        Subcommand add adds the tier <tierpool> (the second one) to base pool <pool> (the first one).

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
                poolnames(list)           : list of pool names.two poolnames actually.
                                            the second is tierpool and the first is pool
                force-nonempty(boolean)   : True or False

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        kw_copy = deepcopy(kw)
        pool_names = kw_copy.pop("poolnames", "")
        cmd = f"{self.base_cmd} add {pool_names[0]} {pool_names[1]}"
        cmd = cmd + core_utils.build_cmd_args(kw=kw_copy)
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def add_cache(self, **kw):
        """
        Subcommand add-cache adds a cache <tierpool> (the second one) of size <size>
        to existing pool <pool> (the first one).

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
                poolnames(list)           : list of pool names.two poolnames actually.
                                            the second is tierpool and the first is pool
                size(int)        : cache size

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        pool_names = kw.get("poolnames")
        size = kw.get("size")
        cmd = f"{self.base_cmd} add-cache {pool_names[0]} {pool_names[1]} {size}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def cache_mode(self, **kw):
        """
        Subcommand cache-mode specifies the caching mode for cache tier <pool>.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
              poolname(str) : name of the pool.
              option(str)    : writeback|readproxy|readonly|none
        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        pool_name = kw.get("poolname")
        option = kw.get("option")
        cmd = f"{self.base_cmd} cache-mode {pool_name} {option}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def remove_(self, **kw):
        """
        Subcommand remove removes the tier <tierpool> (the second one) from base pool <pool> (the first one).

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
              poolnames(list) :  list of pool names.two poolnames actually.
                                 the second is tierpool and the first is pool

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        pool_names = kw.get("poolnames")
        cmd = f"{self.base_cmd} remove {pool_names[0]} {pool_names[1]}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def remove_overlay(self, **kw):
        """
        Subcommand remove-overlay removes the overlay pool for base pool <pool>.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
              poolname(str) : name of the pool.

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        pool_name = kw.get("poolname")
        cmd = f"{self.base_cmd} remove-overlay {pool_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def set_overlay(self, **kw):
        """
        Subcommand set-overlay set the overlay pool for base pool <pool> to be <overlaypool>.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:
              poolnames(list) :  list of pool names.two poolnames actually.
                                 the second is tierpool and the first is pool

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        pool_names = kw.get("poolnames")
        cmd = f"{self.base_cmd} set-overlay {pool_names[0]} {pool_names[1]}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
