import logging

from RhcsQeSdk.core.cli.rbd.mirror.image import Image
from RhcsQeSdk.core.cli.rbd.mirror.pool import Pool
from RhcsQeSdk.core.cli.rbd.mirror.snapshot import Snapshot

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s"
)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)


class Mirror:
    """Base class for all rbd mirror commands.

    This module provides CLI interface to manage rbd mirror and
    objects with wrapper for sub-commands.

    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " mirror"
        self.image = Image(self.base_cmd)
        self.pool = Pool(self.base_cmd)
        self.snapshot = Snapshot(self.base_cmd)
