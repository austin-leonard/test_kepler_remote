import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from astropy.io import fits
import os
import glob
from astropy.table import Table, Column

keys = ["OBJECT", "OBSMODE", "QUARTER", "TEFF", "RADIUS"]
hdu = 0

dir_ = "hdd6tb/02_kepler_time_series_scripts/01_Kepler_KOI/"

values = []
files = []
for file in glob.glob(dir_+"*.fits"):

    header = fits.getheader(file, hdu)
    values.append([header.get(key) for key in keys])
    files.append(file)

row0 = [dict(zip(keys, values[0]))]
t = Table(row0, names=keys)

for i in range(1, len(values)):
    t.add_row(values[i])

new_column = Column(name='path', data=files)
t.add_column(new_column, 0)

print(t.show_in_browser(jsviewer=True))

df = t.to_pandas()

print(df.sort_values(by=["TEFF"], ascending=False))

