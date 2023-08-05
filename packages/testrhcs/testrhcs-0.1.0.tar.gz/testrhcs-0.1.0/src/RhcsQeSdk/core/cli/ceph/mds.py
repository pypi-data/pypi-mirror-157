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


class Mds:
    """
    This module provides CLI interface for management of metadata server configuration and administration.
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " mds"

    def rm_compat(self, **kw):
        """
        This method is used to remove compatible feature.
        Args:
          kw(Dict): Key/value pairs that needs to be provided to the installer.
          Example::
            Supported Keys:
              rank(int) : Rank of the MDS daemon.

        Returns:
          Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        rank = kw.get("rank")
        cmd = self.base_cmd + f" compat rm_compat {rank}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def rm_incompat(self, **kw):
        """
        This method is used to remove incompatible feature.
        Args:
          kw(Dict): Key/value pairs that needs to be provided to the installer.
          Example::
            Supported Keys:
              rank(int) : Rank of the MDS daemon.

        Returns:
          Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        rank = kw.get("rank")
        cmd = self.base_cmd + f" compat rm_incompat {rank}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def compat_show(self, **kw):
        """
        This method is used to show mds compatibility settings.
        Args:
          None

        Returns:
          Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " compat show"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def fail(self, **kw):
        """
        This method is used to force mds to status fail.
        Args:
          kw(Dict): Key/value pairs that needs to be provided to the installer.
          Example::
            Supported Keys:
              rank(int) : Rank of the MDS daemon.

        Returns:
          Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        rank = kw.get("rank")
        cmd = self.base_cmd + f" fail {rank}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def rm(self, **kw):
        """
        This method is used to remove inactive mds.
        Args:
          kw(Dict): Key/value pairs that needs to be provided to the installer.
          Example::
            Supported Keys:
              rank(int) : Rank of the MDS daemon.
              name(str) : Name of the file system.

        Returns:
          Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        name = kw.get("name", "")
        rank = kw.get("rank", "")
        cmd = self.base_cmd + f" rm {name} {rank}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def rmfailed(self, **kw):
        """
        This method is used to remove failed mds.
        Args:
          kw(Dict): Key/value pairs that needs to be provided to the installer.
          Example::
            Supported Keys:
              rank(int) : Rank of the MDS daemon.

        Returns:
          Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        rank = kw.get("rank")
        cmd = self.base_cmd + f" rmfailed {rank}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def stat(self, **kw):
        """
        This method is used to show MDS status.
        Args:
          kw(Dict): Key/value pairs that needs to be provided to the installer.
          Example::
            Supported Keys:
              format(str): This is an optional key that helps to prettify and format the JSON data and print it.
        Returns:
          Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " stat" + core_utils.build_cmd_args(kw=kw)
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def repaired(self, **kw):
        """
        This method is used to mark a damaged MDS rank as no longer damaged.
        Args:
          kw(Dict): Key/value pairs that needs to be provided to the installer.
          Example::
            Supported Keys:
              rank(int) : Rank of the MDS daemon.

        Returns:
          Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        rank = kw.get("rank")
        cmd = self.base_cmd + f" repaired {rank}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def allow_new_snaps(self, **kw):
        """
        This method is used to enable snapshots.
        Args:
          None

        Returns:
          Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " set allow_new_snaps true --yes-i-really-mean-it"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def deactivate(self, **kw):
        """
        This method is used to deactivate the active MDS daemon.
        Args:
          kw(Dict): Key/value pairs that needs to be provided to the installer.
          Example::
            Supported Keys:
              role(str): Replace <role> with "name of the Ceph File System:rank".

        Returns:
          Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        role = kw.get("role")
        cmd = self.base_cmd + f" deactivate {role}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def add_data_pool(self, **kw):
        """
        This method is used to add the newly created pool under the control of the metadata servers.
        Args:
          kw(Dict): Key/value pairs that needs to be provided to the installer.
          Example::
            Supported Keys:
              name(str): name of the newly created pool.

        Returns:
          Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        name = kw.get("name")
        cmd = self.base_cmd + f" add_data_pool {name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
