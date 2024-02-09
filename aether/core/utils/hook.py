import cattrs
import typing

from ... import const

def build(data: const.T, T: const.T) -> const.T:
    return T(data)

def unsupported_type(T: const.T) -> None:
    # if mult_typ := typing.get_args(T):
    #     print(mult_typ)
    #     for typ in mult_typ:
    #         print(typ)
    #         cattrs.register_structure_hook(typ, build)
    # else:
    cattrs.register_structure_hook(T, build)
