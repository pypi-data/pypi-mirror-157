import upload_fits
import is_small
import resize_smalltolarge
import spectral_index_map
import make_image

path = '/Users/colinmoyer/Downloads/'
file1 = path + '/isoscat_0.87mm_inc45.fits'
file2 = path + '/isoscat_1.3mm_inc45.fits'
header1, sim_data1 = upload_fits(file1) # 0.87 mm data & header
header2, sim_data2 = upload_fits(file2) # 1.3 mm data & header

smallim, deltapix1, new_header, bigim, new_dim, deltapix2, bigheader = is_small(sim_data1, sim_data2, header1, header2)

new_im = resize_smalltolarge(smallim, deltapix1, new_dim, deltapix2)

desim = spectral_index_map(new_im, bigim, new_header, bigheader)

make_image(desim)

# need to update header file to match data changes
