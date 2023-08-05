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


class Subuser:
    """
    This module provides CLI interface for commands used for RGW subuser management.
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " subuser"

    def create(self, **kw):
        """Create a new subuser (primarily useful for clients using the Swift API).
        Args:
                uid(str) : User ID
                access(str) : [ read | write | readwrite | full ]
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        uid = kw.get("uid", "")
        cmd = (
            self.base_cmd
            + " create"
            + f" --uid={uid} --subuser={uid} "
            + core_utils.build_cmd_args(kw=kw)
        )
        logger.info(f"Running commmand {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def modify(self, **kw):
        """Modify existing subuser.
        Args:
                uid(str) : User ID
                access(str) : [ read | write | readwrite | full ]
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        uid = kw.get("uid", "")
        cmd = (
            self.base_cmd
            + " modify"
            + f" --uid={uid} --subuser={uid} "
            + core_utils.build_cmd_args(kw=kw)
        )
        logger.info(f"Running commmand {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def rm(self, **kw):
        """Remove a new subuser.
        Args:
                uid(str) : User ID
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        uid = kw.get("uid", "")
        cmd = self.base_cmd + " rm" + f" --subuser={uid}"
        logger.info(f"Running commmand {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
