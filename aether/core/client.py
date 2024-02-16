from aether import const
from aether.core import utils
from ..api import gateway

__all__ = ('Client')

class Connection:
    intents: gateway.Intents
    _gw: gateway.Connection = None

    def __init__(self, *, intents: const.Maybe[gateway.Intents] = const.empty) -> None:
        intents = utils.contains_or(intents, gateway.Intents.none())
        self.intents = intents

    async def start(self, token: str) -> None:
        async with gateway.Connection(token=token, intents=self.intents) as self._gw:
            self._gw._client = self

    async def stop(self) -> None:
        await self._gw.close()

    @property
    def latency(self) -> float:
        return self._gw.latency
    
    @property
    def online(self) -> bool:
        return not bool(self._gw._ws.closed)

Client = Connection