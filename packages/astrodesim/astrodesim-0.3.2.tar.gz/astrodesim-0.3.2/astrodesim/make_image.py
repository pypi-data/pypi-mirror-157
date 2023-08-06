from astropy.visualization import (AsinhStretch, ImageNormalize)
import matplotlib.pyplot as plt
import numpy as np

def make_image(data):
    """
        Function makes image

        Arg: 
            data (numpy.ndarray): image data

        Outputs: 
            plot of image
    """
    # Creates image for simulated observation at 0.87 mm 
    fig = plt.figure(figsize = (8,8))
    vmax = np.percentile(data, 99)
    vmin = np.percentile(data, 1)
    norm = ImageNormalize(vmin=vmin, vmax=vmax, stretch=AsinhStretch())
    snu = np.squeeze(data)

    im = plt.imshow(snu, origin='lower', cmap='inferno', norm=norm)
