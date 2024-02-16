import logging
import typing

from aether import const
from aether.core import utils

logger = logging.getLogger('aether')
logger.setLevel(logging.DEBUG)

class Result(typing.Generic[const.T]):
    fn: typing.Coroutine[const.T]
    once: bool
    
    def __init__(self, fn: typing.Coroutine, *, once: const.Maybe[bool] = const.empty) -> None:
        once = utils.contains_or(once, False)
        self.once = once
    
    def __await__(self) -> typing.Generator:
        if self.once:   logger.warning(f"{self.__name__} can only be called once.")
        else:           return (yield from self.fn.__await__())
        
class Schedule:
    _fns: dict[str, list[typing.Coroutine]] = {}
    
    def __init__(self) -> None: pass
    def __new__(cls) -> None: pass
    
    def get(self, name: str) -> const.Maybe[list[typing.Coroutine]]:
        return utils.contains_or(self._fns.get(name) or const.empty, const.empty)
        
    def add(self, fn: typing.Callable, *, name: str) -> None:
        fns = self.get(name)
        if utils.contains(fns):
            fns.append(fn)
            
    async def run(self, name: str, *args) -> list[Result] | None:
        results = []
        fns = utils.contains_or(self.get(name), False)
        if fns:
            [results.append((await Result(fn, *args))) for fn in fns]
        return results