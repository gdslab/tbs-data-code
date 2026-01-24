'''
    Estimate the vertical shift between two adjacent DTMs.
    Created by Minyoung Jung (jung411@purdue.edu) in 2022.
    Modified by Minyoung Jung in 2024.
    Refer to the data description paper (link provided in the README) for details.
'''


def estimate_vertical_shift(fn_ref, fn_sen, buffer = 100, display=True):
    '''buffer unit : pixel'''
    from osgeo import gdal
    import numpy as np
    import matplotlib.pyplot as plt
    
    dem_ref = gdal.Open(fn_ref)
    dem_sen = gdal.Open(fn_sen)

    

    # region - Define Overlap Area
    ulx_ref, srx_ref, skewx_ref, uly_ref, skewy_ref, sry_ref = dem_ref.GetGeoTransform()
    ulx_sen, srx_sen, skewx_sen, uly_sen, skewy_sen, sry_sen = dem_sen.GetGeoTransform()
    if (srx_ref != srx_sen) or (sry_ref != sry_sen):
        print('Warning:    The spatial resolutions of input images are not same!')
    print('Spatial Resolution\n    REF: %.2f\n    SEN: %.2f' % (srx_ref, srx_sen))

    brx_ref = ulx_ref + (dem_ref.RasterXSize) * srx_ref
    bry_ref = uly_ref + (dem_ref.RasterYSize) * sry_ref
    brx_sen = ulx_sen + (dem_sen.RasterXSize) * srx_sen
    bry_sen = uly_sen + (dem_sen.RasterYSize) * sry_sen

    tmp_x = np.sort(np.array([ulx_ref, brx_ref, ulx_sen, brx_sen]))
    tmp_y = np.sort(np.array([uly_ref, bry_ref, uly_sen, bry_sen]))

    overlap_ul = [tmp_x[1], tmp_y[2]]
    overlap_br = [tmp_x[2], tmp_y[1]]
    # print(overlap_ul)
    # print(overlap_br)
    del tmp_x, tmp_y
    # endregion


    # region - Load Overlapped and Valid DEM Image

    img_coor_x1 = int(round((overlap_ul[0] - ulx_ref)/srx_ref))
    if img_coor_x1 < 0: img_coor_x1 = 0
    img_coor_y1 = int(round((overlap_ul[1] - uly_ref)/sry_ref))
    if img_coor_y1 < 0: img_coor_y1 = 0
    img_coor_x2 = int(round((overlap_br[0] - ulx_ref)/srx_ref))
    if img_coor_x2 > dem_ref.RasterXSize: img_coor_x2 = dem_ref.RasterXSize
    img_coor_y2 = int(round((overlap_br[1] - uly_ref)/sry_ref))
    if img_coor_y2 > dem_ref.RasterYSize: img_coor_y2 = dem_ref.RasterYSize
    # print(img_coor_x1, img_coor_y1, img_coor_x2, img_coor_y2, img_coor_x2-img_coor_x1+1, img_coor_y2-img_coor_y1+1)
    ndhm_img_ref = dem_ref.GetRasterBand(1).ReadAsArray(img_coor_x1, img_coor_y1,
                                                        img_coor_x2-img_coor_x1,
                                                        img_coor_y2-img_coor_y1)
    tmp_coor1 = np.argwhere(ndhm_img_ref != -9999)
    ymin1, xmin1 = np.min(tmp_coor1, axis=0)
    ymax1, xmax1 = np.max(tmp_coor1, axis=0)


    img_coor_x1 = int(round((overlap_ul[0] - ulx_sen)/srx_sen))
    if img_coor_x1 < 0: img_coor_x1 = 0
    img_coor_y1 = int(round((overlap_ul[1] - uly_sen)/sry_sen))
    if img_coor_y1 < 0: img_coor_y1 = 0
    img_coor_x2 = int(round((overlap_br[0] - ulx_sen)/srx_sen))
    if img_coor_x2 > dem_sen.RasterXSize: img_coor_x2 = dem_sen.RasterXSize
    img_coor_y2 = int(round((overlap_br[1] - uly_sen)/sry_sen))
    if img_coor_y2 > dem_sen.RasterYSize: img_coor_y2 = dem_sen.RasterYSize
    # print(img_coor_x1, img_coor_y1, img_coor_x2, img_coor_y2, img_coor_x2-img_coor_x1+1, img_coor_y2-img_coor_y1+1)
    ndhm_img_sen = dem_sen.GetRasterBand(1).ReadAsArray(img_coor_x1, img_coor_y1,
                                                        img_coor_x2-img_coor_x1,
                                                        img_coor_y2-img_coor_y1)
    tmp_coor2 = np.argwhere(ndhm_img_sen != -9999)
    ymin2, xmin2 = np.min(tmp_coor2, axis=0)
    ymax2, xmax2 = np.max(tmp_coor2, axis=0)

    tmp_y = np.sort(np.array([ymin1, ymin2, ymax1, ymax2]))
    tmp_x = np.sort(np.array([xmin1, xmin2, xmax1, xmax2]))


    img_ref = ndhm_img_ref[tmp_y[1]+buffer:tmp_y[2]-buffer, tmp_x[1]+buffer:tmp_x[2]-buffer]
    img_sen = ndhm_img_sen[tmp_y[1]+buffer:tmp_y[2]-buffer, tmp_x[1]+buffer:tmp_x[2]-buffer]
    del img_coor_x1, img_coor_y1, img_coor_x2, img_coor_y2, tmp_coor1, tmp_coor2,\
        ymin1, xmin1, ymax1, xmax1, ymin2, xmin2, ymax2, xmax2, tmp_x, tmp_y, ndhm_img_ref, ndhm_img_sen

    # endregion

    # region - Debug. Image Display
    if display:
        fig = plt.figure()
        ax = fig.add_subplot(1,2,1)
        ax.imshow(img_ref, clim = (0, np.max(img_ref, axis=None)))
        plt.axis('off')
        ax = fig.add_subplot(1,2,2)
        ax.imshow(img_sen, clim = (0, np.max(img_sen, axis=None)))
        plt.axis('off')
        plt.show()
    # endregion


    mask = (img_ref != -9999) * (img_sen != -9999)
    img_dif = img_ref-img_sen
    tmp_loc = np.argwhere(mask == 0)
    for n_p in range(len(tmp_loc)):
        img_dif[tmp_loc[n_p, 0], tmp_loc[n_p,1]] = -9999
    del tmp_loc, n_p, mask

    tmp_bin = np.arange(-10, 10, 0.1)
    hist, bin_edges = np.histogram(img_dif.ravel(), bins= tmp_bin, density=False)
    shift_z=(tmp_bin[:-1][hist==np.max(hist)]+tmp_bin[1:][hist==np.max(hist)])/2
    print(shift_z)

    if display:
        plt.figure()
        plt.hist(img_dif.ravel(), bins=np.arange(shift_z-5,shift_z+5,0.1))
        plt.figure()
        plt.imshow(img_dif, clim=(shift_z-5,shift_z+5)), plt.colorbar()
        plt.axis('off')
        plt.show()
    return shift_z    


# # # # Example code to run # # # # 
# shift_v = estimate_vertical_shift(filepath_dtm1, filepath_dtm2)