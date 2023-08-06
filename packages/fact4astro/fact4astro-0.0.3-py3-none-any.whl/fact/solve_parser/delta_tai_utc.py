#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name: dat.py
"""
Created on Tue Dec 12 18:05:41 2017

@author: Neo(liuniu@smail.nju.edu.cn)


History
12/06/2018 : Now I use module "astropy.time" to calculate "TAI-UTC"
"""

import numpy as np
from astropy.time import Time
from astropy.table import Table


# My modules
from .get_dir import get_aux_dir


# Mapping table between abbreviation and month
month_asc_2_num = {
    "JAN": 1,
    "FEB": 2,
    "MAR": 3,
    "APR": 4,
    "MAY": 5,
    "JUN": 6,
    "JUL": 7,
    "AUG": 8,
    "SEP": 9,
    "OCT": 10,
    "NOV": 11,
    "DEC": 12
}


# -----------------------------  FUNCTIONS -----------------------------
def delta_tai_utc_calc0(mjd):
    """For a given UTC date (MJD), calculate delta(AT) = TAI-UTC.
    """

    # Dates and Delta(AT)s
    changes = np.array([
        [1960,  1,  1.4178180],
        [1961,  1,  1.4228180],
        [1961,  8,  1.3728180],
        [1962,  1,  1.8458580],
        [1963, 11,  1.9458580],
        [1964,  1,  3.2401300],
        [1964,  4,  3.3401300],
        [1964,  9,  3.4401300],
        [1965,  1,  3.5401300],
        [1965,  3,  3.6401300],
        [1965,  7,  3.7401300],
        [1965,  9,  3.8401300],
        [1966,  1,  4.3131700],
        [1968,  2,  4.2131700],
        [1972,  1, 10.0],
        [1972,  7, 11.0],
        [1973,  1, 12.0],
        [1974,  1, 13.0],
        [1975,  1, 14.0],
        [1976,  1, 15.0],
        [1977,  1, 16.0],
        [1978,  1, 17.0],
        [1979,  1, 18.0],
        [1980,  1, 19.0],
        [1981,  7, 20.0],
        [1982,  7, 21.0],
        [1983,  7, 22.0],
        [1985,  7, 23.0],
        [1988,  1, 24.0],
        [1990,  1, 25.0],
        [1991,  1, 26.0],
        [1992,  7, 27.0],
        [1993,  7, 28.0],
        [1994,  7, 29.0],
        [1996,  1, 30.0],
        [1997,  7, 31.0],
        [1999,  1, 32.0],
        [2006,  1, 33.0],
        [2009,  1, 34.0],
        [2012,  7, 35.0],
        [2015,  7, 36.0],
        [2017,  1, 37.0]
    ])

    year, mon, delta_tai_utc = np.transpose(changes)

    mjds = Time(["%d-%d-1" % (yi, mi)
                 for yi, mi in zip(year, mon)])

    if isinstance(mjd, float) or isinstance(mjd, int):

        index = np.searchsorted(mjds.mjd, mjd)
        if index:
            return delta_tai_utc[index - 1]
        else:
            print("Epoch too early!")

    else:
        delta = []

        for mjdi in mjd:

            index = np.searchsorted(mjds.mjd, mjdi)
            if index:
                delta.append(delta_tai_utc[index - 1])
            else:
                print("Epoch too early for %f!" % mjdi)

        return np.asarray(delta)


def delta_tai_utc_calc(mjd):
    """For a given UTC date (MJD), calculate delta(AT) = TAI-UTC.

    Parameters
    ----------
    mjd : float, or array of float
        Modified Julian date

    Returns
    ----------
    dt : float, or array of float
        TAI-UTC in second
    """

    t = Time(mjd, format="mjd", scale="utc")
    dt = Time(t.tai.iso) - Time(t.utc.iso)

    return dt.sec


def read_ls_table(ls_file=None):
    """Read leap second table
    """

    if ls_file is None:
        data_dir = get_aux_dir()
        ls_file = "{}/ut1ls.dat".format(data_dir)

    map_table = Table.read(ls_file, format="ascii.fixed_width_no_header",
                           names=["jd", "offset", "jd0", "slope"],
                           col_starts=(17, 38, 60, 70),
                           col_ends=(25, 47, 65, 78))

    return map_table


def delta_tai_utc_calc_4_epoch(mjd):
    """For a given UTC date (MJD), calculate delta(AT) = TAI-UTC.


    Parameters
    ----------
    mjd : float, or array of float
        Modified Julian date

    Returns
    ----------
    dt : float, or array of float
        TAI-UTC in second
    """

    # MJD -> JD
    jd = mjd + 2400000.5

    # Get the mapping table
    map_table = read_ls_table()

    # Find the time interval
    if jd < map_table["jd"][0]:
        indx = 0
    elif jd < map_table["jd"][-1]:
        indx = -1
    else:
        for indx in range(len(map_table)):
            if jd < map_table["jd"][indx]:
                break

    # Calculate UTC - TAI
    offset = map_table["offset"][indx]
    jd0 = map_table["jd0"][indx]
    slope = map_table["slope"][indx]
    dt = offset + (mjd - jd0) * slope

    return dt


def delta_tai_utc_calc2(mjd):
    """For a given UTC date (MJD), calculate delta(AT) = TAI-UTC.


    Parameters
    ----------
    mjd : float, or array of float
        Modified Julian date

    Returns
    ----------
    dt : float, or array of float
        TAI-UTC in second
    """

    # MJD -> JD
    jd = mjd + 2400000.5

    # Get the mapping table
    map_table = read_ls_table()

    # Find the time interval
    if jd < map_table["jd"][0]:
        indx = 0
    elif jd > map_table["jd"][-1]:
        indx = -1
    else:
        for indx in range(len(map_table)):
            if jd < map_table["jd"][indx]:
                break

        indx = indx - 1

    # Calculate UTC - TAI
    offset = map_table["offset"][indx]
    jd0 = map_table["jd0"][indx]
    slope = map_table["slope"][indx]
    dt = offset + (mjd - jd0) * slope

    # print(mjd, jd, indx, dt)

    return dt


if __name__ == "__main__":
    pass
# --------------------------------- END --------------------------------
