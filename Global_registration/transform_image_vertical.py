'''
    Transform a digital elevation model using a shift estimated by 'estimate_vertical_shift.py'.
    Created by Minyoung Jung (jung411@purdue.edu)
'''  


def transform_image_vertical(fn_in, fn_out, shift_vertical):
    from osgeo import gdal
    import numpy as np

    shift_z = float(shift_vertical[0])

    out_format = 'GTiff'
    driver = gdal.GetDriverByName(out_format)

    input_raster = gdal.Open(fn_in)
    tmp_img = input_raster.ReadAsArray()
    if len(tmp_img.shape) > 2: 
        # tar_ds = driver.Create(fn_out, tmp_img.shape[2], tmp_img.shape[1], tmp_img.shape[0], gdal.GDT_Float32)
        tmp_f = 'Check the number of the input image bands'
        return tmp_f
    else:
        tar_ds = driver.Create(fn_out, tmp_img.shape[1], tmp_img.shape[0], 1, gdal.GDT_Float32)

    tar_ds.SetGeoTransform(input_raster.GetGeoTransform())
    tar_ds.SetProjection(input_raster.GetProjection())
    
    if len(tmp_img.shape) > 2:
        tmp_f = 'Check the number of the input image bands'
        return tmp_f
        # for n_band in range(len(tmp_img.shape)-1):
        #     tar_ds.GetRasterBand(n_band+1).WriteArray(tmp_img[n_band, :, :])
        #     tar_ds.GetRasterBand(n_band+1).SetNoDataValue(input_raster.GetRasterBand(n_band+1).GetNoDataValue())
    else:
        no_data = input_raster.GetRasterBand(1).GetNoDataValue()
        final_img = tmp_img-shift_z
        final_img[tmp_img==no_data] = no_data
        tar_ds.GetRasterBand(1).WriteArray(final_img)
        tar_ds.GetRasterBand(1).SetNoDataValue(input_raster.GetRasterBand(1).GetNoDataValue())
    tar_ds = None
    print('Check: ', fn_out)


# # # # Example code to run # # # # 
# transform_image_vertical(filepath_sensed_horizontallyshifted_DTM, filepath_out_DEM, -shift_v)