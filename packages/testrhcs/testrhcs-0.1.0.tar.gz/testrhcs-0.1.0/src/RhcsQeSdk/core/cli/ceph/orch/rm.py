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


base_cmd_osd = None
rm_obj = None


class OsdRm:
    """
    This module provides CLI interface to ceph orch osd rm sub-commands.
    """

    def __new__(self, **kw):
        """To Remove OSD daemons.
        <osd_id>... [--replace] [--force] [--zap]
        Args:
        kw: Key value pair of method arguments
            Example::
            Supported keys:
                osd-id: id of osd to be removed.
                replace(bool): Replace osd.
                force(bool): force removal.
                zap(bool): zap disks.
        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")

        kw_copy = deepcopy(kw)
        osd_id = kw_copy.pop("osd-id", "")
        global base_cmd_osd
        cmd_args = core_utils.build_cmd_args(kw=kw_copy)

        cmd = base_cmd_osd + f" rm {osd_id}{cmd_args}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    @staticmethod
    def status(**kw):
        """Wrapper for command ceph orch osd status

        Status of OSD removal operation.
        Args:
            kw(dict): Key/value pairs that needs to be provided to the installer
            Example::
            Supported keys:
                format(str): {plain|json|json-pretty|yaml|xml-pretty|xml}
        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        global base_cmd_osd
        cmd_args = core_utils.build_cmd_args(kw=kw)

        cmd = base_cmd_osd + f" rm status{cmd_args}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    @staticmethod
    def stop(**kw):
        """Wrapper for command ceph orch osd stop.

        Cancel ongoing OSD removal operation.
        Args:
            kw(dict): Key/value pairs that needs to be provided to the installer
            Example::
            Supported keys:
                osd-id: id of osd of which removal to be stopped.
        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")

        kw_copy = deepcopy(kw)
        osd_id = kw_copy.pop("osd-id", "")
        global base_cmd_osd

        cmd = base_cmd_osd + f" rm stop {osd_id}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))


class Rm:
    """
    This module provides abstract CLI interface to ceph orch osd rm sub-commands.
    """

    def __new__(self, base_cmd):
        global base_cmd_osd
        base_cmd_osd = base_cmd
        self.base_cmd = base_cmd + " rm"
        return OsdRm
