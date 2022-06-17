import struct
import typing

from geoshp.shp import factory
from geoshp.shp import reader
import geoshp.shp.shapefile as shp


class PointShapefileReader(reader.FixedFeatureShapefileReader):

    def _shape(self, num: int) -> shp.Shape:

        # skip: (header) + (number of features) + (specified feature header and type field)
        # number of features: the headers and contents of a feature -> 28 bytes for POINT types

        self._shp.seek(100 + (28 * (num - 1)) + 12)

        try:
            if num in self._nulls:
                return self._read_null()
            return ...
        except struct.error as err:
            raise shp.ShapefileException(
                f'Cannot access feature {num} due to invalid byte sequencing'
            ) from err
        finally:
            self._shp.seek(0)

    def iter_shapes(self,
                    start: typing.Optional[int] = None,
                    stop: typing.Optional[int] = None,
                    step: typing.Optional[int] = None
                    ) -> typing.Generator[shp.Shape, None, None]:

        if not start:
            start = 1
        elif start

        if not stop:
            stop = self._num_shapes

        if not step:
            step = 1

        # skip: header
        self._shp.seek(100)

        feature = start
        chunk = self._shp.read(28)
        while chunk:
            try:
                yield ...
            except struct.error as err:
                raise shp.ShapefileException(
                    f'Cannot access feature {feature} due to invalid byte sequencing'
                ) from err
            else:
                chunk = self._shp.read(28)
                feature += 1


factory.register_mode('read', 1, PointShapefileReader)
