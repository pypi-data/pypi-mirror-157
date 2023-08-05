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


class RolePolicy:
    """
    This module manages role policies
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " role-policy"

    def put(self, **kw):
        """
        Add/update permission policy to role.

        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              role-name(str): Name of the role.
              policy-name(str): Name of the policy.
              policy-doc(str) : The Permission policy document.
              infile(str)     : passing policy-doc as a file. Alternate to policy_doc

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        kw_copy = deepcopy(kw)
        role_name = kw_copy.pop("role-name", "")
        policy_name = kw_copy.pop("policy-name", "")
        cmd = f"{self.base_cmd} put --role-name={role_name} --policy-name={policy_name}"
        cmd = cmd + core_utils.build_cmd_args(kw=kw_copy)
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def list_(self, **kw):
        """
        List the policies attached to a role.

        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              role-name(str): Name of the role.

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        role_name = kw.get("role-name")
        cmd = f"{self.base_cmd} list --role-name={role_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def get_(self, **kw):
        """
        Get the specified inline policy document embedded with the given role.

        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              role-name(str): Name of the role.
              policy-name(str): Name of the policy.

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        role_name = kw.get("role-name")
        policy_name = kw.get("policy-name")
        cmd = f"{self.base_cmd} get --role-name={role_name} --policy-name={policy_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def delete(self, **kw):
        """
        Remove the policy attached to a role

        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              role-name(str): Name of the role.
              policy-name(str): Name of the policy.

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        role_name = kw.get("role-name")
        policy_name = kw.get("policy-name")
        cmd = f"{self.base_cmd} delete --role-name={role_name} --policy-name={policy_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
