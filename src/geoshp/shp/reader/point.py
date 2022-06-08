from geoshp.shp import factory
from geoshp.shp import reader


class PointShapefileReader(reader.ShapefileReader):
    pass


factory.register_mode('read', 1, PointShapefileReader)
