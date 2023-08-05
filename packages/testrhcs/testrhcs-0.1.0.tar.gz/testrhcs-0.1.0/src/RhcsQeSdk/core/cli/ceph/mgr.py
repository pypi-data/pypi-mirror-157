import logging

import RhcsQeSdk.core.cli.fabfile as fabfile
from RhcsQeSdk.core.cli.ceph.module import Module

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s"
)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)


class Mgr:
    """
    This module provides CLI interface to manage the MGR service.
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " mgr"
        self.module = Module(self.base_cmd)

    def services(self, **kw):
        """
        This method is used to see the addresses of modules with IP and Port number.
        Args:
          None

         Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " services"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
