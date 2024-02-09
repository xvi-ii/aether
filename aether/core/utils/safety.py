from ... import const

def token_safe(fn) -> None:
    def func(fn):
        const.access_token = True
        return fn
    return func

def lock_token() -> None:
    const.access_token = False