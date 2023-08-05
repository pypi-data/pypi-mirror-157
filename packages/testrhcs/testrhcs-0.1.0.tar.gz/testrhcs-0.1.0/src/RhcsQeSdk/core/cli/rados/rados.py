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


class Rados:
    """This module provides CLI interface to manage rados operations."""

    def __init__(self, base_cmd=""):
        self.base_cmd = f"{base_cmd}rados"

    def df(self, **kw):
        """
        The command stats will display the pools utilizations statistics.

        Args:
            None

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " df"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def lspools(self, **kw):
        """
        List pools.
        Args:
          None

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " lspools"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def cppool(self, **kw):
        """
        Copy content of a pool.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              pool_name(str) : Source pool name.
              dest_pool(str) : Destination pool.

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        pool_name = kw.get("pool_name", "")
        dest_pool = kw.get("dest_pool", "")
        cmd = self.base_cmd + f" cppool {pool_name} {dest_pool}"
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def purge(self, **kw):
        """Remove all objects from pool <pool_name> without removing it.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              pool_name(str) : Source pool name.

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        pool_name = kw.get("pool_name", "")
        cmd = self.base_cmd + f" purge {pool_name} --yes-i-really-really-mean-it"
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def ls(self, **kw):
        """
        List objects in pool.
        Args:
          None

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " ls"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def lssnap(self, **kw):
        """
        This method is used to list snaps.
        Args:
          None

        Returns:
          Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " lssnap"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def mksnap(self, **kw):
        """
        Create snap <snap_name>.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              snap_name(str) : Snap name.

        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        snap_name = kw.get("snap_name", "")
        cmd = self.base_cmd + f" mksnap {snap_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def rmsnap(self, **kw):
        """
        Remove snap <snap_name>.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              snap_name(str) : Snap name.

        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        snap_name = kw.get("snap_name", "")
        cmd = self.base_cmd + f" rmsnap {snap_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def get_(self, **kw):
        """
        Fetch object.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              obj_name(str) : Object name.
              outfile(str) : Outfile.

        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        obj_name = kw.get("obj_name", "")
        outfile = kw.get("outfile", "")
        cmd = self.base_cmd + f" get {obj_name} {outfile}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def put_(self, **kw):
        """
        write object with start offset (default:0).
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              obj_name(str) : Object name.
              infile(str) : Infile.
              offset(str) : Offset(optional)

        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        kw_copy = deepcopy(kw)
        obj_name = kw_copy.pop("obj_name", "")
        infile = kw_copy.pop("infile", "")
        cmd = (
            self.base_cmd
            + f" put {obj_name} {infile}"
            + core_utils.build_cmd_args(kw=kw_copy)
        )
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def append_(self, **kw):
        """
        Append object.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              obj_name(str) : Object name.
              infile(str) : Infile.

        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        obj_name = kw.get("obj_name", "")
        infile = kw.get("infile", "")
        cmd = self.base_cmd + f" append {obj_name} {infile}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def truncate(self, **kw):
        """
        Truncate object.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              obj_name(str) : Object name.
              length(str) : Length

        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        obj_name = kw.get("obj_name", "")
        length = kw.get("length", "")
        cmd = self.base_cmd + f" truncate {obj_name} {length}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def create(self, **kw):
        """
        Create object.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              obj_name(str) : Object name.

        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        obj_name = kw.get("obj_name", "")
        cmd = self.base_cmd + f" create {obj_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def rm(self, **kw):
        """
        Remove object(s).
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              obj_name(str) : Object name.
              force-full : Force no matter full or not(optional).

        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        obj_name = kw.get("obj_name", "")
        cmd = self.base_cmd + f" rm {obj_name}" + core_utils.build_cmd_args(kw=kw)
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def cp(self, **kw):
        """
        Copy object.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              obj_name(str) : Object name.
              target-obj(str) : Target object(optional).

        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        obj_name = kw.get("obj_name", "")
        cmd = self.base_cmd + f" cp {obj_name}" + core_utils.build_cmd_args(kw=kw)
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def listxattr(self, **kw):
        """
        List all extended attributes of an object.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              obj_name(str) : Object name.

        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        obj_name = kw.get("obj_name", "")
        cmd = self.base_cmd + f" listxattr {obj_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def getxattr(self, **kw):
        """
        Dump the extended attribute value of attr of an object.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              obj_name(str) : Object name.
              attr(str) : Attribute

        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        obj_name = kw.get("obj_name", "")
        attr = kw.get("attr", "")
        cmd = self.base_cmd + f" getxattr {obj_name} {attr}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def setxattr(self, **kw):
        """
        Set the value of attr in the extended attributes of an object.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              obj_name(str) : Object name.
              attr(str) : Attribute
              value(str) : Value

        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        obj_name = kw.get("obj_name", "")
        attr = kw.get("attr", "")
        value = kw.get("value", "")
        cmd = self.base_cmd + f" setxattr {obj_name} {attr} {value}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def rmxattr(self, **kw):
        """
        Set the value of attr in the extended attributes of an object..
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              obj_name(str) : Object name.
              attr(str) : Attribute

        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        obj_name = kw.get("obj_name", "")
        attr = kw.get("attr", "")
        cmd = self.base_cmd + f" rmxattr {obj_name} {attr}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def stat(self, **kw):
        """
        Stat the named object.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              obj_name(str) : Object name.

        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        obj_name = kw.get("obj_name", "")
        cmd = self.base_cmd + f" stat {obj_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def stat2(self, **kw):
        """
        Stat2 the named object (with high precision time).
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              obj_name(str) : Object name.

        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        obj_name = kw.get("obj_name", "")
        cmd = self.base_cmd + f" stat2 {obj_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def touch(self, **kw):
        """
        Change the named object modification time.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              obj_name(str) : Object name.
              timestamp(str) : Timestamp(optional).

        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        obj_name = kw.get("obj_name", "")
        cmd = self.base_cmd + f" touch {obj_name}" + core_utils.build_cmd_args(kw=kw)
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def mapext(self, **kw):
        """
        Used to map the object name.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              obj_name(str) : Object name.

        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        obj_name = kw.get("obj_name", "")
        cmd = self.base_cmd + f" mapext {obj_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def rollback(self, **kw):
        """
        This method is used to roll back object to snap <snap-name>
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              obj_name(str)  : name of the object.
              snap_name(str) : name of the snap.
              base_pool(str): name of the pool.

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        base_pool = kw.get("base_pool", "")
        obj_name = kw.get("obj_name", "")
        snap_name = kw.get("snap_name", "")
        cmd = self.base_cmd + f" -p {base_pool} rollback {obj_name} {snap_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def listsnaps(self, **kw):
        """
        This method is used to list the snapshots of this object.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              base_pool(str): name of the pool.
              obj_name(str)  : name of the object.

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        base_pool = kw.get("base_pool", "")
        obj_name = kw.get("obj_name", "")
        cmd = self.base_cmd + f"-p {base_pool} listsnaps {obj_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def bench(self, **kw):
        """
        This method is used to benchmark for seconds.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              seconds(int): number of seconds.
              mode(str): write|seq|rand.
              concurrent_operations(str): set number of concurrent I/O operations.(default is 16)
              no-cleanup(bool): set this to true to run a write benchmark with the no-cleanup option.(optional)
              run_name(str): used to benchmark a workload test from multiple clients(optional)
                             (default is 'benchmark_last_metadata')
              no_hints(bool): Set this to true to enable the effect of this flag.(optional)
              reuse_bench(bool): Set this to true to enable the effect of this flag.(optional)
              obj_size(int): default object size is 4MB.
              base_pool(str): name of the pool.

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        kw_copy = deepcopy(kw)
        base_pool = kw_copy.pop("base_pool", "")
        seconds = kw_copy.pop("seconds", "")
        mode = kw_copy.pop("mode", "")
        concurrent_operations = kw_copy.pop("concurrent_operations", 16)
        obj_size = kw.pop("obj_size", "4MB")
        cmd_args = core_utils.build_cmd_args(kw=kw_copy)
        cmd = (
            self.base_cmd
            + f" -p {base_pool} bench {seconds} {mode} -b {obj_size} -t {concurrent_operations}"
            + {cmd_args}
        )
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def cleanup(self, **kw):
        """
        This method is used to clean up a previous benchmark operation.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              run_name(str): used to benchmark a workload test from multiple clients
                             (default is 'benchmark_last_metadata')
              prefix(str): prefix
              base_pool(str): name of the pool.

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        run_name = kw.get("run_name", "benchmark_last_metadata")
        base_pool = kw.get("base_pool", "")
        prefix = kw.get("prefix")
        cmd = (
            self.base_cmd
            + f" -p {base_pool} cleanup --run-name {run_name} --prefix {prefix}"
        )
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def load_gen(self, **kw):
        """
        This method is used to generate load on the cluster.
        Args:
          base_pool(str): name of the pool.
          num_objects(int): number of objects.(optional)
          min_object_size(str): minimum object size.(optional)
          max_object_size(str): maximum object size.(optional)
          max_ops(int): Max number of operations.(optional)
          min_op_len(str) :  Min io size of operations.(optional)
          max_op_len(str) :  Max io size of operations.(optional)
          max_backlog(int): Max backlog size.(optional)
          percent(int): Percent of operations that are read.(optional)
          target_throughput(int): Target throughput (in bytes).(optional)
          run_length(int): Total time (in seconds).(optional)
          offset_align(str): At what boundary to align random op offsets.(optional)

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        kw_copy = deepcopy(kw)
        base_pool = kw_copy.pop("base_pool", "")
        cmd_args = core_utils.build_cmd_args(kw=kw_copy)
        cmd = self.base_cmd + f" -p {base_pool} load-gen" + cmd_args
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def listomapkeys(self, **kw):
        """
        This method is used to list the keys in the object map.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              base_pool(str): name of the pool.
              obj_name(str): name of the object.

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        obj_name = kw.get("obj_name", "")
        base_pool = kw.get("base_pool", "")
        cmd = self.base_cmd + f" -p {base_pool} listomapkeys {obj_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def listomapvals(self, **kw):
        """
        This method is used to list the keys and vals in the object map.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              base_pool(str): name of the pool.
              obj_name(str): name of the object.

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        base_pool = kw.get("base_pool", "")
        obj_name = kw.get("obj_name", "")
        cmd = self.base_cmd + f" -p {base_pool} listomapvals {obj_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def getomapval(self, **kw):
        """
        This method is used to show the value for the specified key in the object's object map.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              base_pool(str): name of the pool.
              obj_name(str): name of the object.
              key(str): object map key.
              file(str): object map key file.
              out-file(bool): if set to false the value will be written to standard output.(optional)

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        kw_copy = deepcopy(kw)
        base_pool = kw_copy.pop("base_pool", "")
        obj_name = kw_copy.pop("obj_name", "")
        key = kw_copy.pop("key", "")
        cmd_args = core_utils.build_cmd_args(kw=kw_copy)
        cmd = self.base_cmd + f" -p {base_pool} getomapval {obj_name} {key}" + cmd_args
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def setomapval(self, **kw):
        """
        This method is used to set the value of key in the object map of object name.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              obj_name(str): name of the object.
              key(str): object map key.
              file(str): object map key file.
              value(bool): if set to false the value will be written to standard input.(optional)

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        kw_copy = deepcopy(kw)
        obj_name = kw_copy.pop("obj_name", "")
        key = kw_copy.pop("key", "")
        cmd_args = core_utils.build_cmd_args(kw=kw_copy)
        cmd = self.base_cmd + f" setomapval {obj_name} {key}" + cmd_args
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def rmomapkey(self, **kw):
        """
        This method is used to remove key from the object map of object name.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              base_pool(str): name of the pool.
              obj_name(str): name of the object.
              key(str): object map key.
              file(str): object map key file.

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        kw_copy = deepcopy(kw)
        base_pool = kw_copy.pop("base_pool", "")
        obj_name = kw_copy.pop("obj_name", "")
        key = kw_copy.pop("key", "")
        cmd_args = core_utils.build_cmd_args(kw=kw_copy)
        cmd = self.base_cmd + f" -p {base_pool} rmomapkey {obj_name} {key}" + cmd_args
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def clearomap(self, **kw):
        """
        This method is used to clear all the omap keys for the specified objects.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              obj_name(str): name of the object.
              base_pool(str): name of the pool.

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        kw_copy = deepcopy(kw)
        base_pool = kw_copy.pop("base_pool", "")
        obj_name = kw_copy.pop("obj_name", "")
        cmd_args = core_utils.build_cmd_args(kw=kw_copy)
        cmd = self.base_cmd + f" -p {base_pool} clearomap {obj_name}" + cmd_args
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def getomapheader(self, **kw):
        """
        This method is used to dump the hexadecimal value of the object map header of object name.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              obj_name(str): name of the object.
              base_pool(str): name of the pool.

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        base_pool = kw.get("base_pool", "")
        obj_name = kw.get("obj_name", "")
        cmd = self.base_cmd + f"-p {base_pool} getomapheader {obj_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def setomapheader(self, **kw):
        """
        This method is used to set the value of the object map header of object name.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              obj_name(str): name of the object.
              value(str): value of the object map header of object name.
              base_pool(str): name of the pool.

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        base_pool = kw.get("base_pool", "")
        obj_name = kw.get("obj_name", "")
        value = kw.get("value", "")
        cmd = self.base_cmd + f" -p {base_pool} setomapheader {obj_name} {value}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def watch(self, **kw):
        """
        This method is used to add watcher on this object.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              obj_name(str): name of the object.
              base_pool(str): name of the pool.

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        base_pool = kw.get("base_pool", "")
        obj_name = kw.get("obj_name", "")
        cmd = self.base_cmd + f" -p {base_pool} watch {obj_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def notify(self, **kw):
        """
        This method is used to notify watcher of this object with message.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              base_pool(str): name of the pool.
              obj_name(str): name of the object.
              message(str): message with which the watcher must be notified.

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        base_pool = kw.get("base_pool", "")
        obj_name = kw.get("obj_name", "")
        message = kw.get("message", "")
        cmd = self.base_cmd + f" -p {base_pool} notify {obj_name} {message}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def listwatchers(self, **kw):
        """
        This method is used to list the watchers of this object.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              base_pool(str): name of the pool.
              obj_name(str): name of the object.

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        base_pool = kw.get("base_pool", "")
        obj_name = kw.get("obj_name", "")
        cmd = self.base_cmd + f" -p {base_pool} listwatchers {obj_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def set_alloc_hint(self, **kw):
        """
        This method is used to set allocation hint for an object.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              base_pool(str): name of the pool.
              obj_name(str): name of the object.
              expected_object_size(str): expected object size.
              expected_write_size(str): expected write size.

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        obj_name = kw.get("obj_name", "")
        base_pool = kw.get("base_pool", "")
        expected_object_size = kw.get("expected_object_size")
        expected_write_size = kw.get("expected_write_size")
        cmd = (
            self.base_cmd
            + f" -p {base_pool} set-alloc-hint {obj_name} {expected_object_size} {expected_write_size}"
        )
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def set_redirect(self, **kw):
        """
        This method is used to set redirect target.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              base_pool(str): name of the pool.
              base_obj_name(str): name of the object.
              target_pool(str): target pool.
              target_object(str): name of the target object.

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        base_pool = kw.get("base_pool", "")
        base_obj_name = kw.get("base_obj_name")
        target_pool = kw.get("target_pool", "")
        target_object = kw.get("target_object", "")
        cmd = (
            self.base_cmd
            + f" -p {base_pool} set-redirect {base_obj_name} --target-pool {target_pool} {target_object}"
        )
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def set_chunk(self, **kw):
        """
        This method is used to convert an object to chunked object.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              base_pool(str): name of the pool.
              obj_name(str): name of the object.
              source_object(str): name of the source object.
              offset(str): start offset.
              length(str): total time (in seconds).
              target_pool(str): target pool.
              target_object(str): name of the target object.
              target_offset(str): taget offset.

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        base_pool = kw.get("base_pool", "")
        source_object = kw.get("source_object", "")
        offset = kw.get("offset", "")
        length = kw.get("length")
        target_pool = kw.get("target_pool", "")
        target_object = kw.get("target_object", "")
        target_offset = kw.get("target_offset", "")
        cmd = (
            self.base_cmd
            + f" -p {base_pool} set-chunk {source_object} {offset} {length}"
            + f"--target-pool {target_pool} {target_object} {target_offset}"
        )
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def tier_promote(self, **kw):
        """
        This method is used to promote the object to the base tier.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              obj_name(str): name of the object.
              base_pool(str): name of the pool.

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        base_pool = kw.get("base_pool", "")
        obj_name = kw.get("obj_name", "")
        cmd = self.base_cmd + f" -p {base_pool} tier-promote {obj_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def unset_manifest(self, **kw):
        """
        This method is used to unset redirect or chunked object.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              obj_name(str): name of the object.
              base_pool(str): name of the pool.

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        base_pool = kw.get("base_pool", "")
        obj_name = kw.get("obj_name", "")
        cmd = self.base_cmd + f" -p {base_pool} unset-manifest {obj_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def tier_flush(self, **kw):
        """
        This method is used to flush the chunked object.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              obj_name(str): name of the object.
              base_pool(str): name of the pool.

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        base_pool = kw.get("base_pool", "")
        obj_name = kw.get("obj_name", "")
        cmd = self.base_cmd + f" -p {base_pool} tier-flush {obj_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def tier_evict(self, **kw):
        """
        This method is used to evict the chunked object.
        Args:
          kw (Dict): Key/value pairs that needs to be provided to the installer.
          Example:
            Supported keys:
              obj_name(str): name of the object.

        Returns:
            Dict(str)
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")
        base_pool = kw.get("base_pool", "")
        obj_name = kw.get("obj_name", "")
        cmd = self.base_cmd + f" -p {base_pool} tier-evict {obj_name}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
