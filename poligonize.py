import numpy as np
from osgeo import gdal, ogr

gdal.UseExceptions()
ogr.UseExceptions()

def poligonize():
    """
    simple test function
    """

    src_ds = gdal.Open('/home/sandro/Documentos/GIS/testes/find_region.tif')
    src_band = src_ds.GetRasterBand(1)

    # Create a memory OGR datasource to put results in.
    mem_drv = ogr.GetDriverByName('Memory')
    mem_ds = mem_drv.CreateDataSource('out')

    mem_layer = mem_ds.CreateLayer('poly', None, ogr.wkbPolygon)

    fd = ogr.FieldDefn('DN', ogr.OFTInteger)
    mem_layer.CreateField(fd)

    # run the algorithm.
    result = gdal.Polygonize(src_band, None, mem_layer, 0, ["8CONNECTED=8"])

    mem_layer.SetAttributeFilter('dn = 1')
    feature = mem_layer.GetNextFeature()
    wkt = feature.GetGeometryRef().ExportToWkt()

    feature.Destroy()
    src_band = None
    src_ds = None
    mem_ds = None

    return {'result': result, 'wkt': wkt}
