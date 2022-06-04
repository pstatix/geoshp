import typing
import geoshp.shp.shapefile as shp

_S = typing.TypeVar('_S')


class _Singleton(type):
    _instance = None

    def __call__(cls: _S, *args, **kwargs) -> _S:
        if cls._instance is None:
            cls._instance = super(_Singleton, cls).__call__(*args, **kwargs)
        return cls._instance


# originally a Python 2.7 case existed
# kept a base class for potential extension
class _ModeFactoryBase(metaclass=_Singleton):
    pass


class _ModeFactory(_ModeFactoryBase):

    def __init__(self) -> None:
        self.modes = {}

    def register(self, mode: str, _type: int, kls: typing.Type[shp.ShapefileInterface]) -> None:

        if (mode, _type) not in self.modes:
            self.modes[(mode, _type)] = kls


def register_mode(mode: str, _type: int, kls: typing.Type[shp.ShapefileInterface]) -> None:

    _ModeFactory().register(mode, _type, kls)
