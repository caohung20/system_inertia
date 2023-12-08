# File:"G:\system_inertia\09_Test_QH\03_QH_2511\ttt.py", generated on TUE, NOV 28 2023  16:34, PSS(R)E Xplore release 35.03.03
import os
import re
import numpy as np

# Create a NumPy array with NaN values
arr = np.array([1, 2, np.nan, 4, np.nan, 6])

# Create a boolean mask to identify NaN values
mask = ~np.isnan(arr)

# Filter the array to remove NaN values
arr_without_nan = arr[mask]

print(arr_without_nan)