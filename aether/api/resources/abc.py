import aenum
import attrs
import typing

from datetime import datetime

from ... import const, utils

class TimestampStyle(aenum.StrEnum):
    SHORT_TIME = 't'
    LONG_TIME = 'T'
    SHORT_DATE = 'd'
    LONG_DATE = 'D'
    SHORT_DATE_TIME = 'f'
    LONG_DATE_TIME = 'F'
    RELATIVE = 'R'

class Timestamp(datetime):
    def mention(self, style: const.Maybe[TimestampStyle] = const.empty) -> str:
        style = utils.contains_or(style, TimestampStyle.SHORT_DATE_TIME)
        return f"<t:{self}:{style}>"

utils.unsupported_type(Timestamp)

DISCORD_EPOCH = typing.Literal[1420070400000]

class Data:
    def __init__(self, typ: const.T) -> None:
        self.snowflake = int(typ)

    @property
    def timestamp(self) -> int:
        return (self.snowflake >> 22) + DISCORD_EPOCH
    
    @property
    def internal_worker_id(self) -> int:
        return (self.snowflake & 0x3E0000) >> 17
    
    @property
    def internal_process_id(self) -> int:
        return (self.snowflake & 0x1F000) >> 12
    
    @property
    def increment(self) -> int:
        return self.snowflake & 0xFFF

class Snowflake[T]:
    def __init__(self: T) -> None:
        self = self

    def __eq__(self: T, other: T) -> bool:
        return T(self) == T(other)
    
    def __repr__(self: T) -> str:
        return str(self)
    
    def __str__(self: T) -> str:
        return str(self)
    
    def __int__(self: T) -> int:
        return int(self)
    
    def __enter__(self: T) -> Data:
        return Data(self)
    
    def __exit__(self: T, *exc) -> None:
        return None
    
    @property
    def created_on(self: T) -> Timestamp:
        with Snowflake(self) as data:
            return Timestamp.utcfromtimestamp(data.timestamp)

utils.unsupported_type(Snowflake)

@attrs.define(kw_only=True)
class Object:
    id: Snowflake[str]
    _client: 'Connection' # type: ignore

Partial = typing.Mapping[str, const.T]
utils.unsupported_type(Partial)