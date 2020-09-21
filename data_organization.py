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

dir_ = "../02_kepler_time_series_scripts/01_Kepler_KOI/"

values = []
files = []
n_flares = []
for file in glob.glob(dir_+"*.fits"):

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

    cadence = header.get("OBSMODE")
    if cadence == "short cadence":
        x = lc.flux
        median = np.median(x)
        sigma = np.std(x)
        flare_threshold = median + (6*sigma)
        peaks, peak_val = find_peaks(x, height=flare_threshold, distance=30)
        n_flares.append(len(peaks))
    else:
        y = lc.flux
        median = np.median(y)
        sigma = np.std(y)
        flare_threshold = median + (6*sigma)
        peaks, peak_val = find_peaks(y, height=flare_threshold, distance=4)
        n_flares.append(len(peaks))
    lc_raw.close()
    

row0 = [dict(zip(keys, values[0]))]
t = Table(row0, names=keys, masked = True)



for i in range(1, len(values)):
    t.add_row(values[i])

new_column = Column(name='path', data=files)
t.add_column(new_column, 0)

flares = Column(name = "n_flares", data = n_flares)
t.add_column(flares)

t.write("kepler_koi.html", format = "ascii.html", overwrite = True)
