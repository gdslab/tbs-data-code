'''
    Transform raster data (.tif) using shifts estimated by 'estimate_horizontal_shift.py'.
    Created by Minyoung Jung (jung411@purdue.edu) 
'''    

def transform_image(fn_in, fn_out, shifts):
    from osgeo import gdal

    shift_x, shift_y = shifts

    out_format = 'GTiff'
    driver = gdal.GetDriverByName(out_format)

    input_raster = gdal.Open(fn_in)

    tmp_img = input_raster.ReadAsArray()

    if len(tmp_img.shape) > 2: 
        tar_ds = driver.Create(fn_out, tmp_img.shape[2], tmp_img.shape[1], tmp_img.shape[0], gdal.GDT_Float32)
    else:
        tar_ds = driver.Create(fn_out, tmp_img.shape[1], tmp_img.shape[0], 1, gdal.GDT_Float32)
    
    tmp = input_raster.GetGeoTransform()
    out_transform = (tmp[0]-shift_x, tmp[1], tmp[2], tmp[3]-shift_y, tmp[4], tmp[5]); del tmp
    
    tar_ds.SetGeoTransform(out_transform)
    tar_ds.SetProjection(input_raster.GetProjection())
    
    if len(tmp_img.shape) > 2:
        for n_band in range(len(tmp_img.shape)-1):
            tar_ds.GetRasterBand(n_band+1).WriteArray(tmp_img[n_band, :, :])
            tar_ds.GetRasterBand(n_band+1).SetNoDataValue(input_raster.GetRasterBand(n_band+1).GetNoDataValue())
    else:
        tar_ds.GetRasterBand(1).WriteArray(tmp_img)
        tar_ds.GetRasterBand(1).SetNoDataValue(input_raster.GetRasterBand(1).GetNoDataValue())
    tar_ds = None
    print('Check: ', fn_out)
    


# # # # Example code to run # # # #
# transform_image(filepath_sensed_raster, filepath_shifted_raster, shifts_h)
