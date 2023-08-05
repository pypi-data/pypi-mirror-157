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


class Config:
    """
    This module provides CLI interface to configure cluster via ceph config.
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " config"

    def dump(self, **kw):
        """
        Subcommand dump to dump all options for the cluster.

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " dump"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def ls(self, **kw):
        """
        Subcommand ls to list all option names for the cluster.

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " ls"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def help(self, **kw):
        """
        Subcommand help to describe the specified configuration option.

        Args:
            kw(dict) :       Key/value pairs
            Supported keys:
              option(str) : option to be described

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        option = kw.get("option", "")
        cmd = self.base_cmd + f" help {option}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def get_(self, **kw):
        """
        Subcommand get to dump the option(s) for the specified entity.

        Args:
            kw(dict) :       Key/value pairs
            Supported keys:
              who(str) : entity
              option(str) : option to be described

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        who = kw.get("who", "")
        option = kw.get("option", "")
        cmd = self.base_cmd + f" get {who} {option}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def show(self, **kw):
        """
        Subcommand show to display the running configuration of the specified entity.

        Args:
            kw(dict) :       Key/value pairs
            Supported keys:
              who(str) : entity

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        who = kw.get("who", "")
        cmd = self.base_cmd + f" show {who}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def show_with_defaults(self, **kw):
        """
        Subcommand show-with-defaults to display the running configuration along with the
        compiled-in defaults of the specified entity.

        Args:
            kw(dict) :       Key/value pairs
            Supported keys:
              who(str) : entity

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        who = kw.get("who", "")
        cmd = self.base_cmd + f" show-with-defaults {who}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def set_(self, **kw):
        """
        Subcommand set to set an option for one or more specified entities.

        Args:
            kw(dict) :       Key/value pairs
            Supported keys:
              who(str)    : entity
              option(str) : option to be described
              value(str)  :  value for an option

        Examples:
            ceph config set mgr target_max_misplaced_ratio .07
            ceph config set mgr mgr/balancer/sleep_interval 60

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        who = kw.get("who", "")
        option = kw.get("option", "")
        value = kw.get("value", "")
        cmd = self.base_cmd + f" set {who} {option} {value}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def rm(self, **kw):
        """
        Subcommand rm to clear an option for one or more entities.

        Args:
            kw(dict) :       Key/value pairs
            Supported keys:
              who(str) : entity
              option(str) : option to be described

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        who = kw.get("who", "")
        option = kw.get("option", "")
        cmd = self.base_cmd + f" rm {who} {option}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def log(self, **kw):
        """
        Subcommand log to show recent history of config changes.

        Args:
            kw(dict) :       Key/value pairs
            Supported keys:
              count(int) : no of recent logs. default is 10

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        count = kw.get("count", 10)
        cmd = self.base_cmd + f" log {count}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def reset(self, **kw):
        """
        Subcommand reset to revert configuration to the specified historical version.

        Args:
            kw(dict) :       Key/value pairs
            Supported keys:
              version(float) : historical version to which configuration is reverted

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        version = kw.get("version")
        cmd = self.base_cmd + f" reset {version}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def assimilate_conf(self, **kw):
        """
        Subcommand assimilate-conf to assimilate options from stdin, and return a new, minimal conf file.

        Args:
            kw(dict) :       Key/value pairs
            Supported keys:
              input_file(str) : Input file
              output_file(str): Output file
        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        input_file = kw.get("input_file")
        output_file = kw.get("output_file")
        cmd = self.base_cmd + f" assimilate-conf -i {input_file} -o {output_file}"
        logger.info(f"Running command {cmd}")

        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def generate_minimal_conf(self, **kw):
        """
        Subcommand generate-minimal-conf to generate a minimal ceph.conf file,
        which can be used for bootstrapping a daemon or a client.

        Args:
            kw(dict) :       Key/value pairs
            Supported keys:
              path(str) : minimal-config-path

        Returns:
            Dict(str)
            A mapping of host strings of the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        path = kw.get("path")
        cmd = self.base_cmd + f" generate-minimal-conf > {path}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
