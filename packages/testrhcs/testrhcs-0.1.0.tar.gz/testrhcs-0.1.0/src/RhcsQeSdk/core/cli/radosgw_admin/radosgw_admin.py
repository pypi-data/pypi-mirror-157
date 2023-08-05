import logging

from RhcsQeSdk.core.cli.radosgw_admin.bi import Bi
from RhcsQeSdk.core.cli.radosgw_admin.bucket import Bucket
from RhcsQeSdk.core.cli.radosgw_admin.caps import Caps
from RhcsQeSdk.core.cli.radosgw_admin.key import Key
from RhcsQeSdk.core.cli.radosgw_admin.log import Log
from RhcsQeSdk.core.cli.radosgw_admin.metadata import Metadata
from RhcsQeSdk.core.cli.radosgw_admin.object import Object
from RhcsQeSdk.core.cli.radosgw_admin.period import Period
from RhcsQeSdk.core.cli.radosgw_admin.pool import Pool
from RhcsQeSdk.core.cli.radosgw_admin.realm import Realm
from RhcsQeSdk.core.cli.radosgw_admin.reshard import Reshard
from RhcsQeSdk.core.cli.radosgw_admin.role import Role
from RhcsQeSdk.core.cli.radosgw_admin.role_policy import RolePolicy
from RhcsQeSdk.core.cli.radosgw_admin.subscription import Subscription
from RhcsQeSdk.core.cli.radosgw_admin.subuser import Subuser
from RhcsQeSdk.core.cli.radosgw_admin.topic import Topic
from RhcsQeSdk.core.cli.radosgw_admin.usage import Usage
from RhcsQeSdk.core.cli.radosgw_admin.user import User
from RhcsQeSdk.core.cli.radosgw_admin.zone import Zone
from RhcsQeSdk.core.cli.radosgw_admin.zonegroup import Zonegroup

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s"
)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)


class Radosgw_admin:
    """
    This module provides CLI interface to manage users, quotas, buckets, indexes,
    and all other aspects of the radosgw service.
    """

    def __init__(self, base_cmd=""):
        self.base_cmd = f"{base_cmd}radosgw-admin"
        self.zonegroup = Zonegroup(self.base_cmd)
        self.zone = Zone(self.base_cmd)
        self.topic = Topic(self.base_cmd)
        self.realm = Realm(self.base_cmd)
        self.bucket = Bucket(self.base_cmd)
        self.period = Period(self.base_cmd)
        self.user = User(self.base_cmd)
        self.subscription = Subscription(self.base_cmd)
        self.bi = Bi(self.base_cmd)
        self.usage = Usage(self.base_cmd)
        self.role = Role(self.base_cmd)
        self.role_policy = RolePolicy(self.base_cmd)
        self.key = Key(self.base_cmd)
        self.object = Object(self.base_cmd)
        self.caps = Caps(self.base_cmd)
        self.log = Log(self.base_cmd)
        self.pool = Pool(self.base_cmd)
        self.subuser = Subuser(self.base_cmd)
        self.reshard = Reshard(self.base_cmd)
        self.metadata = Metadata(self.base_cmd)
