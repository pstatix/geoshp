import abc
import pathlib
import struct
import typing


import geoshp.core.types as types
import geoshp.shp.shapefile as shp

__all__ = [
    'ShapefileReader'
]


class _HeaderData(typing.NamedTuple):
    """Data container for header information when reading"""
    file_code: int
    version: int
    shape_type: int
    bbox: shp.BoundingBox


# declared multiple inheritance to tell PyCharm to stop warning
class ShapefileReader(shp.ShapefileInterface, abc.ABC):

    def __init__(self, file: types.FilePath) -> None:

        super().__init__()

        file = pathlib.Path(file)
        shpf = file.with_suffix('.shp')
        shxf = file.with_suffix('.shx')

        self._shp = shpf.open('rb')
        self._shx = shxf.open('rb')

        self._shp_path = shpf.resolve().as_posix()
        self._shx_path = shxf.resolve().as_posix()

        try:
            header_data = self.shp_header(self._shp)

            self._file_code = header_data.file_code
            self._version = header_data.version
            self._shape_type = header_data.shape_type
            self._bbox = header_data.bbox

        except struct.error as err:
            raise shp.ShapefileException(f'Failed to parse header of {self._shp_path}') from err

        finally:
            self.close()

        self._shx.seek(0, 2)  # move to bottom of file
        self._num_shapes = (self._shx.tell() - 100) // 8

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

    def __getitem__(self, key: int) -> shp.Shape:

        return self._shape(key)

    @abc.abstractmethod
    def _shape(self, num: int) -> shp.Shape:

        raise NotImplementedError

    @abc.abstractmethod
    def iter_shapes(self) -> typing.Generator[shp.Shape, None, None]:

        raise NotImplementedError

    @staticmethod
    def shp_header(fp: typing.BinaryIO) -> _HeaderData:

        fp.seek(0)  # explicitly reset
        fc = struct.unpack('>i24x', fp.read(28))[0]
        ver, _type = struct.unpack('<2i', fp.read(8))
        bbox = list(struct.unpack('<8d', fp.read(64)))

        return _HeaderData(fc, ver, _type, shp.BoundingBox(*bbox))

    def shape(self, num: int) -> shp.Shape:

        if abs(num) > self._num_shapes:
            # might need to adjust display to be 1-indexed?
            raise shp.ShapefileException(f'Feature {num} outside range 0->{self._num_shapes}')

        elif num == 0:
            num = 1  # shape records begin a 1 not 0

        elif num < 0:
            num = (self._num_shapes + num) + 1

        return self._shape(num)  # need to check if indexing is correct

    def close(self) -> None:

        shpf = self._shp_path is not None
        shxf = self._shx_path is not None

        if shpf and not self._shp.closed:
            self._shp.close()

        if shxf and not self._shx.closed:
            self._shx.close()



