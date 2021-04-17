import numpy as np
from osgeo import gdal, ogr
from math import sqrt, pow, isclose
from colorsys import rgb_to_hsv

gdal.UseExceptions()
ogr.UseExceptions()

def euclidean_distance(x,y):
    return sqrt(sum(pow(a-b,2) for a, b in zip(x, y)))

def normalization(value, stats):
    return (value - stats.minimumValue) / (stats.maximumValue - stats.minimumValue)

def find_region(canvas, layer, point, threshold=0.1):
    """
    Find contiguous region from the start point
    """

    if not isinstance(layer, QgsRasterLayer) or not layer.renderer().type() == 'multibandcolor':
        return None

    # nbands = min(layer.bandCount(),3)

    height = layer.height()
    width = layer.width()

    xsize = layer.rasterUnitsPerPixelX()
    ysize = layer.rasterUnitsPerPixelY()

    # use canvas for array size
    rows = int( (canvas.extent().yMaximum() - canvas.extent().yMinimum()) / ysize )
    cols = int( (canvas.extent().xMaximum() - canvas.extent().xMinimum()) / xsize )

    layer_ymax = layer.extent().yMaximum()
    layer_xmin = layer.extent().xMinimum()

    canvas_ymax = canvas.extent().yMaximum()
    canvas_xmin = canvas.extent().xMinimum()

    shift_r, shift_c = 0, 0
    xmin, ymax = layer_xmin, layer_ymax

    if layer_ymax > canvas_ymax:
        # negative shift in row and adjust ymax 
        canvas_row = int((layer_ymax - canvas_ymax) / ysize)
        shift_r = -canvas_row 
        ymax = layer_ymax - (canvas_row * ysize)

    if canvas_xmin > layer_xmin:
        # negative shift in col and adj xmin
        canvas_col = int((canvas_xmin - layer_xmin) / xsize)
        shift_c = -canvas_col
        xmin = layer_xmin + (canvas_col * xsize)

    #row in pixel coordinates
    row = int((layer_ymax - point.y()) / ysize)

    #col in pixel coordinates
    column = int((point.x() - layer_xmin) / xsize)

    if row < 0 or column < 0 or row >= height or column >= width:
        return None

    provider = layer.dataProvider()
    # bands = [provider.block(1 + n, layer.extent(), width, height) for n in range(nbands)]
    band_red = provider.block(layer.renderer().redBand(), layer.extent(), width, height)
    band_green = provider.block(layer.renderer().greenBand(), layer.extent(), width, height)
    band_blue = provider.block(layer.renderer().blueBand(), layer.extent(), width, height)

    red_stats = layer.dataProvider().bandStatistics(layer.renderer().redBand(), QgsRasterBandStats.All, canvas.extent())
    green_stats = layer.dataProvider().bandStatistics(layer.renderer().greenBand(), QgsRasterBandStats.All, canvas.extent())
    blue_stats = layer.dataProvider().bandStatistics(layer.renderer().blueBand(), QgsRasterBandStats.All, canvas.extent())

    # get target value
    # target = [bands[n].value(row, column) for n in range(nbands)]
    target  = rgb_to_hsv(normalization(band_red.value(row, column), red_stats),
               normalization(band_green.value(row, column), green_stats),
               normalization(band_blue.value(row, column), blue_stats))[0] # only hue

    neighbors = [(-1,-1), (-1,0), (-1,1), (0,1), (1,1), (1,0), (1,-1), (0,-1)]
    stack = [(row, column)] # push start coordinate on stack
    raster = np.zeros((rows, cols), dtype = bool)

    # find region
    while stack:
        r, c = stack.pop()
        try:
            raster[r + shift_r, c + shift_c] = True # shift to fit in array size
        except IndexError: # neighbor is out of canvas
            pass
        for dr, dc in neighbors:
            nr, nc = r + dr, c + dc
            try:
                # value = [bands[n].value(nr, nc) for n in range(nbands)]
                value  = rgb_to_hsv(normalization(band_red.value(nr, nc), red_stats),
                          normalization(band_green.value(nr, nc), green_stats),
                          normalization(band_blue.value(nr, nc), blue_stats))[0] # only hue
                if (nr >= 0 and nc >= 0 and nr < height and nc < width # limits
                    and (nr + shift_r) >= 0 and (nc + shift_c) >= 0
                    and not raster[nr + shift_r, nc + shift_c] # already done
                    and isclose(euclidean_distance([value], [target]), 0, abs_tol=threshold)): # only hue
                    stack.append((nr, nc))
            except IndexError: # neighbor is out of canvas
                pass

    mem_driver = gdal.GetDriverByName('MEM') # debug
    # mem_driver = gdal.GetDriverByName("GTiff") # debug

    # mem_ds = mem_driver.Create('', cols, rows, 1, gdal.GDT_Byte) # debug
    mem_ds = mem_driver.Create('', cols, rows, 1, gdal.GDT_Byte) # debug
    mem_ds.SetGeoTransform((xmin, xsize, 0, ymax, 0, -ysize))
    mem_ds.SetProjection(layer.crs().toWkt())

    # write memory raster
    mem_band = mem_ds.GetRasterBand(1)
    mem_band.WriteArray(raster)
    mem_band.SetNoDataValue(0)

    dst_driver = ogr.GetDriverByName('MEMORY')
    dst_ds = dst_driver.CreateDataSource('out')
    dst_layer = dst_ds.CreateLayer('poly', None, ogr.wkbPolygon)

    fd = ogr.FieldDefn('DN', ogr.OFTInteger)
    dst_layer.CreateField(fd)

    # run the algorithm.
    result = gdal.Polygonize(mem_band, None, dst_layer, 0, ["8CONNECTED=8"])

    if result != 0:
        return None

    dst_layer.SetAttributeFilter('dn = 1')
    feature = dst_layer.GetNextFeature()
    wkt = feature.GetGeometryRef().ExportToWkt()

    feature.Destroy()
    mem_band = None
    mem_ds = None
    dst_ds = None

    geom = QgsGeometry.fromWkt(wkt)
    footprint = QgsRubberBand(canvas, True)
    footprint.setToGeometry(geom, layer.crs())
    footprint.setStrokeColor(QColor(255, 255, 82))
    footprint.setWidth(3)
    footprint.hide()

    return footprint

    # # poligonize memory raster
    # gdal.Polygonize(mem_ds.GetRasterBand(1), None, dst_layer, -1, [], callback=None)

    # geom = next(dst_layer)

    # gdal.Unlink('/vsimem/inmem.vrt')

    # mem_ds = None
    # dst_ds = None

    # return geom.GetGeometryRef()


# Create the destination data source
# x_res = int((x_max - x_min) / pixel_size)
# y_res = int((y_max - y_min) / pixel_size)
# target_ds = gdal.GetDriverByName('MEM').Create('', x_res, y_res, gdal.GDT_Byte)
# target_ds.SetGeoTransform((x_min, pixel_size, 0, y_max, 0, -pixel_size))
# band = target_ds.GetRasterBand(1)
# band.SetNoDataValue(NoData_value)

# from osgeo import osr
# import numpy
# dst_ds.SetGeoTransform([444720, 30, 0, 3751320, 0, -30])
# srs = osr.SpatialReference()
# srs.SetUTM(11, 1)
# srs.SetWellKnownGeogCS("NAD27")
# dst_ds.SetProjection(srs.ExportToWkt())
# raster = numpy.zeros((512, 512), dtype=numpy.uint8)
# dst_ds.GetRasterBand(1).WriteArray(raster)
# # Once we're done, close properly the dataset
# dst_ds = None