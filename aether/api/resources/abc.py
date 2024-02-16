import aenum
import attrs
import typing

from datetime import datetime

from aether import const
from aether.core import utils

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

class Snowflake(typing.Generic[const.T]):
    def __init__(self: const.T) -> None:
        self = self

    def __eq__(self: const.T, other: const.T) -> bool:
        return const.T(self) == const.T(other)
    
    def __repr__(self: const.T) -> str:
        return str(self)
    
    def __str__(self: const.T) -> str:
        return str(self)
    
    def __int__(self: const.T) -> int:
        return int(self)
    
    def __enter__(self: const.T) -> Data:
        return Data(self)
    
    def __exit__(self: const.T, *exc) -> None:
        return None
    
    @property
    def created_on(self: const.T) -> Timestamp:
        with Snowflake(self) as data:
            return Timestamp.utcfromtimestamp(data.timestamp)

utils.unsupported_type(Snowflake)

@attrs.define(kw_only=True)
class Object:
    id: Snowflake[str]
    _client: 'client.Connection' # type: ignore

class Partial(typing.Mapping[str, const.T]): ... 
utils.unsupported_type(Partial)

class Endpoint:
    class CDN(aenum.StrEnum):
        CUSTOM_EMOJI = 'emojis/{emoji_id}'
        GUILD_ICON = 'icons/{guild_id}'
        GUILD_SPLASH = 'splashes/{guild_id}/{guild_splash}'
        GUILD_DISCOVERY_SPLASH = 'discovery-splashes/{guild_id}/{guild_discovery_splash}'
        GUILD_BANNER = 'banners/{guild_id}/{guild_banner}'
        USER_BANNER = 'banners/{user_id}/{user_banner}'
        DEFAULT_USER_AVATAR = 'embed/avatars/{index}'
        USER_AVATAR = 'avatars/{user_id}/{user_avatar}'
        GUILD_MEMBER_AVATAR = 'guilds/{guild_id}/users/{user_id}/avatars/{member_avatar}'
        USER_AVATAR_DECORATION = 'avatar-decorations/{user_id}/{user_avatar_decoration}'
        APPLICATION_ICON = 'app-icons/{application_id}/{icon}'
        APPLICATION_COVER = 'app-icons/{application_id}/{cover_image}'
        APPLICATION_ASSET = 'app-assets/{application_id}/{asset_id}'
        ACHIEVEMENT_ICON = 'app-assets/{application_id}/achievements/{achievement_id}/icons/{icon_hash}'
        STORE_PAGE_ASSET = 'app-assets/{application_id}/store/{asset_id}'
        STICKER_PACK_BANNER = 'app-assets/{applicaion_id}/store/{sticker_pack_banner_asset_id}'
        TEAM_ICON = 'team-icons/{team_id}/{team_icon}'
        STICKER = 'stickers/{sticker_id}'
        ROLE_ICON = 'role-icons/{role_id}/{role_icon}'
        GUILD_SCHEDULED_EVENT_COVER = 'guild-events/{scheduled_event_id}/{scheduled_event_cover_image}'
        GUILD_MEMBER_BANNER = 'guilds/{guild_id}/users/{user_id}/banners/{member_banner}'
class Asset(str):
    @classmethod
    def resolve(cls, path: Endpoint.CDN, *, animated: const.Maybe[bool] = const.empty, **kwargs) -> str:
        animated = utils.contains_or(animated, True if 'a_' in kwargs.keys() else False)
        file_type = '.gif' if animated else '.png' # fuck .jpeg
        return path.format(**kwargs) + file_type
        
    
utils.unsupported_type(Asset)