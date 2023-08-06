def is_small(im1, im2, header1, header2):
    """ 
        Fuction determines which image has the least amount of pixels
        And, initiates necessary parameters for the resize function

        Args: 
            im1 (numpy.ndarray): data for first image
            im2 (numpy.ndarray): data for second image
            header1 (astropy.io.fits.header.Header): fits file header for first image
            header2 (astropy.io.fits.header.Header): fits file header for second image

        Returns: 
            small_im (numpy.ndarray): smallest image data, 
            deltapix1 (float): pixel thickness (deg/pix) of smallest image,
            smallhead (astropy.io.fits.header.Header): header file of smallest image,
            big_im (numpy.ndarray): largest image data,
            new_dim (int): largest image length along x-direction in pixels,
            deltapix2 (float): pixel thickness (deg/pix) of largest image,
            bighead (astropy.io.fits.header.Header): header file of largest image
    """
    # NEED TO RESOLVE CASE FOR SIZE1 == SIZE2

    size1 = im1.shape[0]*im1.shape[1]
    size2 = im2.shape[0]*im2.shape[1]

    if size1 < size2:
        small_im = im1
        deltapix1 = header1['CDELT2']
        smallhead = header1
        big_im = im2
        deltapix2 = header2['CDELT2']
        bighead = header2
        new_dim = header2['NAXIS1']
    else:
        small_im = im2
        deltapix1 = header2['CDELT2']
        smallhead = header2
        big_im = im1
        deltapix2 = header1['CDELT2']
        bighead = header1
        new_dim = header1['NAXIS1']

    return small_im, deltapix1, smallhead, big_im, new_dim, deltapix2, bighead
