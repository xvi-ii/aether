import random
import sys
import time
import aenum
import attrs
import cattrs
import logging
import trio
import trio_websocket as websocket
import typing
import ujson

from . import events
from .. import const
from ..core import utils

logger = logging.getLogger('aether')
logger.setLevel(logging.DEBUG)

class OpCode(aenum.IntEnum):
    DISPATCH                = 0
    HEARTBEAT               = aenum.auto()
    IDENTIFY                = aenum.auto()
    PRESENCE_UPDATE         = aenum.auto()
    VOICE_STATE_UPDATE      = aenum.auto()
    RESUME                  = 6
    RECONNECT               = aenum.auto()
    REQUEST_GUILD_MEMBERS   = aenum.auto()
    INVALID_SESSION         = aenum.auto()
    HELLO                   = aenum.auto()
    HEARTBEAT_ACK           = aenum.auto()

@attrs.define(kw_only=True)
class Payload:
    op: OpCode
    d: typing.Any | None # noqa
    s: int | None = None
    t: str | None = None

class Intents(aenum.IntFlag):
    GUILDS                          = 1 << 0
    GUILD_MEMBERS                   = aenum.auto()
    GUILD_MODERATION                = aenum.auto()
    GUILD_EMOJIS_AND_STICKERS       = aenum.auto()
    GUILD_INTEGRATIONS              = aenum.auto()
    GUILD_WEBHOOKS                  = aenum.auto()
    GUILD_INVITES                   = aenum.auto()
    GUILD_VOICE_STATES              = aenum.auto()
    GUILD_PRESENCES                 = aenum.auto()
    GUILD_MESSAGES                  = aenum.auto()
    GUILD_MESSAGE_REACTIONS         = aenum.auto()
    GUILD_MESSAGE_TYPING            = aenum.auto()
    DIRECT_MESSAGES                 = aenum.auto()
    DIRECT_MESSAGE_REACTIONS        = aenum.auto()
    DIRECT_MESSAGE_TYPING           = aenum.auto()
    MESSAGE_CONTENT                 = aenum.auto()
    GUILD_SCHEDULED_EVENTS          = aenum.auto()
    AUTO_MODERATION_CONFIGURATION   = 1 << 20
    AUTO_MODERATION_EXECUTION       = aenum.auto()

    @classmethod
    def none(cls) -> 'Intents':
        return Intents(0)

@attrs.define(kw_only=True)
class _State:
    version: const.Maybe[int] = const.empty
    encoding: const.Maybe[str] = const.empty
    compress: const.Maybe[bool] = const.empty
    heartbeat_interval: int | float = None
    can_hb: bool = None
    last_hb: float = None
    last_ack: float = None
    resume_gateway_url: str = None
    session_id: str = None
    sequence_no: int = None

