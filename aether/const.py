import typing

T = typing.TypeVar("T")
empty = ...
Maybe = typing.Union[T, type(empty)]

access_token: bool = False
GATEWAY_URL = 'wss://gateway.discord.gg/'
USER_AGENT = '🪄 v0.0.1'