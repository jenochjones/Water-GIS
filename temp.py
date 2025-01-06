# -*- coding: utf-8 -*-
"""
Created on Sun Jan  5 08:18:21 2025

@author: acfar
"""

import ctypes
from ctypes import byref, c_char_p, c_int, c_float, c_double, c_long

# Load the EPANET DLL
epanet = ctypes.WinDLL(r".\epanet22_toolkit\epanet2.dll")

# Example: Define ENopen function
epanet.ENopen.argtypes = [c_char_p, c_char_p, c_char_p]
epanet.ENopen.restype = c_int

# Example: Define ENclose function
epanet.ENclose.argtypes = []
epanet.ENclose.restype = c_int

# Example: Define ENgetversion function
epanet.ENgetversion.argtypes = [ctypes.POINTER(c_int)]
epanet.ENgetversion.restype = c_int


# Define file paths
inp_file = b"example.inp"   # Replace with your input file path
rpt_file = b"example.rpt"   # Replace with your report file path
out_file = b"example.out"   # Replace with your binary output file path

# Open the EPANET project
result = epanet.ENopen(inp_file, rpt_file, out_file)
if result != 0:
    print(f"Error opening project: {result}")
    exit()

# Get EPANET version
version = c_int()
result = epanet.ENgetversion(byref(version))
if result == 0:
    print(f"EPANET Version: {version.value}")
else:
    print(f"Error retrieving version: {result}")

# Close the EPANET project
result = epanet.ENclose()
if result != 0:
    print(f"Error closing project: {result}")

