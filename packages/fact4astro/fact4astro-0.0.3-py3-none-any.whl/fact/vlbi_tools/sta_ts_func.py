#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name: sta_ts_func.py
"""
Created on Sat May  1 11:28:22 2021

@author: Neo(niu.liu@nju.edu.cn)

Tools dealing with the station coordinate time-series available at
http://ivsopar.obspm.fr/stations/index.php.
"""

import os
import sys

import numpy as np

from astropy.table import Table, Column
from astropy.time import Time
import astropy.units as u

# My mudoles
from .get_dir import get_vlbi_sol_dir


# -----------------------------  FUNCTIONS -----------------------------
def sta_ts_dir():
    """
    Return the default directory of station coordinate time series
    """

    sol_dir = get_vlbi_sol_dir()
    data_dir = "{:s}/opa/ts-sta".format(sol_dir)

    return data_dir


def read_sta_ts(sta_file):
    """Retrieve station coordinate time series.

    Parameters
    ----------
    sta_file : string
        name of data file

    Returns
    ----------
    sta_ts : astropy.table object
     |__
        sta_name : string
            name of station
        xp : array, float
            X component of position
        yp : array, float
            Y component of position
        zp : array, float
            Z component of position
        xp_err : array, float
            formal uncertainty of X component
        yp_err : array, float
            formal uncertainty of Y component
        zp_err : array, float
            formal uncertainty of Z component
        up : array, float
            U component
        ep : array, float
            E component
        np : array, float
            N component
        up_err : array, float
            formal uncertainty of U component
        ep_err : array, float
            formal uncertainty of E component
        np_err : array, float
            formal uncertainty of N component
        sess_name : string
            session name
        epoch : float
            epoch in Julian year
    """

    # Check if the input file exists
    if not os.path.exists(sta_file):
        print("Couldn't find the input file", sta_file)
        sys.exit()

    sta_ts = Table.read(sta_file,
                        format="ascii.fixed_width_no_header",
                        names=["sta_name",
                               "xp", "xp_err", "yp", "yp_err", "zp", "zp_err",
                               "up", "up_err", "ep", "ep_err", "np", "np_err",
                               "sess_name", "epoch"],
                        col_starts=[137, 13, 27, 38, 52, 64, 77,
                                    86, 96, 103, 113, 120, 130, 147, 0],
                        col_ends=[146, 26, 35, 51, 60, 76, 85,
                                  95, 102, 112, 119, 129, 136, 157, 10])

    # Add information for units
    sta_ts["xp"].unit = u.m / 1000
    sta_ts["yp"].unit = u.m / 1000
    sta_ts["zp"].unit = u.m / 1000
    sta_ts["xp_err"].unit = u.m / 1000
    sta_ts["yp_err"].unit = u.m / 1000
    sta_ts["zp_err"].unit = u.m / 1000
    sta_ts["up"].unit = u.m / 1000
    sta_ts["ep"].unit = u.m / 1000
    sta_ts["np"].unit = u.m / 1000
    sta_ts["up_err"].unit = u.m / 1000
    sta_ts["ep_err"].unit = u.m / 1000
    sta_ts["np_err"].unit = u.m / 1000
    sta_ts["epoch"].unit = u.yr

    return sta_ts


