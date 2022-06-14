import abc
import typing


class ShapefileException(Exception):
    pass


class Shape(typing.NamedTuple):
    """Data container for all ShapefileInterface modalities"""
    rec_num: int
    form: list = []  # default to empty list for NullShapeType


class BoundingBox(typing.NamedTuple):
    """Data container for all ShapefileInterface modalities"""
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    z_min: float
    z_max: float
    m_min: float
    m_max: float

    def __str__(self) -> str:

        return str([v for v in self])  # potential for expansion for detail


class ShapefileInterface(abc.ABC):

    def __init__(self) -> None:

        self._file_code = 0         # type: int
        self._version = 0           # type: int
        self._num_shapes = 0        # type: int
        self._bbox = [0.0] * 8      # type: typing.List[float]
        self._shape_type = None     # type: typing.Optional[int]
        self._shp_path = None       # type: typing.Optional[str]
        self._shx_path = None       # type: typing.Optional[str]
        self._shp = None            # type: typing.Optional[typing.BinaryIO]
        self._shx = None            # type: typing.Optional[typing.BinaryIO]
        self._has_nulls = False     # type: bool

    def __enter__(self) -> 'ShapefileInterface':

        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:

        self.close()

    def __del__(self) -> None:

        shp = self._shp_path is not None
        shx = self._shx_path is not None

        if shp or shx:
            self.close()

    def __len__(self) -> int:

        return self._num_shapes

    @abc.abstractmethod
    def close(self) -> None:
        raise NotImplementedError

    @property
    def type(self) -> int:

        return self._shape_type

    @property
    def bbox(self) -> typing.List[float]:

        return self._bbox

    @property
    def shp(self) -> str:

        return self._shp_path if self._shp_path is not None else None

    @property
    def shx(self) -> str:

        return self._shx_path if self._shx_path is not None else None

    @property
    def has_nulls(self) -> bool:

        return self._has_nulls

    @property
    def closed(self) -> bool:

        shp = self._shp is not None
        shx = self._shx is not None

        if shp and shx:
            return self._shp.closed and self._shx.closed
        return False


