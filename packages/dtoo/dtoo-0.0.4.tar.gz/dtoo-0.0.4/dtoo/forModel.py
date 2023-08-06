import attr

def dataclass_wrapper(cls):

    @attr.define(frozen=True)
    class Wrapper(cls):

        def __init__(self):
            super().__init__()

        @staticmethod
        def Create():
            obj = cls()
            obj.__class__.__name__ = "myobject"
            return  obj

    return Wrapper