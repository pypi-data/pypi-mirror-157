from astrodesim.astrodesim import upload_fits as fits
from astrodesim.astrodesim import is_small as small
from astrodesim.astrodesim import resize_smalltolarge as resize
from astrodesim.astrodesim import spectral_index_map as alpha
from astrodesim.astrodesim import make_image as im

#class FeedMeFiles(object):
#    """
#    Class contains two fits files of the same image at different wavelengths

#    Args:
#        file1 (str): path to fits file with image at one wavelength
#        file2 (str): path to fits file with same image at another wavelength 
#    """
#    def __init__(self, file1, file2):
#        self.file1 = file1
#        self.file2 = file2

def map(file1, file2):
    """
    Function outputs a dust emission spectral index map

    Args: 
        files (FeedMeFiles): paths to file1 and file2
    """
    header1, sim_data1 = fits.upload_fits(file1) 
    header2, sim_data2 = fits.upload_fits(file2)

    smallim, deltapix1, new_header, bigim, new_dim, deltapix2, bigheader = small.is_small(sim_data1, sim_data2, header1, header2)

    new_im = resize.resize_smalltolarge(smallim, deltapix1, new_dim, deltapix2)

    desim = alpha.spectral_index_map(new_im, bigim, new_header, bigheader)

    im.make_image(desim)
