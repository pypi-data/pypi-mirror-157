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


class Realm:
    """
    This module This module provides CLI interface to manage realm of the object gateway service.
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " realm"

    def create(self, **kw):
        """
        Creates a realm.
        If the realm is default if condition evaluates to true the realm will be set to default.
        otherwise else section executes and may have to specify the realm name each time we create zone_group and zone.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              rgw-realm(str): Takes the realm name as input.
              default(bool): True to create default realm , False for non-default realm.

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        realm_name = kw.get("rgw-realm")
        default = kw.get("default")
        if default:
            cmd = self.base_cmd + f" create --rgw-realm={realm_name} --default"
        else:
            cmd = self.base_cmd + f" create --rgw-realm={realm_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def delete(self, **kw):
        """
        To delete a realm, execute realm delete and specify the realm name.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              rgw-realm(str): Takes the realm name as input.

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        realm_name = kw.get("rgw-realm")
        cmd = self.base_cmd + f" delete --rgw-realm={realm_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def get_(self, **kw):
        """
        Takes a realm name as an input to fetch the details of the realm.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              rgw-realm(str): Takes the realm name as input.

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        realm_name = kw.get("rgw-realm")
        cmd = self.base_cmd + f" get --rgw-realm={realm_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def default_(self, **kw):
        """
        Takes realm name as an input to set the realm as default one.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              rgw-realm(str): Takes the realm name as input.

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        realm_name = kw.get("rgw-realm")
        cmd = self.base_cmd + f" default --rgw-realm={realm_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def list_(self, **kw):
        """
        This will list all the realms.
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

    def list_periods(self, **kw):
        """
        This will list all the realm periods.
        Args:
          None

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " list-periods"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def rename(self, **kw):
        """
        Renames a realm.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              rgw-realm(str): Takes the realm name as input.
              realm-new-name(str): Takes the new realm name as input.

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        realm_name = kw.get("rgw-realm")
        new_realm_name = kw.get("realm-new-name")
        cmd = (
            self.base_cmd
            + f" rename --rgw-realm={realm_name} --realm-new-name={new_realm_name}"
        )
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def set_(self, **kw):
        """
        Takes realm name and infile name as an input to set the realm.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              rgw-realm(str): Takes the realm name as input.
              infile(str): Takes this json file as an input.

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        realm_name = kw.get("rgw-realm")
        in_file = kw.get("infile")
        cmd = self.base_cmd + f" set --rgw-realm={realm_name} --infile={in_file}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def pull(self, **kw):
        """
        To pull a realm from the node containing the master zone group and master zone.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              url(str) : url to the master zone.
              access-key(str): The secondary zones will require them to authenticate with the master zone.
              secret-key(str): The secondary zones will require them to authenticate with the master zone.

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        url = kw.get("url")
        access_key = kw.get("access-key")
        secret_key = kw.get("secret-key")
        cmd = (
            self.base_cmd
            + f" pull --url={url} --access-key={access_key} --secret={secret_key}"
        )
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def get_default(self, **kw):
        """
        lists out the default realm.
        Args:
          None

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " get-default"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
