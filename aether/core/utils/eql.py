from ... import const

def contains(expected: const.Maybe[const.T], default: const.T) -> const.T:
    return expected if expected is not const.empty else default