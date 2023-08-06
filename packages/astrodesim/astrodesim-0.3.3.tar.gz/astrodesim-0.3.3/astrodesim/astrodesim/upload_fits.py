from astropy.io import fits

def upload_fits(file):   
    """ 
        Fuction uploads a fits file

        Arg: 
            file (str): path to fits file with desired image

        Returns: 
            header (astropy.io.fits.header.Header): header file
            sim_data (numpy.ndarray): image data

    """
    with fits.open(file) as hdul:
        sim_data = hdul[0].data[0,0,:,:]
        header = hdul[0].header
    
    return header, sim_data
