#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name: read_itrf.py
"""
Created on Thu Jan 25 15:18:36 2018

@author: Neo(liuniu@smail.nju.edu.cn)
"""

from astropy.table import Table
from astropy import units as u
import numpy as np
from numpy import genfromtxt
import os
import sys


__all__ = {"read_itrf", "find_stable_sta"}


# -----------------------------  FUNCTIONS -----------------------------
def read_itrf(datafile):
    '''Retrieve site positions/voelocities from ITRF file.

    Parameters
    ---------
    datafile : string
            path and name of ITRF file.

    Returns
    ---------
    sta : array, string
            Station name
    pvX : array, float
            Position/Velocity of X-component, meter
    pvY : array, float
            Position/Velocity of Y-component, meter
    pvZ : array, float
            Position/Velocity of Z-component, meter
    '''

    sta = []
    pvX = []
    pvY = []
    pvZ = []

    for line in open(datafile, 'r'):
        if line[0] != '$':
            sta.append(line[:12].strip())
            # pvX.append(float(line[12:27]))
            # pvY.append(float(line[27:43]))
            # pvZ.append(float(line[43:58]))

            pvX.append(float(line[12:28]))
            pvY.append(float(line[28:45]))
            pvZ.append(float(line[45:61]))

    sta = np.array(sta)
    pvX = np.array(pvX)
    pvY = np.array(pvY)
    pvZ = np.array(pvZ)

    return sta, pvX, pvY, pvZ


def find_stable_sta(sta, pvX, pvY, pvZ):
    '''Get the position/velocity for stable stations.

    'Stable' here means the stations which position is unique in ITRF.
    '''

    cond = np.ones_like(sta, dtype=bool)

    for i, stai in enumerate(sta):

        if cond[i]:

            ind = np.where(sta == stai)[0]
            if ind.size > 1:
                for j in ind:
                    cond[j] = False

    nsta = sta[cond]
    npvX = pvX[cond]
    npvY = pvY[cond]
    npvZ = pvZ[cond]

    return nsta, npvX, npvY, npvZ


def itrf2014_core_network():
    """Read the table of core network stations of ITRF2014
    """

    table_file = (
        "/Users/Neo/Astronomy/Data/solve/itrf2014/core_network_ITRF2014.txt")

    core_network = Table.read(table_file,
                              format="ascii.fixed_width_no_header",
                              names=["site_id", "domes_nb", "solution",
                                     "technique", "site_name",
                                     "longitude", "latitude"],
                              col_starts=(0, 5, 18, 21, 28, 45, 56),
                              col_ends=(4, 14, 19, 26, 40, 54, 64))

    return core_network


def parse_itrf2014_sit_file(sit_file):
    """
    """

    # empty array to store data
    sou_name = Table.read(sit_file, format="ascii.fixed_width_no_header",
                          names=["sta_name", "Xp", "Yp", "Zp", "ref_epoch"],
                          comment="$$",
                          col_starts=(4, 15, 31, 46, 61),
                          col_ends=(11, 26, 42, 57, 68))


def parse_itrf2014_vel_file(vel_file):
    """
    """

    # empty array to store data
    sou_name = Table.read(vel_file, format="ascii.fixed_width_no_header",
                          names=["sta_name", "Xv", "Yv", "Zv", "ref_epoch"],
                          comment="$$", data_start=1,
                          col_starts=(4, 20, 37, 53, 64),
                          col_ends=(11, 27, 44, 60, 71))


# --------------------------------- MAIN ------------------------------
if __name__ == '__main__':
    print("Nothing to do!")
    pass

# --------------------------------- END -------------------------------
