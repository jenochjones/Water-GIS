# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
from wntr.epanet import io as epanet_io
from wntr.network import io as network_io

open_file_path = r"C:\Users\acfar\Documents\Enoch\EPANET\example-networks\Net1.inp"

inp = epanet_io.InpFile()

project = inp.read(open_file_path)

gis = network_io.to_gis(project)
print('stop')
