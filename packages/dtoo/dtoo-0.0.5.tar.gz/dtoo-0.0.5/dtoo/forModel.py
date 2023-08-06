import attr
from typing import TypeVar

T = TypeVar('T')

def dataclass_wrapper(cls: T) -> T:

    @attr.define(frozen=True)
    class Wrapper(cls):

        def __init__(self):
            super().__init__()

        @staticmethod
        def Create():
            obj = cls()
            obj.__class__.__name__ = "myobject"
            return  obj

        @staticmethod
        def GetType():
            return type(cls)

    return Wrapper

# def dataclass_wrapper(cls: T) -> T:
#
#     def Create(cls):
#         obj = cls()
#         obj.__class__.__name__ = "myobject"
#         return obj
#
#     cls.Create = classmethod(Create)
#
#     return cls