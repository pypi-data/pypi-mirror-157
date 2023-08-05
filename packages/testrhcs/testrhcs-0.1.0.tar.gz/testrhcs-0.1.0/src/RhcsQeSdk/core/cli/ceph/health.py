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


class Health:
    """This module provides CLI interface to implement ceph health associated commands."""

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " health"

    def detail(self, **kw):
        """
        The command detail will display the clusters health in detail.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:

            None

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " detail"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def unmute(self, **kw):
        """
        The command unmute will unmute a type of health check.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:

            code(str): the health check code.

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        code = kw.get("code", "")
        cmd = self.base_cmd + f" unmute {code}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def mute(self, **kw):
        """
        The command mute will mute a type of health check.

        Args:
            kw(Dict): Key/value pairs that needs to be provided to the installer.
            Example::
            Supported Keys:

            code(str): the health check code.
            muting_time(str): time duration the health check code has to be muted.(optional)

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        code = kw.get("code", "")
        muting_time = kw.get("muting_time", "")
        cmd = self.base_cmd + f" mute {code} {muting_time}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
