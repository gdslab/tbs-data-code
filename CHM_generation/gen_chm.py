
######################## Must need to be modified #############################
# # Input point cloud and Output CHM file
fn_las = 'path_of_the_downloded_TBS_point_cloud.laz'
fn_out = 'path_of_the_generated_chm.tif'

# # Parameters:
spatial_resolution = 0.25 # unit: meter
percentile_value_for_chm = 98 # unit: percentile

######################## Can be modified ######################################
no_data_value = -9999 # No data value for CHM, indicating no lidar returns or outside the TBS region
###############################################################################

import os, time
import laspy as lp
import numpy as np
from osgeo import gdal, osr
import rasterio
from rasterio.fill import fillnodata


# # # # # # (1) Import las file # # # # #
las = lp.read(fn_las)

x = np.array(las.x)
y = np.array(las.y)
z = las['HeightAboveGround']
# z = np.array(las.z) # '''If you are interested in ellipsoidal height, use this line instead of the right above'''
del las

# # Define boundary
boundary_tl = [round(np.min(x)), round(np.max(y))] # Top-Left Coordinates (X,Y)
boundary_br = [round(np.max(x)), round(np.min(y))] # Bottom-Rgith Coordinates (X,Y)
print('       # of points in LAS: %d' % len(z))




# # # # # # (2) Convert to the CHM image coordinate # # # # # #
# tic = time.time()

img_x_ndhm = np.round((x - boundary_tl[0])/spatial_resolution)
img_y_ndhm = np.round((boundary_tl[1] - y)/spatial_resolution)

dict_pts_ndhm = {}

n_p = int(0)
num_pts = len(z)
while n_p < num_pts:
    tmp_key = (int(img_x_ndhm[n_p]), int(img_y_ndhm[n_p]))
    if not tmp_key in dict_pts_ndhm.keys():
        dict_pts_ndhm[tmp_key] = [z[n_p]]
    else:
        dict_pts_ndhm[tmp_key].append(z[n_p])
    del tmp_key

    n_p += 1
# print('       Took %.2f secs' %(time.time()-tic)); del tic
del n_p, num_pts




# # # # # # (3) CHM image pixel value assign # # # # # #
# tic = time.time()
img_ysize = int(round(abs((boundary_tl[1]-boundary_br[1])/spatial_resolution)))
img_xsize = int(round(abs((boundary_tl[0]-boundary_br[0])/spatial_resolution)))

nop = np.zeros((img_ysize, img_xsize), dtype=np.uint16)
ndhm = np.zeros((img_ysize, img_xsize), dtype=np.float32) - no_data_value
for n_x in range(img_xsize):
    for n_y in range(img_ysize):
        if (n_x, n_y) in dict_pts_ndhm.keys():
            ndhm[n_y, n_x] = np.percentile(dict_pts_ndhm[(n_x, n_y)], percentile_value_for_chm)
            nop[n_y, n_x] = len(dict_pts_ndhm[(n_x, n_y)])
del n_x, n_y
# print('       Took %.2f secs' %(time.time()-tic)); del tic




# # # # # (4) Save CHM and (optional) smoothing # # # # #
out_format = 'GTiff'
driver = gdal.GetDriverByName(out_format)
out_geotransform = [boundary_tl[0], spatial_resolution, 0,
                    boundary_tl[1], 0, -spatial_resolution]
out_projection = osr.SpatialReference()
out_projection.ImportFromEPSG(32718)

ndhm_ds = driver.Create(fn_out, ndhm.shape[1], ndhm.shape[0], 1, gdal.GDT_Float32)
ndhm_ds.SetGeoTransform(out_geotransform)
ndhm_ds.SetProjection(out_projection.ExportToWkt())
ndhm_ds.GetRasterBand(1).WriteArray(ndhm)
ndhm_ds.GetRasterBand(1).SetNoDataValue(-9999)
ndhm_ds = None
del out_format, driver

# # region - (option) Smoothing holes
# with rasterio.open(fn_out, 'r+') as src:
#     n_band = 1
#     arr = src.read(n_band)
#     arr_filled = fillnodata(arr, mask=nop, max_search_distance = spatial_resolution*10,
#                             smoothing_iterations=0)
#     src.write_band(n_band, arr_filled)
# del src, arr, arr_filled, n_band
# # endregion
print('       Check CHM in %s' % fn_out)

