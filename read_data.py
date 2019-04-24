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
        self.data_raw = nd.rotate(np.array([data.GetRasterBand(i + 1).ReadAsArray() for i in range(self.raster_count)]), 270, axes=(1, 2))

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
        return self.bands['Band_{0}'.format(band_number)], self.data_raw[band_number - 1, :, :]
    
    def set_white_ref_box(self, x1, x2, y1, y2):
        white_ref_box = self.data_raw[:, y1:y2, x1:x2]
        self.white_ref_spectrum = white_ref_box.mean(axis=(1, 2))
        self.data = self.data_raw / self.white_ref_spectrum[:, np.newaxis, np.newaxis]

    def show_preview(self, band, vertical_lines=np.arange(250, 500, 50)):
        """ Show preview of the data:
            raw image for specified band,
            white reference spectrum,
            corrected image,
            vertical profiles.
        """
        """ WARNING:
            The data is being modified here.
            This is an awful behaviour, that should always be avoided.
            Remove the following line as soon as possible!
        """
        self.data[self.data > 1.5] = 1.5
        f, ax = plt.subplots(2, 2)
        plt.suptitle('Preview of the spectral image, timestamp: {0}'.format(self.datetime), y=0.95, size=16)

        ax[0][0].set_title('RGB sensor'.format(name))
        ax[0][0].imshow(self.preview, origin='upper')

        ax[1][0].set_title('Spectral sensor, {0} nm band'.format(name))
        ax[1][0].imshow(self.data[band - 1, :, :], origin='upper', cmap='inferno')

        ax[0][1].set_title('White reference spectrum')
        ax[0][1].plot(np.array([img.bands['Band_{0}'.format(i + 1)] for i in np.arange(self.raster_count)], dtype=np.float32), self.white_ref_spectrum)
        ax[0][1].grid()

        ax[1][1].set_title('Vertical profile')
        ax[1][1].invert_yaxis()
        for line in vertical_lines:
            ax[1][1].plot(self.data[band, :, line], np.arange(512))
#        ax[1][1].set_xlim([0.5, 1.5])
        ax[1][1].grid()
        ax[1][1].set_xlabel('Reflectance')
        plt.show()


if __name__ == '__main__':
    pass
    input_folder = '/home/dm/work/data/tryoshnikov/snow_pits/2/spectrum/'
    input_image = '2019-04-14_004'
    img = HyperSpectralImage(input_folder, input_image)
    band = 120
    name, data_raw = img.get_band(band)
    img.set_white_ref_box(410, 480, 400, 470)
    img.show_preview(band, vertical_lines=np.arange(150, 351, 50))
