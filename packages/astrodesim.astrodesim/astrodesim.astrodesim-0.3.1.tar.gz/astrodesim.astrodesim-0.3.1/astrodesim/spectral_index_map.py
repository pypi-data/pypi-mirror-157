import numpy as np
from astrodesim.astrodesim import jyperbeam_to_jyperpix as convert
from astrodesim.astrodesim import spectral_index_conversion as make

def spectral_index_map(data1, data2, header1, header2):
    """ 
        Fuction creates image data in dust emission spectral index units from two images at different wavelengths

        Arg: 
            data1 (numpy.ndarray): data of first image
            data2 (numpy.ndarray): data of second image
            header1 (astropy.io.fits.header.Header): fits file header of first image
            header2 (astropy.io.fits.header.Header): fits file header of second image

        Returns: 
            im3 (numpy.ndarray): image data in dust emission spectral index units
    """
    # Converts intensity of image data from Jy/beam to Jy/pix
    im1 = convert.jyperbeam_to_jyperpix(header1, data1) 
    im2 = convert.jyperbeam_to_jyperpix(header2, data2) 

    c = 299792258 # speed of light in m/s

    lambda1 = c/header1['CRVAL4'] # frequency in Hz (need to test input for this)
    lambda2 = c/header2['CRVAL4'] # frequency in Hz 

    width = im1.shape[0]
    length = im2.shape[1]

    im3 = np.empty((width, length))

    for i in range(width):
        for j in range(length):
            flux1 = im1[i,j]
            flux2 = im2[i,j]
            im3[i,j] = make.spectral_index_conversion(flux1, flux2, lambda1, lambda2)

    return im3
