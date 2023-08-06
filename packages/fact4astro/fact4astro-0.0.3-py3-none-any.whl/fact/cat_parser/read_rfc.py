#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name: read_rfc.py
"""
Created on Sat May 22 11:06:18 2021

@author: Neo(niu.liu@nju.edu.cn)

Format
# Field    1:1    A1    Category: C (calibrator), N (non-calibrator), U (unreliable coordinates)
# Field    4:11   A8    IVS name (B1950)
# Field   13:22   A10   IAU name (J2000.0)
# Field   25:26   I2    Right ascension: hours
# Field   28:29   I2    Right ascension: minutes
# Field   31:39   F9.6  Right ascension: seconds
# Field   41:43   I3    Declination: degrees
# Field   45:46   I3    Declination: minutes
# Field   48:57   F8.5  Declination: seconds
# Field   58:63   F6.2  Inflated error in right ascension in mas
# Field   65:70   F6.2  Inflated error in declination in mas
# Field   73:78   F6.3  Correlation between right ascension and declination
# Field   80:85   I6    Number of observations used
#
# Field   88:88   A1    Blank or < or - for S-band total flux density integrated over entire map
# Field   89:93   F5.3  S-band total flux density integrated over entire map,  Jy
# Field   95:95   A1    Blank or < or - for S-band unresolved flux density at VLBA baselines, Jy
# Field   96:100  F5.3  S-band unresolved flux density at long VLBA baselines, Jy
#
# Field  103:103  A1    Blank or < or - for C-band total flux density integrated over entire map
# Field  104:108  F5.3  C-band total flux density integrated over entire map,  Jy
# Field  110:110  A1    Blank or < or - for C-band unresolved flux density at VLBA baselines
# Field  111:115  F5.3  C-band unresolved flux density at long VLBA baselines, Jy
#
# Field  118:118  A1    Blank or < or - for X-band total flux density integrated over entire map
# Field  119:123  F5.3  X-band total flux density integrated over entire map,  Jy
# Field  125:125  A1    Blank or < or - for X-band unresolved flux density at VLBA baselines
# Field  126:130  F5.3  X-band unresolved flux density at long VLBA baselines, Jy
#
# Field  133:133  A1    Blank or < or - for U-band total flux density integrated over entire map
# Field  134:138  F5.3  U-band total flux density integrated over entire map,  Jy
# Field  140:140  A1    Blank or < or - for U-band unresolved flux density at VLBA baselines
# Field  141:145  F5.3  U-band unresolved flux density at long VLBA baselines, Jy
#
# Field  148:148  A1    Blank or < or - for K-band total flux density integrated over entire map
# Field  149:153  F5.3  K-band total flux density integrated over entire map,  Jy
# Field  155:155  A1    Blank or < or - for K-band unresolved flux density at VLBA baselines
# Field  156:160  F5.3  K-band unresolved flux density at long VLBA baselines, Jy
#
# Field  163:165  A3    Used Band: S, C, X, U, K or X/S
# Field  168:175  A8    Catalogue name

#
# Missing value: -1.0
# minus in columns 88, 95, 103, 110, 118, 125, 133, 140, 148, 155 means that no data in the following column present
# <     in columns 88, 95, 103, 110, 118, 125, 133, 140, 148, 155 means that the upper limit of the flux density is presented in the following column.

"""

import numpy as np
from astropy.table import Table
from astropy import units as u

# My modules
from .get_dir import get_data_dir


# -----------------------------  MAIN -----------------------------
def read_rfc(rfc_file=None):
    """Read the RFC catalog

    Information about the RFC catalog could be found at
    http://astrogeo.org/rfc/

    Returns
    -------
    rfc: an astropy.Table object
        data in the catalog

    """

    if rfc_file is None:
        data_dir = get_data_dir()
        rfc_file = "{}/rfc/rfc_2021a_cat.txt".format(data_dir)

    rfc = Table.read(rfc_file, format="ascii.fixed_width_no_header",
                     names=["ivs_name", "icrf_name", "category",
                            "ra", "dec", "ra_err", "dec_err", "ra_dec_corr", "used_obs",
                            "S_total_flux_flag", "S_total_flux",
                            "S_unrev_flux_flag", "S_unrev_flux",
                            "C_total_flux_flag", "C_total_flux",
                            "C_unrev_flux_flag", "C_unrev_flux",
                            "X_total_flux_flag", "X_total_flux",
                            "X_unrev_flux_flag", "X_unrev_flux",
                            "U_total_flux_flag", "U_total_flux",
                            "U_unrev_flux_flag", "U_unrev_flux",
                            "K_total_flux_flag", "K_total_flux",
                            "K_unrev_flux_flag", "K_unrev_flux",
                            "used_band", "catalogue_name"],
                     col_starts=[3, 12, 0, 24, 40, 57, 64, 72, 79,
                                 87, 88, 94, 95, 102, 103, 109, 110,
                                 117, 118, 124, 125, 132, 133, 139, 140,
                                 147, 148, 154, 155, 162, 167],
                     col_ends=[11, 22, 1, 39, 57, 63, 70, 78, 85,
                               88, 93, 95, 100, 103, 108, 110, 115,
                               118, 123, 125, 130, 133, 138, 140, 145,
                               148, 153, 155, 160, 165, 175])

    # Position information
    ra_dec_str = Table.read(irfc_file,
                            format="ascii.fixed_width_no_header",
                            names=["ra_dec"], col_starts=[24], col_ends=[57])

    ra_dec = SkyCoord(ra_dec_str["ra_dec"], unit=(u.hourangle, u.deg))
    rfc["ra"] = Column(ra_dec.ra, name="ra")
    rfc["dec"] = Column(ra_dec.dec, name="dec")

    # Add Correction factor to 'ra_err'
    arc_fac = np.cos(np.deg2rad(rfc["dec"]))
    rfc["ra_err"] = rfc["ra_err"] * arc_fac

    # Add unit information
    rfc["ra"].unit = u.deg
    rfc["dec"].unit = u.deg
    rfc["ra_err"].unit = u.mas
    rfc["dec_err"].unit = u.mas

    # Calculate the semi-major axis of error ellipse
    pos_err, pos_err_min, pa = error_ellipse_calc(
        rfc["ra_err"], rfc["dec_err"], rfc["ra_dec_corr"])

    # Add the semi-major axis of error ellipse to the table
    pos_err = Column(pos_err, name="pos_err", unit=u.mas)
    pa = Column(pa, name="eepa", unit=u.deg)
    rfc.add_columns([pos_err, pa], indexes=[9, 9])

    return rfc


# --------------------------------- END --------------------------------
