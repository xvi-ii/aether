import random

from ... import const

def can_access_token(fn) -> None:
    const.token_access = True
    return fn

def garble_token(token: str) -> str:
    chars = '▖▗▘▙▚▛▜▝▞▟▂▃▄▅▆▇█▉▊▋▌▍'
    return ''.join([random.choice(chars) for _ in range(len(token))])

def lock_token() -> None:
    const.token_access = False