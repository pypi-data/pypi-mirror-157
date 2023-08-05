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


class Reshard:
    """
    This module provides CLI interface for commands of radosgw-admin reshard.
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " reshard"

    def add_(self, **kw):
        """Schedule a resharding of a bucket.
        Args:
                bucket_name(str) : Bucket name
                num_shards(str) : New number of shards
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        bucket = kw.get("bucket_name", "")
        num_shards = kw.get("num_shards", "")
        cmd = self.base_cmd + " add" + f" --bucket {bucket} --num-shards {num_shards}"
        logger.info(f"Running commmand {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def list_(self, **kw):
        """List all bucket resharding or scheduled to be resharded.
        Args:
                None
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " list"
        logger.info(f"Running commmand {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def process(self, **kw):
        """Process of scheduled reshard jobs.
        Args:
                None
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        cmd = self.base_cmd + " process"
        logger.info(f"Running commmand {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def status(self, **kw):
        """Resharding status of a bucket.
        Args:
                bucket_name(str) : Bucket name
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        bucket = kw.get("bucket_name", "")
        cmd = self.base_cmd + " status" + f" --bucket {bucket}"
        logger.info(f"Running commmand {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))

    def cancel(self, **kw):
        """Cancel resharding a bucket.
        Args:
                bucket_name(str) : Bucket name
        Returns:
            Dict(str)
            A mapping of host strings to the given task’s return value for that host’s execution run
        """
        kw = kw.get("kw")
        bucket = kw.get("bucket_name", "")
        cmd = self.base_cmd + " cancel" + f" --bucket {bucket}"
        logger.info(f"Running commmand {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
