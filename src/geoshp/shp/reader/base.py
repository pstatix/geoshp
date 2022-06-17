import abc
import array
import pathlib
import struct
import typing

import geoshp.core.types as types
import geoshp.shp.shapefile as shp

__all__ = [
    'ShapefileReader',
    'FixedFeatureShapefileReader',
    'DynamicFeatureShapefileReader'
]


class _HeaderData(typing.NamedTuple):
    """Data container for header information when reading"""
    file_code: int
    version: int
    shape_type: int
    bbox: shp.BoundingBox


# declared multiple inheritance to tell PyCharm to stop warning
class ShapefileReader(shp.ShapefileInterface, metaclass=abc.ABCMeta):

    def __init__(self, file: types.FilePath, *args, **kwargs) -> None:

        super().__init__(*args, **kwargs)

        # even if a pathlib.Path object is passed in, copy it
        file = pathlib.Path(file)
        shpf = file.with_suffix('.shp')
        shxf = file.with_suffix('.shx')

        self._shp = shpf.open('rb')
        self._shx = shxf.open('rb')

        self._shp_path = shpf.resolve().as_posix()
        self._shx_path = shxf.resolve().as_posix()

        self._nulls = set()     # type: typing.Set[int]
        self._lengths = []      # type: typing.List[int]

        self._load_header_data()
        self._load_record_data()

    def __str__(self) -> str:

        show = (
            f'{type(self).__name__} @ addr: <{hex(id(self))}>\n'
            f'\tLocation: {self._shp_path}\n'
            f'\tFeatures: {self._num_shapes}\n'
            f'\tBBOX: {self._bbox}'
        )

        return show

    def __repr__(self) -> str:

        return f'{type(self).__name__}(file={self._shp_path})'

    def __getitem__(self,
                    key: typing.Union[int, types.Slice]
                    ) -> typing.Union[shp.Shape, typing.List[shp.Shape]]:

        try:
            start = key.start
            stop = key.stop
            step = key.step

            self._check_index(start, stop)

        except AttributeError:

            self._check_index(key)

            return self._shape(key)

        else:
            return list(self.iter_shapes(start, stop, step))

    def _read_null(self) -> shp.Shape:

        rn = struct.unpack('', self._shp.read(12))[0]

        return shp.Shape(rec_num=rn)

    def _load_header_data(self) -> None:

        try:
            header_data = self.shp_header(self._shp)

            self._file_code = header_data.file_code
            self._version = header_data.version
            self._shape_type = header_data.shape_type
            self._bbox = header_data.bbox

        except struct.error as err:
            # ensure cleanup on error
            self.close()

            raise shp.ShapefileException(
                f'Failed to parse header of {self._shp_path}'
            ) from err

    def _load_record_data(self) -> None:

        # get the count of features
        self._shx.seek(0)  # explicitly reset
        self._shx.seek(0, 2)  # move to bottom of file
        self._num_shapes = (self._shx.tell() - 100) // 8

        # reset head
        self._shx.seek(0)
        self._shx.seek(100)

        # low-memory footprint read of data
        data = array.array('l')
        data.fromfile(self._shx, self._num_shapes * 2)
        data.byteswap()

        # get just the offset
        # self._lengths = data[0::2]

        # NULL features will have a total content length of 2 16-bit words
        # the i + 1 is because files are 1-indexed
        self._nulls = {i + 1 for i, cl in enumerate(data[::2]) if cl == 2}

        if self._nulls:
            self._has_nulls = True

    @abc.abstractmethod
    def _shape(self, num: int) -> shp.Shape:

        raise NotImplementedError

    @abc.abstractmethod
    def iter_shapes(self,
                    start: typing.Optional[int] = None,
                    stop: typing.Optional[int] = None,
                    step: typing.Optional[int] = None
                    ) -> typing.Generator[shp.Shape, None, None]:

        raise NotImplementedError

    @staticmethod
    def shp_header(fp: typing.BinaryIO) -> _HeaderData:

        fp.seek(0)  # explicitly reset
        fc = struct.unpack('>i24x', fp.read(28))[0]
        ver, _type = struct.unpack('<2i', fp.read(8))
        bbox = list(struct.unpack('<8d', fp.read(64)))
        fp.seek(0)  # explicitly reset

        return _HeaderData(fc, ver, _type, shp.BoundingBox(*bbox))

    def shape(self, num: int) -> shp.Shape:

        # shift right to allow Python 0-indexing
        if num >= 0:
            num += 1

        # shifting not required when below 0
        # allow backwards access
        # example:
        #   self._num_shapes = 100
        #   num = -2 (i.e. access 2nd to last shape like a list)
        #   num = (100 - 2) + 1 = 99
        # total reads required is the same if having compute a seek to the record header
        elif num < 0:
            num = (self._num_shapes + num) + 1

        # take advantage of the __getitem__ implementation
        return self[num]

    def close(self) -> None:

        shpf = self._shp_path is not None
        shxf = self._shx_path is not None

        if shpf and not self._shp.closed:
            self._shp.close()

        if shxf and not self._shx.closed:
            self._shx.close()


# the Esri specification allows Shapefiles to contain NULL types and base types
# so all of these cases are NonNull by default but need required methods to
# ensure they can parse the next record if it is a NULL
class NonNullShapefileReader(ShapefileReader, metaclass=abc.ABCMeta):

    def __init__(self, *args, **kwargs) -> None:

        super().__init__(*args, **kwargs)


class FixedFeatureShapefileReader(NonNullShapefileReader, metaclass=abc.ABCMeta):

    pass


class DynamicFeatureShapefileReader(NonNullShapefileReader, metaclass=abc.ABCMeta):

    def _shape(self, num: int) -> shp.Shape:
        pass

    def iter_shapes(self,
                    start: typing.Optional[int] = None,
                    stop: typing.Optional[int] = None,
                    step: typing.Optional[int] = None
                    ) -> typing.Generator[shp.Shape, None, None]:
        pass
