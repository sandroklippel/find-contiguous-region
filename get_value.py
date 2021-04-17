def get_value(layer, row, col):
    
    extent = layer.extent()
    rows = layer.height()
    cols = layer.width()
    
    provider = layer.dataProvider()
    block = provider.block(1, extent, cols, rows)

    return block.value(row, col)

def get_value_canvas(canvas, layer, point):

    extent = canvas.extent()
    xsize = layer.rasterUnitsPerPixelX()
    ysize = layer.rasterUnitsPerPixelY()

    rows = int( (extent.yMaximum() - extent.yMinimum()) / ysize )
    cols = int( (extent.xMaximum() - extent.xMinimum()) / xsize )

    #row in pixel coordinates
    row = int( (extent.yMaximum()- point.y()) / ysize )

    #col in pixel coordinates
    col = int( (point.x() - extent.xMinimum()) / xsize )

    provider = layer.dataProvider()
    block = provider.block(1, extent, cols, rows)

    return block.value(row, col)