class Connection:
    intents: Intents
    _state: _State
    _token: str
    _ws: websocket.WebSocketConnection = None
    _tasks = None
    _client: 'client.Connection' = None # type: ignore

    @property
    def token(self) -> str:
        if const.token_access:  return self._token
        else:                   return 'Not allowed'
    
    @token.setter
    def token(self, value: str) -> None:
        self._token = value

    def __init__(self, *, token: str, intents: const.Maybe[Intents] = const.empty) -> None:
        intents = utils.contains_or(intents, Intents.none())
        self.intents = intents
        self._state = _State()
        self._token = token

    async def __aenter__(self) -> 'Connection':
        self._tasks = trio.open_nursery(strict_exception_groups=True)
        scheduler = await self._tasks.__aenter__()
        scheduler.start_soon(self._heartbeat)
        scheduler.start_soon(self.restart)
        return self
    
    async def __aexit__(self, *exc):
        return await self._tasks.__aexit__(*exc)
    
    async def _send(self, payload: Payload) -> bool:
        payload_as_dict = attrs.asdict(payload)
        dict_as_json = ujson.dumps(payload_as_dict)
        try:
            await self._ws.send_message(dict_as_json)
            table = utils.dict_as_table(payload.d if not isinstance(payload.d, (int, bool)) else payload_as_dict)
            logger.debug(f"<- {payload.t or payload.op.name}\n{table}")
            return 1
        except websocket.ConnectionClosed as exc:
            logger.exception(exc)
            return 0
    
    async def _receive(self) -> Payload | None:
        try:
            recv = await self._ws.get_message()
            json_as_dict = ujson.loads(recv)
            payload = cattrs.structure(json_as_dict, Payload)
            table = utils.dict_as_table(payload.d)

            logger.debug(f"-> {payload.t or payload.op.name}" + (f"\n{table}" if table else ''))
            return payload
        except websocket.ConnectionClosed as exc:
            logger.exception(exc)
            return

    async def start(
        self,
        token: str,
        *,
        version: const.Maybe[int] = const.empty,
        encoding: const.Maybe[str] = const.empty,
        compress: const.Maybe[bool] = const.empty
    ) -> None:
        self._token = token
        version = utils.contains_or(version, 10)
        encoding = utils.contains_or(encoding, 'json')
        compress = utils.contains_or(compress, False)

        self._state.version = version
        self._state.encoding = encoding
        self._state.compress = compress

        try:
            async with websocket.open_websocket_url(
                self._state.resume_gateway_url or const.GATEWAY_URL
                + f"?v={version}&encoding={encoding}"
                + ('&compress=zlib-stream' if compress else '')
            ) as self._ws:
                while not self._ws.closed:
                    payload = await self._receive()
                    await self._track(payload)
        except websocket.HandshakeError as exc:
            logger.exception(exc)
            return
        
    async def close(self, *, reset_state: const.Maybe[bool] = const.empty) -> None:
        if (
            isinstance(self._ws, websocket.WebSocketConnection)
            and not self._ws.closed
        ):
            await self._ws.aclose()
        if reset_state := utils.contains_or(reset_state, False):
            self._state = _State()

    async def restart(self) -> None:
        if self._ws == None or self._ws.closed:
            await self.start(
                self._token,
                version=utils.contains_or(self._state.version, 10),
                encoding=utils.contains_or(self._state.encoding, 'json'),
                compress=utils.contains_or(self._state.compress, False)
            )

    async def _track(self, payload: Payload) -> None:
        self._state.sequence_no = payload.s
        match payload.op:
            case OpCode.DISPATCH:           pass # await self._dispatch(payload)
            case OpCode.HEARTBEAT:          await self._heartbeat()
            case OpCode.RESUME:             await self._resume()
            case OpCode.INVALID_SESSION:
                if payload.d:               await self._resume()
                else:                       await self.close()
            case OpCode.RECONNECT:          await self._resume()
            case OpCode.HELLO:
                if self._state.session_id:  await self._resume()
                else:                       await self._identify()
                self._state.heartbeat_interval = payload.d['heartbeat_interval'] / 1000
                self._state.can_hb = True 
            case OpCode.HEARTBEAT_ACK:
                self._state.last_ack = time.perf_counter()
                logger.debug(f"-> 💓 {round(self.latency, 2)}")
            case _:                         pass
        match payload.t:
            case 'READY':
                self._state.resume_gateway_url = payload.d['resume_gateway_url']
                self._state.session_id = payload.d['session_id']
            case _:                         pass

    async def _dispatch(self, payload: Payload) -> None:
        name = payload.t.lower()
        data = lambda T:  cattrs.structure(payload.d or const.empty, T)
        send = lambda *D: await self._client._spawn(name, *(data(d) for d in D))
        match payload.t.upper():
            case 'HELLO':           send(*events.Hello)
            case 'READY':           send(*events.Ready)
            case 'RESUMED':         send(*events.Resumed)
            case 'RECONNECT':       send(*events.Reconnect)
            case 'INVALID_SESSION': send(*events.InvalidSession)

    @utils.can_access_token
    async def _identify(
        self,
        *,
        compress: const.Maybe[bool] = const.empty,
        large_threshold: const.Maybe[int] = const.empty
    ) -> None:
        compress = utils.contains_or(compress, False)
        large_threshold = utils.contains_or(large_threshold, 50)

        if large_threshold < 50 or large_threshold > 250:
            large_threshold = 50
            logger.error(f"large_threshold out of bounds (50-250): {large_threshold}")

        payload = Payload(
            op=OpCode.IDENTIFY,
            d={
                'token': self.token,
                'properties': {
                    'os': sys.platform,
                    'browser': const.USER_AGENT,
                    'device': const.USER_AGENT
                },
                'compress': compress,
                'large_threshold': large_threshold,
                # 'shard': shard,
                # 'presence': presence,
                'intents': self.intents
            }
        )
        utils.lock_token()
        await self._send(payload)

    @utils.can_access_token
    async def _resume(self) -> None:
        payload = Payload(
            op=OpCode.RESUME,
            d={
                'token': self.token,
                'session_id': self._state.session_id,
                'seq': self._state.sequence_no
            }
        )
        utils.lock_token()
        await self._send(payload)
    
    async def _heartbeat(self) -> None:
        await trio.sleep(random.random())
        while self._state.can_hb:
            payload = Payload(op=OpCode.HEARTBEAT, d=self._state.sequence_no)
            await self._send(payload)
            self._state.last_hb = time.perf_counter()
            await trio.sleep(self._state.heartbeat_interval)

    @property
    def latency(self) -> float:
        return self._state.last_ack - self._state.last_hb