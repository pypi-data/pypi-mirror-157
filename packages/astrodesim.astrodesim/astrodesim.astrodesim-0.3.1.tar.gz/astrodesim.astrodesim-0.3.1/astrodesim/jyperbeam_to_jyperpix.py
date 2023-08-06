import numpy as np

def jyperbeam_to_jyperpix(header, data):
    """ 
        Fuction converts Jy/beam to Jy/pix

        Arg: 
            header (astropy.io.fits.header.Header): fits file header
            data (numpy.ndarray): image data

        Returns: 
            Jyperpix_data (numpy.ndarray): image data in Jy/pix

    """
    convert = np.pi/180 # deg to rads
    fwhm_to_sigma = 1./(8*np.log(2))**0.5

    bmaj = header['BMAJ']*convert
    bmin = header['BMIN']*convert

    beam_area = 2.*np.pi*(bmaj*bmin*fwhm_to_sigma*2) # in staradians
    Jyperpix_data = data/beam_area

    return Jyperpix_data
