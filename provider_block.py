layer = iface.activeLayer()

provider = layer.dataProvider()

extent = provider.extent()

rows = layer.height()
cols = layer.width()

#xsize = layer.rasterUnitsPerPixelX()
#ysize = layer.rasterUnitsPerPixelY()

print(rows, cols)

block = provider.block(1, extent, cols, rows)