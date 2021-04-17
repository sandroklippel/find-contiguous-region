# trocar valores do raster com block

from osgeo import gdal, osr
import numpy as np
 
layer = iface.activeLayer()
 
provider = layer.dataProvider()
 
extent = provider.extent()
 
rows = layer.height()
cols = layer.width()
 
xmin = extent.xMinimum()
ymax = extent.yMaximum()
xsize = layer.rasterUnitsPerPixelX()
ysize = layer.rasterUnitsPerPixelY()
 
print(rows, cols)
 
block = provider.block(1, extent, cols, rows)
 
values = [ [] for i in range(rows) ]
 
for i in range(rows):
    for j in range(cols):
        if block.value(i,j) == 4:
            block.setValue(i,j,25)
            values[i].append(block.value(i,j))
        else:
            values[i].append(block.value(i,j))
 
raster = np.array(values)
 
geotransform = [xmin, xsize, 0, ymax, 0, -ysize]
 
# Create gtif file with rows and columns from parent raster 
driver = gdal.GetDriverByName("GTiff")
 
output_file = "/home/zeito/pyqgis_data/aleatorio_block.tif"
 
dst_ds = driver.Create(output_file, 
                       cols, 
                       rows, 
                       1, 
                       gdal.GDT_Int16)
 
##writting output raster
dst_ds.GetRasterBand(1).WriteArray( raster )
  
#setting extension of output raster
# top left x, w-e pixel resolution, rotation, top left y, rotation, n-s pixel resolution
dst_ds.SetGeoTransform(geotransform)
  
# setting spatial reference of output raster 
epsg = layer.crs().postgisSrid()
srs = osr.SpatialReference()
srs.ImportFromEPSG(epsg)
dst_ds.SetProjection( srs.ExportToWkt() )
  
#Close output raster dataset 
dst_ds = None