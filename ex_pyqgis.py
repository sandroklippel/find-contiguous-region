filename = "/home/zeito/pyqgis_data/aleatorio.tif" #path to raster

layer = QgsRasterLayer(filename,
                       "my_raster")

provider = layer.dataProvider()

extent = layer.extent()

xmin, ymin, xmax, ymax = extent.toRectF().getCoords()

cols = layer.width()
rows = layer.height()

pixelWidth = layer.rasterUnitsPerPixelX()
pixelHeight = layer.rasterUnitsPerPixelY()

block = provider.block(1, extent, cols, rows)

points_list = [ (355278.165927, 4473095.13829), (355978.319525, 4472871.11636) ]#list of X,Y coordinates

for point in points_list:
    col = int((point[0] - xmin) / pixelWidth)
    row = int((ymax - point[1] ) / pixelHeight)

    print row,col, block.value(row, col)