# def get_sou_ts(sou_name, data_dir=None):
#     """Read radio source coordinate time-series data
#
#     Parameters
#     ----------
#     sou_name: string
#         source name of IERS designation or file name with the data
#     data_dir: string
#         directory to store the data file
#
#     Returns
#     -------
#     coordts : astropy.table.Table object
#         coordinate time series
#     """
#
#     if not data_dir:
#         data_dir = sta_ts_dir()
#
#     data_file = "{}.dat".format(sou_name)
#     coordts = read_ts(data_file, data_dir)
#
#     return coordts
#
#
# def ts_stat(coordts):
#     """Simple statistics of coordinate time-series
#
#     Parameter
#     ---------
#     sou_name: string
#         source name of IERS designation or file name with the data
#     """
#
#     stat = {}
#
#     # Number of used sessions
#     numses = len(coordts)
#     stat["used_ses"] = numses
#
#     # Number of used observations
#     numobs = np.sum(coordts["used_obs"])
#     stat["used_obs"] = numobs
#
#     #### TO-DO ####
#     # MAYBE PRINT THESE STATISTICS
#     #### TO-DO ####
#
#
# def sou_ts_stat(sou_name):
#     """Simple statistics of coordinate time-series
#
#     Parameter
#     ---------
#     sou_name: string
#         source name
#     """
#
#     coordts = get_sou_ts(sou_name)
#
#     ts_stat(coordts)
#
#     # NOT CLEAR YET ABOUT WHAT TO DO NEXT
#
#
# def get_icrf3_pos(sou_name, wv="sx"):
#     """Get radio source position from the ICRF3 catalog
#
#     Parameters
#     ----------
#     sou_name: string
#         source name
#     wv: str,
#         wavelength, SX, K, or XKa
#
#     Returns
#     -------
#     pos : a dict object
#         key: "ra", "dec"
#         value: ra, dec in degree
#     """
#
#     icrf3 = read_icrf3(wv=wv)
#
#     # Find the source position
#     mask = (icrf3["iers_name"] == sou_name)
#     sou = icrf3[mask]
#
#     if len(sou):
#         ra = sou["ra"][0]
#         dec = sou["dec"][0]
#
#         if sou["type"][0] == "C":
#             sou_type = "C"
#         else:
#             sou_type = "O"
#
#     else:
#         print("There is no entry for {} in ICRF3 catalog,".format(sou_name),
#               "use the mean position instead.")
#         return False
#
#     pos = {"ra": ra, "dec": dec, "type": sou_type}
#
#     return pos
#
#
# def calc_ts_oft(sou_name, coordts):
#     """Calculate the time series offset wrt. ICRF3 position
#
#     Parameters
#     ----------
#     sou_name: string
#         source name
#     coordts : astropy.table.Table object
#         coordinate time series
#
#     Return
#     ------
#     dpos : a dict object
#         key: "dra", "ddec", "rho", "pa"
#         value: dra, ddec, rho in mas
#                pa in deg
#     """
#
#     pos = get_icrf3_pos(sou_name)
#
#     if pos:
#         ra0 = pos["ra"]
#         dec0 = pos["dec"]
#         sou_type = pos["type"]
#     else:
#         ra0 = np.mean(coordts["ra"])
#         dec0 = np.mean(coordts["dec"])
#         sou_type = "N"
#
#     dra = coordts["ra"] - ra0
#     ddec = coordts["dec"] - dec0
#
#     dra.unit = u.deg
#     ddec.unit = u.deg
#     dra.convert_unit_to(u.mas)
#     ddec.convert_unit_to(u.mas)
#
#     rho = np.sqrt(dra**2 + ddec**2)
# #     pax, pay = pa_calc(np.array(dra), np.array(ddec))
#     pa = pa_calc(np.array(dra), np.array(ddec))
#
#     dpos = {"dra": dra, "ddec": ddec, "rho": rho, "pa": pa, "type": sou_type}
#
#     return dpos
#
#
# def get_ts(sou_name, data_dir=None, calc_oft=False):
#     """get the time series offset wrt. ICRF3 position
#
#     Parameters
#     ----------
#     sou_name: string
#         source name
#
#     Return
#     ------
#     dpos : a dict object
#         key: "dra", "ddec"
#         value: dra, ddec in mas
#     """
#
#     if not data_dir:
#         data_dir = sta_ts_dir()
#
#     coordts = get_sou_ts(sou_name, data_dir)
#
#     if calc_oft:
#         dpos = calc_ts_oft(sou_name, coordts)
#         dra = dpos["dra"]
#         ddec = dpos["ddec"]
#         rho = dpos["rho"]
#         pa = dpos["pa"]
#
#         # Check the source type in the ICRF3 S/X catalog
#         type_list = [dpos["type"]] * len(coordts)
#         sou_type = Column(type_list, name="type")
#
#         coordts.add_columns([dra, ddec, rho, pa, sou_type], names=[
#                             "dra", "ddec", "rho", "pa", "type"])
#
#     return coordts


# ----------------------------- MAIN -----------------------------------
if __name__ == "__main__":
    pass
# ------------------------------ END -----------------------------------
