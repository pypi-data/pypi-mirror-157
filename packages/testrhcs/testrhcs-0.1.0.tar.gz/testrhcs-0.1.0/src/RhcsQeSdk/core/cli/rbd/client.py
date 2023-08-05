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


class Client:

    """
    This Class provides wrappers for rbd journal client commands.
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " client"

    def disconnect(self, **kw):
        """Wrapper for rbd journal client disconnect.

        Flag image journal client as disconnected.
        Args:
        kw: Key value pair of method arguments
            Example::
            Supported keys:
                journal_spec(str): journal specification.
                                    [<pool-name>/[<namespace>/]]<journal-name>
                namespace(str): name of the namespace
                pool(str): pool name
                image(str): image name
                journal(str): journal name
                client-id(str): client ID (leave unspecified to disconnect all)
        Returns:
            Dict(str):
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")

        kw_copy = deepcopy(kw)
        journal_spec = kw_copy.pop("journal_spec", "")
        cmd_args = core_utils.build_cmd_args(kw=kw_copy)

        cmd = f"{self.base_cmd} disconnect {journal_spec}{cmd_args}"
        logger.info(f"Running command {cmd}")
        return fabfile.run_command(cmd, config=kw.get("env_config"))
