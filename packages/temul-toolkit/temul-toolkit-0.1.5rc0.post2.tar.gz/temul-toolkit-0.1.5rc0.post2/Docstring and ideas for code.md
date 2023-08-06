# Docstring Example

```
'''
Explanation of function

Parameters
----------

Returns
-------

Examples
--------
'''
```

# To Dos:

1. sort unnecessary files into current correct files - done
2. make sure imports are linking each module
3. create api file that imports everything, or two
    3a. One for everything - done
    3b. One for everything except prismatic -done
4. verify api files import what you want
    4a. just import the no_prismatic api into api with *
5. make checklist for pull requests.
    5a. should you add the function to the api/api_no_prismatic?
    5b. docstring with examples?
    5c. works in site-packages?
6. add fft masking code
    6a. PR on atomap for log plotting of add_atoms_with_gui()
7. For get_masked_ifft(), calibration of units automatically.   
8. Update docstrings
    8a. image stack function example/dummy data
    8b. dummy data for simulate_and_calibrate_with_prismatic()
    8d. Fix docstring for return_xyz_coordinates()
    8f. Fix docstring for convert_numpy_z_coords_to_z_height_string
    8g. Fix docstring for return_z_coordinates()
    8h. Fix docstring for convert_numpy_z_coords_to_z_height_string()
    8j. load_and_compare_images()
9. Add correct warning to load_data_and_sampling()
12. Change save_variables (e.g., crop_image_hs) to np array.
15. Auto toggle refine have a histogram option.
16. remove scalebar_true param, just have a function for it and run it where neccessary (in line profile code too).
17. Remove 'return' from calibrate_intensity_distance_with_sublattice_roi
18. figsize for line profile
19. round sampling to 6 decimal places in Model Refiner setup
20. set the calibration area for model refiner to be a small area automatically.
21. includeThermalEffects for simulation func: simulate_with_prismatic
22. save raw simulation within model refiner
23. Line 1169: Remove print(type(sublattice_intensity))
24. With the atom intensities, loop over the atoms themselves rather than an index of the sublattice. That way if you want to see the calculatd bksub intensities, when you look at sublattice.atom_amplitude_max_intensity you will get the correct values, rather than just the max values. eg. assign atom.amplitude_max_intensity to the value instead. see local background subtraction and how it doesn't store the bksub values in the, it just outputs a list, we want it to store in the atom.
25. Add error function to intensity tools
26. see lin 291 of dark_bright_boracite.py (inoutplane) for calibrating the plot_polarisation_vectors plot.
27. All example data loading should be done via an example_data.py function

# Ideas for code development


Absolutely Need to Develop:

*Update all to newest version of atomap and hyperspy.

gaussian fitting function of multiple histogram regions, with ouput/log: 
    for the fitting of gaussians to 1D intensity plot/histogram;
    each time it fails or suceeds, print out the response. and finally 
    print out a log of the whole fitting procedure.

intensity refine function:
    make cleaner, layout as below, maybe split up if needed/better.

Errors and uncertainties
    define the gaussian fitting error and uncertainty
    define the intensity error and uncertainty
    log the error between images (exp vs. sim)

lorentzian filter for simulation, increase time and frozen Phonons also

max, mean, min for calibrate and other functions that don't have it already.
    

For the image_size_x,y,z have the input as a list of len 3 (x,y,z)
Same for the create cif and xyz data

Similar for the mask radii for intensity refine. Have it on loop, going through
a sublattice for each mask radius. Could have a check to see if they are the 
same length. If not, tell the user that the final mask_radius will be used for
every other sublattice after the last mask radius entered.
In other words: if we have 5 sublattices, and input a list of 3 mask_radius,
we simply use the final mask radius for the last 3 sublattices in the loop! 

For the refine loops, each loop, print out the time taken in minutes. Then at
the end, print out the entire time taken.

Make it easy to have the mpl plots saved or not. Just save the data should be 
an option. It's easy to plot the mpl or hs plots after in a loop!

Position Refine;
get prismatic sampling edit
open a pandas df for tracking changes
create xyz file for sublattices given

create loop
    set up simulation
    do simulation
    load simulation
    calibrate simulation

    all of the above done in the simulate_with_prismatic function

    filter simulation
    save calibrated and filtered simulation

    

counter before refinement
image diff position to create new sublattice
    plot new sub
    assign elements and Z height
    save new sub

counter after refinement
compare sublattice
    dont think I need to compare counters for image diff position? 
    IT counts the number of elements before a new sublattice is added. It isn't 
    going to the same if a new sublattice is added, and it is going to return 
    sub_new=None anyway and break...

    logging the counts before the first and after each iteration is good 
    though, because we can save the evolution of the refinement in a pandas 
    csv file.


create new xyz file for next iteration
save counts as a csv file
create a new folder in which to place all of this refinement.
    make sure the filename isn't overlapping with another tag in your folder,
    otherwise those files would also be moved.
move the xyz files in 


Add functions to polarisation.py for domain wall mapping.
> centre_colormap for the LNO domain and any diverging, see if it's useful.



# Order to upload to atomap

max min mean total with tests



# Dependencies:

from atomap.atom_finding_refining import _make_circular_mask
from matplotlib import gridspec
import rigidregistration
from tifffile import imread, imwrite, TiffWriter
from collections import Counter
import warnings
from time import time
from pyprismatic.fileio import readMRC
import pyprismatic as pr
from glob import glob
from atomap.atom_finding_refining import normalize_signal
from atomap.tools import remove_atoms_from_image_using_2d_gaussian
import os
from skimage.measure import compare_ssim as ssm
from atomap.atom_finding_refining import get_atom_positions_in_difference_image
from scipy.ndimage.filters import gaussian_filter
import collections
from atomap.atom_finding_refining import subtract_average_background
from numpy import mean
import matplotlib.pyplot as plt
import hyperspy.api as hs
import atomap.api as am
import numpy as np
from numpy import log
import CifFile
import pandas as pd
import scipy
import periodictable as pt
import matplotlib
