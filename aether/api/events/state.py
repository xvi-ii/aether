import attrs
import typing

from .. import resources
from ... import const

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

Resumed: typing.TypeAlias = const.Maybe
Reconnect: typing.TypeAlias = const.Maybe
InvalidSession: typing.TypeAlias = const.Maybe
