#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name: eob_comp.py
import time
"""
Created on Wed Feb 27 14:59:41 2019

@author: Neo(liuniu@smail.nju.edu.cn)

Compare the EOP series and calculate the offsets (or differences).

"""

from astropy.table import Table, join, Column
import astropy.units as u
from astropy.units import cds
import numpy as np
import sys
import os
import time


__all__ = {"calc_eop_offset", "save_eop_offset"}


# -----------------------------  FUNCTIONS -----------------------------
def root_sum_square(x, y):
    """Calculate the root-sum-square."""

    return np.sqrt(x**2 + y**2)


def save_eop_offset(eop_oft, oft_file):
    """Save the eop offset series into a text file.

    Parameters
    ----------
    eop_oft : Table object
        eop offset series
    oft_file : string
        name of file to store the data
    """

    # Header
    eop_oft.meta["comments"] = [
        " EOP Offset series",
        " Columns  Units   Meaning",
        "    1     day     Time Tag for polar motion and UT1 (MJD)",
        "    2     day     Time Tag for Nutation (MJD)",
        "    3     uas     offset of X pole coordinate",
        "    4     uas     offset of Y pole coordinate",
        "    5     musec   offset of UT1",
        "    6     musec   offset of LOD",
        "    7     uas     offset of dX of Nutation offsets",
        "    8     uas     offset of dY of Nutation offsets",
        "    9     uas     formal uncertainty for offset of X pole coordinate",
        "   10     uas     formal uncertainty for offset of Y pole coordinate",
        "   11     musec   formal uncertainty for offset of UT1",
        "   12     musec   formal uncertainty for offset of LOD",
        "   13     uas     formal uncertainty for offset of Nutation dX",
        "   14     uas     formal uncertainty for offset of Nutation dY",
        " Created date: %s." % time.strftime("%d/%m/%Y", time.localtime())]

    eop_oft.write(oft_file, format="ascii.fixed_width_no_header",
                  exclude_names=["sess_id"],
                  formats={"epoch_pmr": "%14.6f", "epoch_nut": "%14.6f",
                           "dxp": "%+8.1f", "dyp": "%+8.1f",
                           "dut": "%+8.1f", "dlod": "%+8.3f",
                           "ddX": "%+8.1f", "ddY": "%+8.1f",
                           "dxp_err": "%8.1f", "dyp_err": "%8.1f",
                           "dut_err": "%8.1f", "dlod_err": "%8.3f",
                           "ddX_err": "%8.1f", "ddY_err": "%8.1f"},
                  delimiter="", overwrite=True)


def read_eop_offset(oft_file):
    """Read EOP offset data.

    Parameters
    ----------
    oft_file : string
        EOP offset file

    Returns
    ----------
    eop_oft : astropy.table object
    """

    if not os.path.isfile(oft_file):
        print("Couldn't find the file", oft_file)
        sys.exit()

    eop_oft = Table.read(oft_file, format="ascii",
                         names=["epoch_pmr", "epoch_nut",
                                "dxp", "dyp", "dut", "dlod", "ddX", "ddY",
                                "dxp_err", "dyp_err", "dut_err", "dlod_err",
                                "ddX_err", "ddY_err"])

    # Add unit information
    eop_oft["epoch_pmr"].unit = cds.MJD
    eop_oft["epoch_nut"].unit = cds.MJD

    eop_oft["dxp"].unit = u.uas
    eop_oft["dyp"].unit = u.uas
    eop_oft["dxp_err"].unit = u.uas
    eop_oft["dyp_err"].unit = u.uas

    eop_oft["dut"].unit = u.second / 1e6
    eop_oft["dut_err"].unit = u.second / 1e6
    eop_oft["dut"].unit = u.second / 1e6
    eop_oft["dut_err"].unit = u.second / 1e6

    eop_oft["ddX"].unit = u.uas
    eop_oft["ddY"].unit = u.uas
    eop_oft["ddX_err"].unit = u.uas
    eop_oft["ddY_err"].unit = u.uas

    return eop_oft


