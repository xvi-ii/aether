import attrs

from aether import const
from aether.api import resources

@attrs.define(kw_only=True)
class Hello:
    heartbeat_interval: int

@attrs.define(kw_only=True)
class Ready:
    v: int
    user: resources.User
    guilds: list[resources.Partial]
    session_id: str
    resume_gateway_url: str
    shard: const.Maybe[tuple[int, int]] = const.empty
    application: resources.Partial

Resumed = const.empty
Reconnect = const.empty
InvalidSession = const.empty
