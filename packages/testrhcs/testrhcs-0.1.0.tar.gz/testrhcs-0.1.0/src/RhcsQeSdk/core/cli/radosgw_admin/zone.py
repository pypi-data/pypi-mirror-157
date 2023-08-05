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


class Zone:
    """
    This module provides CLI interface for zone management of object gateway service.
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " zone"

    def create(self, **kw):
        """
        To create a zone, specify a zone name.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              rgw-zone(str) : Takes the zone name as an input.
              rgw-zonegroup(str) : Takes the zone group name as an input.
              endpoints(str) : combination of an endpoint and port number.
              default(bool) : True to create default zone , False for non-default zone.
              rgw-realm(str): Takes the realm name as input.
              access-key(str):The secondary zones will require them to authenticate with the master zone.
              secret-key(str):The secondary zones will require them to authenticate with the master zone.

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        kw_copy = deepcopy(kw)
        zonegroup_name = kw_copy.pop("rgw-zonegroup", "")
        rgw_zone = kw_copy.pop("rgw-zone", "")
        cmd_args = core_utils.build_cmd_args(kw=kw_copy)
        cmd = (
            self.base_cmd
            + f" create --rgw-zonegroup={zonegroup_name} --rgw-zone={rgw_zone}"
            + cmd_args
        )
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def delete(self, **kw):
        """
        To delete a zone, first remove it from the zonegroup.
        Then, update the period and delete the zone.
        Then again re-update the period.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              rgw-zone(str) : Takes the zone name as an input.

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        rgw_zone = kw.get("rgw-zone")
        cmd = self.base_cmd + f" delete --rgw-zone={rgw_zone}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def modify(self, **kw):
        """
        To modify a zone, specify the zone name and the parameters you wish to modify.
        If the cluster was configured to run in an active-passive configuration, the secondary zone is a read-only zone.
        Remove the --read-only status to allow the zone to receive write operations.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              rgw-zone(str) : Takes the zone name as an input.
              access-key(str): The secondary zones will require them to authenticate with the master zone.
              secret-key(str): The secondary zones will require them to authenticate with the master zone.
              endpoints(str): url to the master zone.
              read-only(str): set the --read-only status to allow the zone to receive write operations.

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")

        cmd = self.base_cmd + " modify " + core_utils.build_cmd_args(kw=kw)
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def set_(self, **kw):
        """
        It Set zone cluster params.
        To set a zone, create a JSON object consisting of the pools, save the object to a file (e.g., zone.json).
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              rgw-zone(str) : Takes the zone name as an input.
              infile(JSON) : Takes the Json file as an input.

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        rgw_zone = kw.get("rgw-zone")
        in_file = kw.get("infile")
        cmd = self.base_cmd + f" set --rgw-zone={rgw_zone} --infile={in_file}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def rename(self, **kw):
        """
        To rename a zone, specify the zone name and the new zone name.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              rgw-zone(str) : Takes the zone name as an input.
              zone-new-name(str) : Takes the new zone name as an input.

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        rgw_zone = kw.get("rgw-zone")
        zone_new_name = kw.get("zone-new-name")
        cmd = (
            self.base_cmd
            + f" rename --rgw-zone={rgw_zone} --zone-new-name={zone_new_name}"
        )
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def get_(self, **kw):
        """
        This method is used to fetch the configuration of a zone.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              rgw-zone(str) : Takes the zone name as an input.

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        rgw_zone = kw.get("rgw-zone")
        cmd = self.base_cmd + f" get --rgw-zone={rgw_zone}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def list_(self, **kw):
        """
        List the zones in a cluster.
        Args:
          None

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " list"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
