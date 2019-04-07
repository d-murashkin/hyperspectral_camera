#!/usr/bin/env python
""" Basic reading utils.
"""

import os
import datetime
from xml.etree import ElementTree

import gdal
import numpy as np
from scipy import ndimage as nd
from matplotlib import pyplot as plt


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
        filelist = [i for i in os.listdir(input_fld + input_image + '/results/') if '.dat' in i]
        if len(filelist) != 1:
            print('Failed to read the data.')
            return False
        self.name = filelist[0][12:-4]
        
        file_to_read = input_folder + input_image + '/results/REFLECTANCE_{0}.dat'.format(self.name)
        data = gdal.Open(file_to_read)
        if not data:
            print('Failed to read the data.')
            return False

        """ Read metadata (band list), number of raster bands and the data band by band. """
        self.bands = data.GetMetadata_Dict()
        self.raster_count = data.RasterCount
        self.data = nd.rotate(np.array([data.GetRasterBand(i + 1).ReadAsArray() for i in range(self.raster_count)]), 270, axes=(1, 2))

        """ Read RGB images """
        self.scene = plt.imread(input_folder + input_image + '/results/RGBSCENE_{0}.png'.format(self.name))
        self.preview = plt.imread(input_folder + input_image + '/results/RGBBACKGROUND_{0}.png'.format(self.name))

        """ Read MetaData """
        metadata = ElementTree.parse(input_folder + input_image + '/metadata/{0}.xml'.format(self.name)).getroot()
        self.integration_time = metadata[2][4].text
        self.lat = metadata[2][1].text
        self.lon = metadata[2][2].text
        self.datetime = datetime.datetime.strptime(metadata[2][0].text[:-6], '%d %b %Y %H:%M:%S')
    
    def get_band(self, band_number):
        """ Return the band wavelength and the image.
        """
        if band_number > self.raster_count:
            print('Unable to read band {0}. There are only {1} bands available.'.format(band_number, self.raster_count))
            return False
        return self.bands['Band_{0}'.format(band_number)], self.data[band_number - 1, :, :]


if __name__ == '__main__':
    pass
    input_folder = '/home/dmitrii/data/hypercamera/'
    input_image = '2019-03-05_023'
#    input_image = 'test'
    img = HyperSpectralImage(input_folder, input_image)
    plt.figure()
    name, data = img.get_band(5)
    plt.imshow(data, origin='upper')
    plt.title('Timestamp: {0}, wavelength={1}nm'.format(img.datetime, name))
    plt.show()
