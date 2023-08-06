#!/usr/bin/env ipython
# -*- coding: utf-8 -*-
# File name: read_hip.py
"""
Created on Wed Nov  3 09:35:24 2021

@author: Neo(niu.liu@nju.edu.cn)

This code is used to load the Hipparcos catalog (ESA 1997) and extract data 
for some specific sources
"""

import numpy as np

from astropy.table import Table, Column
from astropy import units as u
# from astropy.coordinates import SkyCoord

# My modules
from get_dir import get_data_dir

__all__ = []


# -----------------------------  FUNCTIONS -----------------------------
def get_hip_dir():
    """Return the directory where the Hipparcos data are stored.

    """

    cat_dir = get_data_dir()
    hip_dir = "{:s}/hipparcos".format(cat_dir)

    return hip_dir


def read_hip_main():
    """Load the Hipparcos main catalog

    """

    hip_dir = get_hip_dir()
    hip_main_file = "{:s}/I_239_hip_main.dat.fits".format(hip_dir)
    hip_main_table = Table.read(hip_main_file)

    return hip_main_table


def read_tyc_main():
    """Load the Tycho main catalog
BUGs
Traceback (most recent call last):
  File "/Users/Neo/Github/catalog/read_hip.py", line 64, in <module>
    read_tyc_main()
  File "/Users/Neo/Github/catalog/read_hip.py", line 56, in read_tyc_main
    tyc_main_table = Table.read(tyc_main_file)
  File "/Users/Neo/scisoft/opt64/lib/python3.9/site-packages/astropy/table/connect.py", line 61, in __call__
    out = registry.read(cls, *args, **kwargs)
  File "/Users/Neo/scisoft/opt64/lib/python3.9/site-packages/astropy/io/registry.py", line 527, in read
    data = reader(*args, **kwargs)
  File "/Users/Neo/scisoft/opt64/lib/python3.9/site-packages/astropy/io/fits/connect.py", line 227, in read_table_fits
    return read_table_fits(hdulist, hdu=hdu,
  File "/Users/Neo/scisoft/opt64/lib/python3.9/site-packages/astropy/io/fits/connect.py", line 234, in read_table_fits
    data = table.data
  File "/Users/Neo/scisoft/opt64/lib/python3.9/site-packages/astropy/utils/decorators.py", line 767, in __get__
    val = self.fget(obj)
  File "/Users/Neo/scisoft/opt64/lib/python3.9/site-packages/astropy/io/fits/hdu/table.py", line 402, in data
    data = self._get_tbdata()
  File "/Users/Neo/scisoft/opt64/lib/python3.9/site-packages/astropy/io/fits/hdu/table.py", line 763, in _get_tbdata
    raise ValueError(f"Duplicate field names: {dup}")
ValueError: Duplicate field names: ['---']
    """

    hip_dir = get_hip_dir()
    tyc_main_file = "{:s}/I_239_tyc_main.dat.fits".format(hip_dir)
    tyc_main_table = Table.read(tyc_main_file)

    return tyc_main_table


def read_hip_dmo():
    """Load the Hipparcos orbital solution

    """

    hip_dir = get_hip_dir()
    hip_dmo_file = "{:s}/I_239_hip_dm_o.dat.gz.fits".format(hip_dir)
    hip_dmo_table = Table.read(hip_dmo_file)

    return hip_main_table


# -------------------------------- MAIN --------------------------------
if __name__ == "__main__":
    read_hip_dmo()
# --------------------------------- END --------------------------------
