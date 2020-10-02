import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from astropy.io import fits
import os
import glob
from astropy.table import Table, Column
import lightkurve as lk
from scipy.signal import find_peaks

keys = ["OBJECT", "OBSMODE", "QUARTER", "RADIUS", "KEPMAG"]
hdu = 0

dir_ = "../02_kepler_time_series_scripts/"

directories = glob.glob(dir_ + "*_Q*/")

values = []
files = []
total_flares = []
flares_above_6_sigma = []

# Loop through each directory and each file in it
#for directory in directories:
for directory in directories:
    for ind,file in enumerate(glob.glob(directory+"*.fits")):
        # Get header contents
        header = fits.getheader(file, hdu)
        values.append([header.get(key) for key in keys])
        files.append(file)   
    
        # Get number of flares and flare times
        lc_raw = fits.open(str(file))
        raw_flux = lc_raw[1].data["PDCSAP_FLUX"]
        time = lc_raw[1].data["TIME"]

        lc = lk.LightCurve(time = time, flux = raw_flux)
        lc = lc.remove_nans().flatten()

        # different cadences require different flare detection windows
        cadence = header.get("OBSMODE")
        if cadence == "short cadence":
            x = lc.flux
            median = np.median(x)
            sigma = np.std(x)
            flare_threshold = median + (3*sigma)
            peaks, peak_val = find_peaks(x, height=flare_threshold, distance=30)
            total_flares.append(len(peaks))
        
            flare_threshold_six_sigma = median + (6*sigma)
            peaks_six, peak_val_six = find_peaks(x, height=flare_threshold_six_sigma, distance=30)
            flares_above_6_sigma.append(len(peaks_six))
        
        else:
            y = lc.flux
            median = np.median(y)
            sigma = np.std(y)
            flare_threshold = median + (3*sigma)
            peaks, peak_val = find_peaks(y, height=flare_threshold, distance=4)
            total_flares.append(len(peaks))
        
            flare_threshold_six_sigma = median + (6*sigma)
            peaks_six, peak_val_six = find_peaks(y, height=flare_threshold_six_sigma, distance=4)
            flares_above_6_sigma.append(len(peaks_six))
    
        lc_raw.close()
        
        print("Finished", ind, "of", len(os.listdir(directory)) "in directory", directory)
    
       
    

# Construct table
row0 = [dict(zip(keys, values[0]))]
t = Table(row0, names=keys, masked = True)

for i in range(1, len(values)):
    t.add_row(values[i])

new_column = Column(name='path', data=files)
t.add_column(new_column, 0)

flares = Column(name = "Total Flares", data = total_flares)
t.add_column(flares)

flares_sixsig = Column(name = "Flares Above Six Sigma", data = flares_above_6_sigma)
t.add_column(flares_sixsig)

# Save table as a file
t.write("kepler_all.html", format = "ascii.html", overwrite = True)
