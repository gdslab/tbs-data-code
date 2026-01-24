'''
    Estimate horizontal shifts between two adjacent CHMs using Mutual Information.
    'estimate_horizontal_shift' was created by Minyoung Jung (jung411@purdue.edu) in 2024.
    Refer to the Data Description paper (link provided in the README) for details.
    For 'mutual_information_2d', please refer to the **reference information provided within the function.    
'''

def estimate_horizontal_shift(fn_ref, fn_sen,
                 size_grid = '200', size_patch = '10', num_patch = '1',
                 shift_x=[0, 10], shift_y=[0,10], buffer_size = 20, nodata = -9999, display=True):
    
    # fn_ref: file path of the reference CHM (.tif)
    # fn_sen: file path of the sensed CHM (which will be aligned to the reference CHM; .tif)
    # size_grid, size_patch, shift_x, shift_y, buffer_size are in meter.
    
    from osgeo import gdal
    from scipy.stats import mode
    import numpy as np
    import matplotlib.pyplot as plt


    size_grid = float(size_grid)
    size_patch = int(size_patch)
    num_patch = int(num_patch)
    nodata = float(nodata)
    buffer_size = float(buffer_size)


    ndhm_ref = gdal.Open(fn_ref)
    ndhm_sen = gdal.Open(fn_sen)

    # region - Define Overlap Area
    ulx_ref, srx_ref, skewx_ref, uly_ref, skewy_ref, sry_ref = ndhm_ref.GetGeoTransform()
    ulx_sen, srx_sen, skewx_sen, uly_sen, skewy_sen, sry_sen = ndhm_sen.GetGeoTransform()

    # if (srx_ref != srx_sen) or (sry_ref != sry_sen):
    #     print('Warning:    The spatial resolutions of input images are not same!')
    #     return
    print('Spatial Resolution\n    REF: %.2f  |  SEN: %.2f' % (srx_ref, srx_sen))
    del skewx_ref, skewy_ref, skewx_sen, skewy_sen

    brx_ref = ulx_ref + (ndhm_ref.RasterXSize) * srx_ref
    bry_ref = uly_ref + (ndhm_ref.RasterYSize) * sry_ref
    brx_sen = ulx_sen + (ndhm_sen.RasterXSize) * srx_sen
    bry_sen = uly_sen + (ndhm_sen.RasterYSize) * sry_sen


    tmp_x = np.sort(np.array([ulx_ref, brx_ref, ulx_sen, brx_sen]))
    tmp_y = np.sort(np.array([uly_ref, bry_ref, uly_sen, bry_sen]))

    overlap_ul = [tmp_x[1], tmp_y[2]]
    overlap_br = [tmp_x[2], tmp_y[1]]
    del tmp_x, tmp_y
    # endregion


    # region - Load Overlapped and Valid NDHM Image
    img_coor_x1 = int(round((overlap_ul[0] - ulx_ref)/srx_ref))
    if img_coor_x1 < 0: img_coor_x1 = 0
    img_coor_y1 = int(round((overlap_ul[1] - uly_ref)/sry_ref))
    if img_coor_y1 < 0: img_coor_y1 = 0
    img_coor_x2 = int(round((overlap_br[0] - ulx_ref)/srx_ref))
    if img_coor_x2 > ndhm_ref.RasterXSize: img_coor_x2 = ndhm_ref.RasterXSize
    img_coor_y2 = int(round((overlap_br[1] - uly_ref)/sry_ref))
    if img_coor_y2 > ndhm_ref.RasterYSize: img_coor_y2 = ndhm_ref.RasterYSize
    # print(img_coor_x1, img_coor_y1, img_coor_x2, img_coor_y2, img_coor_x2-img_coor_x1+1, img_coor_y2-img_coor_y1+1)
    ndhm_img_ref = ndhm_ref.GetRasterBand(1).ReadAsArray(img_coor_x1, img_coor_y1,
                                                        img_coor_x2-img_coor_x1,
                                                        img_coor_y2-img_coor_y1)
    tmp_coor1 = np.argwhere(ndhm_img_ref != nodata)
    ymin1, xmin1 = np.min(tmp_coor1, axis=0)
    ymax1, xmax1 = np.max(tmp_coor1, axis=0)


    img_coor_x1 = int(round((overlap_ul[0] - ulx_sen)/srx_sen))
    if img_coor_x1 < 0: img_coor_x1 = 0
    img_coor_y1 = int(round((overlap_ul[1] - uly_sen)/sry_sen))
    if img_coor_y1 < 0: img_coor_y1 = 0
    img_coor_x2 = int(round((overlap_br[0] - ulx_sen)/srx_sen))
    if img_coor_x2 > ndhm_sen.RasterXSize: img_coor_x2 = ndhm_sen.RasterXSize
    img_coor_y2 = int(round((overlap_br[1] - uly_sen)/sry_sen))
    if img_coor_y2 > ndhm_sen.RasterYSize: img_coor_y2 = ndhm_sen.RasterYSize
    # print(img_coor_x1, img_coor_y1, img_coor_x2, img_coor_y2, img_coor_x2-img_coor_x1+1, img_coor_y2-img_coor_y1+1)
    ndhm_img_sen = ndhm_sen.GetRasterBand(1).ReadAsArray(img_coor_x1, img_coor_y1,
                                                        img_coor_x2-img_coor_x1,
                                                        img_coor_y2-img_coor_y1)
    tmp_coor2 = np.argwhere(ndhm_img_sen != nodata)
    ymin2, xmin2 = np.min(tmp_coor2, axis=0)
    ymax2, xmax2 = np.max(tmp_coor2, axis=0)

    tmp_y = np.sort(np.array([ymin1, ymin2, ymax1, ymax2]))
    tmp_x = np.sort(np.array([xmin1, xmin2, xmax1, xmax2]))

    buffer = int(round(buffer_size/srx_ref)) # unit: pixel
    img_ref = ndhm_img_ref[tmp_y[1]+buffer:tmp_y[2]-buffer, tmp_x[1]+buffer:tmp_x[2]-buffer]
    img_sen = ndhm_img_sen[tmp_y[1]+buffer:tmp_y[2]-buffer, tmp_x[1]+buffer:tmp_x[2]-buffer]
    del img_coor_x1, img_coor_y1, img_coor_x2, img_coor_y2, tmp_coor1, tmp_coor2,\
        ymin1, xmin1, ymax1, xmax1, ymin2, xmin2, ymax2, xmax2, tmp_x, tmp_y, ndhm_img_ref, ndhm_img_sen

    # endregion

    # region - Image Display and size
    if display:
        fig = plt.figure()
        ax = fig.add_subplot(1,2,1)
        ax.imshow(img_ref, clim = (0, np.percentile(img_ref, 98, axis=None)))
        plt.axis('off')
        ax = fig.add_subplot(1,2,2)
        ax.imshow(img_sen, clim = (0, np.percentile(img_sen, 98, axis=None)))
        plt.axis('off')
        plt.show()

    size_y_img_ref, size_x_img_ref = img_ref.shape
    size_y_img_sen, size_x_img_sen = img_sen.shape

    size_y_grd_ref = size_y_img_ref * abs(sry_ref)
    size_x_grd_ref = size_x_img_ref * abs(srx_ref)
    size_y_grd_sen = size_y_img_sen * abs(sry_sen)
    size_x_grd_sen = size_x_img_sen * abs(srx_sen)

    if display:
        print('\nReference Image Size\n    Pixel: %d by %d\n    Ground: %.2f by %.2f' % \
            (size_x_img_ref, size_y_img_ref, size_x_grd_ref, size_y_grd_ref))
        print('Sensed Image Size\n    Pixel: %d by %d\n    Ground: %.2f by %.2f' % \
            (size_x_img_sen, size_y_img_sen, size_x_grd_sen, size_y_grd_sen))

    # endregion

    # region - Gridding

    shift_init_x = round(shift_x[0]/srx_ref)
    shift_range_x = round(shift_x[1]/srx_ref)
    shift_init_y = round(shift_y[0]/sry_ref)
    shift_range_y = round(shift_y[1]/sry_ref)

    shifts_x = np.arange(shift_init_x-shift_range_x, shift_init_x+shift_range_x+1, 1).tolist() # unit: pixel
    # print(shifts_x)
    shifts_y = np.arange(shift_init_y-shift_range_y, shift_init_y+shift_range_y+1, -1).tolist()
    # print(shifts_y)
    
    size_grid_img   = int(round(size_grid / srx_ref))
    num_grid_x = int(np.ceil(img_ref.shape[1] / size_grid_img))
    if num_grid_x < 1: num_grid_x = 2
    num_grid_y = int(np.ceil(img_ref.shape[0] / size_grid_img))
    if num_grid_y < 1: num_grid_y = 2

    intervals_x = np.round(np.linspace(0, img_ref.shape[1], num_grid_x))
    if np.min(shifts_x) < 0: intervals_x[0] = abs(np.min(shifts_x))
    if np.max(shifts_x) > 0: intervals_x[-1] = img_ref.shape[1]-np.max(shifts_x)
    # if np.max(shifts_x) > 0: intervals_x[0] = np.max(shifts_x)
    # if np.min(shifts_x) < 0: intervals_x[-1] = img_ref.shape[1] + np.min(shifts_x)
    intervals_y = np.round(np.linspace(0, img_ref.shape[0], num_grid_y))
    if np.min(shifts_y) < 0: intervals_y[0] = abs(np.min(shifts_y))
    if np.max(shifts_y) > 0: intervals_y[-1] = img_ref.shape[0]-np.max(shifts_y)
    # if np.max(shifts_y) > 0: intervals_y[0] = np.max(shifts_y)
    # if np.min(shifts_y) < 0: intervals_y[-1] = img_ref.shape[0] + np.min(shifts_y)
    # print(intervals_x)
    # print(intervals_y)
    print('\nGrid Number:', len(intervals_x)-1, len(intervals_y)-1)
    # endregion


    # region - MI for selected patches
    size_patch_img  = int(round(size_patch / srx_ref / 2))
    mis_calculated = {}
    lut = []
    for i in range(len(intervals_x)-1):
        for j in range(len(intervals_y)-1):
            # print('[%d, %d] Grid' % (i, j))

            x1 = int(intervals_x[i])
            x2 = int(intervals_x[i+1])
            y1 = int(intervals_y[j])
            y2 = int(intervals_y[j+1])
            
            grid_size_x = x2-x1
            grid_size_y = y2-y1
            seed_x = np.random.choice(grid_size_x-size_patch_img, num_patch, replace=False) + size_patch_img
            seed_y = np.random.choice(grid_size_y-size_patch_img, num_patch, replace=False) + size_patch_img

            
            for n_p in range(num_patch):
                
                patch_img_ref = img_ref[y1:y2, x1:x2][seed_y[n_p]-size_patch_img:seed_y[n_p]+size_patch_img,
                                                    seed_x[n_p]-size_patch_img:seed_x[n_p]+size_patch_img]
                valid_ref = (patch_img_ref != nodata)

                patch_mis = np.zeros((len(shifts_y), len(shifts_x)))
                for n_dx in range(len(shifts_x)):
                    for n_dy in range(len(shifts_y)):
                        shift = [int(shifts_x[n_dx]), int(shifts_y[n_dy])]
                        # print('      Shift (x, y)', shift) # true_loc = loc+shift
                        
                        tmp_img = img_sen[y1+shift[1]:y2+shift[1], x1+shift[0]:x2+shift[0]]
                        patch_img_sen = tmp_img[seed_y[n_p]-size_patch_img:seed_y[n_p]+size_patch_img,
                                             seed_x[n_p]-size_patch_img:seed_x[n_p]+size_patch_img]
                        del tmp_img
                        valid_sen = (patch_img_sen != nodata)
                        valid_both = (valid_ref * valid_sen).ravel()
                        # if np.sum(valid_both) != len(valid_both): dafdsf
                        # print(patch_img_sen.ravel()[valid_both])
                        patch_mis[n_dy, n_dx] = mutual_information_2d(patch_img_ref.ravel()[valid_both], patch_img_sen.ravel()[valid_both])
                
                mi_mx = np.max(patch_mis, axis=None)
                position = np.argwhere(patch_mis==mi_mx)
                if len(position) > 1:
                    print('  Patch location: [%d, %d]' % (seed_x[n_p], seed_y[n_p]))
                    print('    Warning: The MI results has multiple maximum points\n')
                else:
                    dx = shifts_x[position[0, 1]]
                    dy = shifts_y[position[0, 0]]
                    mis_calculated[(x1+seed_x[n_p], y1+seed_y[n_p])] = patch_mis
                    # print('  Patch location: [%d, %d]' % (seed_x[n_p], seed_y[n_p]))
                    # print('    Estimated Shift: %.2f in X' % (dx*srx_ref))
                    # print('                   : %.2f in Y' % (dy*srx_ref))
                    # print('    Calculated MI score: %.3f\n' % mi_mx)
                    lut.append([x1+seed_x[n_p], y1+seed_y[n_p], dx, dy, mi_mx])
    lut = np.array(lut)
    # endregion

    dx, count_x = mode(lut[:,2])
    dy, count_y = mode(lut[:,3])

    shift_x = dx * srx_ref
    shift_y = dy * sry_ref

    print('Estimated Shifts in X and Y: [%.2f, %.2f]\n    with counts: [%d, %d] out of %d' % (shift_x, shift_y, count_x, count_y, len(lut)))

    if display:
        img_mi = mis_calculated[(lut[lut[:,-1]==np.max(lut[:, -1]),0][0], lut[lut[:,-1]==np.max(lut[:, -1]),1][0])]
        plt.figure()
        plt.imshow(img_mi), plt.colorbar(), plt.axis('off')
        plt.show()
    
    plt.figure()
    plt.imshow(img_ref, clim=(0,55))
    for n_p in range(len(lut)):
        tmp = lut[n_p, :]
        scale = 10
        plt.arrow(tmp[0], img_ref.shape[0]-tmp[1], tmp[2]*scale, -tmp[3]*scale,
                  ec='red')

    return (shift_x, shift_y), lut


