#!/usr/bin/env python
""" Basic reading utils.
"""

import os

import gdal
import numpy as np


class HyperSpectralImage(object):
    """ The main class for HyperSpectral Images.
        The hyperspectral data is stored as a numpy array (band, x, y) of float32 numbers at self.data
        Band numbers and corresponding wavelengths are stored as a dictionary self.bands with the following format:
            'Band_{0}'.format(band_number): wavelength
    """
    def __init__(self, input_fld, input_img):
        """ Open the data file with GDAL """
        self.input_folder = input_fld
        self.input_img = input_img
        file_to_read = input_folder + input_image + '/results/REFLECTANCE_{0}.dat'.format(input_image)
        data = gdal.Open(file_to_read)
        if not data:
            filelist = [i for i in os.listdir(input_fld + input_image + '/results/') if '.dat' in i]
            if len(filelist) != 1:
                print('Failed to read the data.')
                return False
            data = gdal.Open(input_folder + input_image + '/results/' + filelist[0])
        if not data:
            print('Failed to read the data.')
            return False
        """ Read metadata (band list), number of raster bands and the data band by band. """
        self.bands = data.GetMetadata_Dict()
        self.raster_count = data.RasterCount
        self.data = np.array([data.GetRasterBand(i + 1).ReadAsArray() for i in range(self.raster_count)])
        print(self.data.shape)
    
    def get_band(self, band_number):
        """ Return band wavelength and image
        """
        if band_number > self.raster_count:
            print('Unable to read band {0}. There are only {1} bands available.'.format(band_number, self.raster_count))
            return False
        return self.bands['Band_{0}'.format(band_number)], self.data[band_number - 1, :, :]


if __name__ == '__main__':
    pass
    input_folder = '/home/dmitrii/data/hypercamera/'
    input_image = '2019-03-05_023'
    img = HyperSpectralImage(input_folder, input_image)
    print(img.bands)
    print(img.raster_count)
