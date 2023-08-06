import math

def spectral_index_conversion(flux1, flux2, wavelength1, wavelength2):
    """ 
        Fuction computes the dust emission spectral index from two intensity values

        Arg: 
            flux1 (float): Intensity (Jy/pix) of a single pixel from first image
            flux2 (float): Intensity (Jy/pix) of a single pixel from second image
            wavelength1 (float): wavelength of first image
            wavelength2 (float): wavelength of second image

        Returns: 
            alpha (float): dust emission spectral index
    """   
    flux_replacement = 1e-34
    
    # corrects for negative or zero values to be used in log calculations
    if flux1 < 0:
        flux1 = flux_replacement
        
    if flux2 <= 0:
        flux2 = flux_replacement

    flux_rat = math.log10(flux1/flux2)
    wavelength_rat = math.log10(wavelength2/wavelength1)
    alpha = flux_rat/wavelength_rat 

    return alpha