def calc_eop_offset(eop1, eop2, oft_file=None, cross_keys="db_name"):
    """Calculate the EOP difference series between two solutions.

    Parameters
    ----------
    eop1, eop2: astropy.table object
        EOP series from two solutions

    Return
    ------
<< << << < HEAD
    eop_oft: astropy.table object
== == == =
    eopoft: astropy.table object
>>>>>> > 5510ed4dba6e91fb143e99d48d59d7c55f9cc037
        EOP difference series
    """

    # Copy the original tables and keep only the EOP information
    eop3 = Table(eop1)
    eop3.keep_columns([cross_keys, "epoch_pmr", "epoch_nut",
                       "xp", "yp", "ut1_utc", "dX", "dY", "lod",
                       "xp_err", "yp_err", "ut1_err", "dX_err", "dY_err",
                       "lod_err"])

    eop4 = Table(eop2)
    eop4.keep_columns([cross_keys,
                       "xp", "yp", "ut1_utc", "dX", "dY", "lod",
                       "xp_err", "yp_err", "ut1_err", "dX_err", "dY_err",
                       "lod_err"])

    # Cross-match between two tables
    eop_com = join(eop3, eop4, keys=cross_keys)

    print("There are %d and %d points in series 1 and series 2, respectively,"
          "between which %d are common."
          % (len(eop1), len(eop2), len(eop_com)))

    # Calculate the offset and the uncertainties
    dxp = eop_com["xp_1"] - eop_com["xp_2"]
    dyp = eop_com["yp_1"] - eop_com["yp_2"]
    dut = eop_com["ut1_utc_1"] - eop_com["ut1_utc_2"]
    ddX = eop_com["dX_1"] - eop_com["dX_2"]
    ddY = eop_com["dY_1"] - eop_com["dY_2"]
    dlod = eop_com["lod_1"] - eop_com["lod_2"]

    dxp_err = root_sum_square(eop_com["xp_err_1"], eop_com["xp_err_2"])
    dyp_err = root_sum_square(eop_com["yp_err_1"], eop_com["yp_err_2"])
    dut_err = root_sum_square(eop_com["ut1_err_1"], eop_com["ut1_err_2"])
    ddX_err = root_sum_square(eop_com["dX_err_1"], eop_com["dX_err_2"])
    ddY_err = root_sum_square(eop_com["dY_err_1"], eop_com["dY_err_2"])
    dlod_err = root_sum_square(eop_com["lod_err_1"], eop_com["lod_err_2"])

    # Convert the unit
    # Time tag
    # from astropy.time import Time
    # t_pmr_mjd = Time(eop_com["epoch_pmr"], format="mjd")
    # t_pmr = Column(t_pmr_mjd.jyear, unit=u.year)
    #
    # t_nut_mjd = Time(eop_com["epoch_nut"], format="mjd")
    # t_nut = Column(t_nut_mjd.jyear, unit=u.year)

    # Polar motion (as -> uas)
    dxp.convert_unit_to(u.uas)
    dxp_err.convert_unit_to(u.uas)
    dyp.convert_unit_to(u.uas)
    dyp_err.convert_unit_to(u.uas)

    # UT1-UTC and lod (s -> us)
    dut.convert_unit_to(u.second / 1e6)
    dut_err.convert_unit_to(u.second / 1e6)
    dlod.convert_unit_to(u.second / 1e6)
    dlod_err.convert_unit_to(u.second / 1e6)

    # Nutation offset (as -> uas)
    ddX.convert_unit_to(u.uas)
    ddX_err.convert_unit_to(u.uas)
    ddY.convert_unit_to(u.uas)
    ddY_err.convert_unit_to(u.uas)

    # Add these columns to the combined table.
    eop_oft = Table([eop_com[cross_keys], eop_com["epoch_pmr"],
                    eop_com["epoch_nut"],
                    dxp, dyp, dut, dlod, ddX, ddY,
                    dxp_err, dyp_err, dut_err, dlod_err, ddX_err, ddY_err],
                    names=[cross_keys, "epoch_pmr", "epoch_nut",
                           "dxp", "dyp", "dut", "dlod", "ddX", "ddY",
                           "dxp_err", "dyp_err", "dut_err", "dlod_err",
                           "ddX_err", "ddY_err"])

    # Save the EOP offset series
    if oft_file is not None:
        print("Save the EOP offset series in", oft_file)
        save_eop_offset(eop_oft, oft_file)

    return eop_oft


if __name__ == "__main__":
    print("Nothing to do!")
# --------------------------------- END --------------------------------
