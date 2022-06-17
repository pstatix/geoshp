import struct
import typing

from geoshp.shp import factory
from geoshp.shp import reader
import geoshp.shp.shapefile as shp

# TODO: Implement variant w/ null records
# Esri specification allows for each feature type to also have NULL types
#   within the same file for later population
# Currently no support for this but would require shifting bytes and
#   additional checks on write/close operations
# For a ShapefileReader subclass it can exist as a separate entity or be
#   composed into the classes as a member object on shape access


class NullShapefileReader(reader.ShapefileReader):

    def __init__(self, *args, **kwargs) -> None:

        super().__init__(*args, **kwargs)

        self._has_nulls = True

    def _shape(self, num: int) -> shp.Shape:

        # skip: (header) + (number of features) + (specified feature header and type field)
        # number of features: the headers and contents of a feature -> 28 bytes for POINT types

        self._shp.seek(100 + (28 * (num - 1)) + 12)

        try:
            return ...
        except struct.error as err:
            raise shp.ShapefileException(
                f'Cannot access feature {num} due to invalid byte sequencing'
            ) from err

    def iter_shapes(self) -> typing.Generator[shp.Shape, None, None]:

        # skip: header
        # self._shp.seek(100)
        #
        # feature = 1
        # chunk = self._shp.read(28)
        # while chunk:
        #     try:
        #         yield ...
        #     except struct.error as err:
        #         raise shp.ShapefileException(
        #             f'Cannot access feature {feature} due to invalid byte sequencing'
        #         ) from err
        #     else:
        #         chunk = self._shp.read(28)
        #         feature += 1

        pass


factory.register_mode('read', 0, NullShapefileReader)
