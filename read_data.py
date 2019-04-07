#!/usr/bin/env python
""" Basic reading utils.
"""

import gdal
import numpy as np


class HyperSpectralImage(object):
    def __init__(self, input_fld, input_img):
        self.input_folder = input_fld
        self.input_img = input_img
        file_to_read = input_folder + input_image + '/results/REFLECTANCE_{0}.dat'.format(input_image)
        data = gdal.Open(file_to_read)
        if not data:
            print('Failed to read the data.')
            return False
        self.bands = data.GetMetadata_Dict()
        self.raster_count = data.RasterCount
        self.data = np.array([data.GetRasterBand(i + 1).ReadAsArray() for i in range(self.raster_count)])
        print(self.data.shape)


if __name__ == '__main__':
    pass
    input_folder = '/home/dmitrii/data/hypercamera/'
    input_image = '2019-03-05_023'
#    file_to_read = input_folder + input_image + '/results/REFLECTANCE_{0}.dat'.format(input_image)
#    print(file_to_read)
#    data = gdal.Open(file_to_read)
#    if not data:
#        print('Failed to read the data.')
    img = HyperSpectralImage(input_folder, input_image)
    print(img.bands)
    print(img.raster_count)

