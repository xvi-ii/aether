from ... import const

def contains(expected: const.Maybe[const.T]) -> bool:
    return expected is not const.empty

def contains_or(expected: const.Maybe[const.T], default: const.T) -> const.T:
    return expected if contains(expected) else default

def contains_all(expected: const.Maybe[const.T]) -> bool:
    return all(contains(T) for T in expected)