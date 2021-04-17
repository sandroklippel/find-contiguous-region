import numpy as np
from osgeo import gdal, ogr

gdal.UseExceptions()
ogr.UseExceptions()

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

    if row < 0 or column < 0 or row >= height or column >= width:
        row = -1
        column = -1

    return row, column

def get_value(layer, row, col):
    
    extent = layer.extent()
    rows = layer.height()
    cols = layer.width()
    
    provider = layer.dataProvider()
    block = provider.block(1, extent, cols, rows)

    return block.value(row, col)

def get_contiguous_region(layer, point):
    """
    Return contiguous region from the start point
    """
    
    row, col = get_row_col(layer, point)
    print('Row: {}, Col: {}'.format(row, col))
    
    height = layer.height()
    width = layer.width()
    
    val = get_value(layer, row, col)
    print(f'Value: {val}')

    neighbours = [(-1,-1), (-1,0), (-1,1), (0,1), (1,1), (1,0), (1,-1), (0,-1)]
    stack = [(row, col)] # push start coordinate on stack
    coords = []

    while stack:
        r, c = stack.pop()
        coords.append((r, c))
        for dr, dc in neighbours:
            nr, nc = r + dr, c + dc
            if (nr >= 0 and nc >= 0 and nr < height and nc < width # limits
                and (nr, nc) not in coords and get_value(layer, nr, nc) == val):
                stack.append((nr, nc))
    
    return coords

def region_grow(layer, point):
    """
    Return contiguous region from the start point
    """
    
    row, col = get_row_col(layer, point)
    
    height = layer.height()
    width = layer.width()
    
    val = get_value(layer, row, col)

    neighbours = [(-1,-1), (-1,0), (-1,1), (0,1), (1,1), (1,0), (1,-1), (0,-1)]
    stack = [(row, col)] # push start coordinate on stack
    raster = np.zeros((height, width), dtype = bool)

    while stack:
        r, c = stack.pop()
        raster[r, c] = True
        for dr, dc in neighbours:
            nr, nc = r + dr, c + dc
            if (nr >= 0 and nc >= 0 and nr < height and nc < width # limits
                and not raster[nr, nc] # already done
                and get_value(layer, nr, nc) == val):
                stack.append((nr, nc))

    mem_drv = gdal.GetDriverByName('MEM')
    dest = mem_drv.Create('', rast.RasterXSize, rast.RasterYSize, 1, gdal.GDT_Float32) 
    
    return None