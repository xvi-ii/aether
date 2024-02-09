import cattrs
import typing

from ... import const

def build(T: const.T, data: const.T) -> const.T:
    return data(T)

def unsupported_type(T: const.T) -> None:
    print(T)
    # if mult_typ := typing.get_args(T):
    #     print(mult_typ)
    #     for typ in mult_typ:
    #         print(typ)
    #         cattrs.register_structure_hook(typ, build)
    # else:
    cattrs.register_structure_hook(T, build)
