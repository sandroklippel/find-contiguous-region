# get row col from coordinates

def get_row_col(layer, point):

    width = layer.width()
    height = layer.height()

    xsize = layer.rasterUnitsPerPixelX()
    ysize = layer.rasterUnitsPerPixelY()

    extent = layer.extent()

    ymax = extent.yMaximum()
    xmin = extent.xMinimum()

    #row in pixel coordinates
    row = int((ymax - point.y()) / ysize )

    #row in pixel coordinates
    column = int((point.x() - xmin) / xsize )

    if row <= 0 or column <=0 or row > height or column > width:
        row = "out of extent"
        column = "out of extent"

    return row, column