def mutual_information_2d(x, y, sigma=1, normalized=False):
    """
    Computes (normalized) mutual information between two 1D variate from a
    joint histogram.
    Parameters
    ----------
    x : 1D array
        first variable
    y : 1D array
        second variable
    sigma: float
        sigma for Gaussian smoothing of the joint histogram
    Returns
    -------
    nmi: float
        the computed similariy measure
    """

    from scipy import ndimage
    import numpy as np

    EPS = np.finfo(float).eps



    bins = (256, 256)

    jh = np.histogram2d(x, y, bins=bins)[0]

    # smooth the jh with a gaussian filter of given sigma
    ndimage.gaussian_filter(jh, sigma=sigma, mode='constant',
                                 output=jh)

    # compute marginal histograms
    jh = jh + EPS
    sh = np.sum(jh)
    jh = jh / sh
    s1 = np.sum(jh, axis=0).reshape((-1, jh.shape[0]))
    s2 = np.sum(jh, axis=1).reshape((jh.shape[1], -1))

    # Normalised Mutual Information of:
    # Studholme,  jhill & jhawkes (1998).
    # "A normalized entropy measure of 3-D medical image alignment".
    # in Proc. Medical Imaging 1998, vol. 3338, San Diego, CA, pp. 132-143.
    if normalized:
        mi = ((np.sum(s1 * np.log(s1)) + np.sum(s2 * np.log(s2)))
                / np.sum(jh * np.log(jh))) - 1
    else:
        mi = ( np.sum(jh * np.log(jh)) - np.sum(s1 * np.log(s1))
               - np.sum(s2 * np.log(s2)))

    return mi


# # # # Example code to run # # # #
# shifts_h, mis = estimate_horizontal_shift(
#     filepath_chm1,
#     filepath_chm2,
#     size_grid = '50', num_patch = '2',
#     shift_x = [0, 5], shift_y = [0, 5], buffer_size = 50)