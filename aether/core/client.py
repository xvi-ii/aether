import typing

from aether import const
from aether.core import utils, scheduler
from aether.api import gateway

__all__ = ('Connection')

class Connection:
    intents: gateway.Intents
    _scheduler: scheduler.Schedule
    _gw: gateway.Connection = None

    def __init__(self, *, intents: const.Maybe[gateway.Intents] = const.empty) -> None:
        intents = utils.contains_or(intents, gateway.Intents.none())
        self.intents = intents
        self._scheduler = scheduler.Schedule()

    async def start(self, token: str) -> None:
        async with gateway.Connection(token=token, intents=self.intents) as self._gw:
            self._gw._client = self

    async def stop(self) -> None:
        await self._gw.close()

    def on(self, fn: const.Maybe[typing.Coroutine] = const.empty, *, name: const.Maybe[str] = const.empty) -> typing.Coroutine:
        name = utils.contains_or(name, fn.__name__)
        
        def inner(fn: typing.Coroutine):
            callsite = self._scheduler.get(name)
            self._scheduler.add(callsite)
            return fn

        return inner(fn)
        
    @property
    def latency(self) -> float:
        return self._gw.latency
    
    @property
    def online(self) -> bool:
        return not bool(self._gw._ws.closed)
