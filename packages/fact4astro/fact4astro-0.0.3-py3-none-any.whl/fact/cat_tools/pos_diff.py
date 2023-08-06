#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name: pos_diff.py
"""
Created on Fri Sep 21 15:39:02 2018

@author: Neo(liuniu@smail.nju.edu.cn)
"""

from functools import reduce
import sys

from math import hypot
import numpy as np
from astropy.coordinates import SkyCoord
from astropy.table import Table
from astropy.table import join
from astropy.table import Column
from astropy import units as u

# My progs
from .pos_err import error_ellipse_calc


__all__ = ["nor_sep_calc", "calc_coord_oft", "pa_calc",
           "calc_pos_diff", "nor_pm_calc"]


# -----------------------------  FUNCTIONS -----------------------------
def nor_pm_calc(pmra, pmra_err, pmdec, pmdec_err, pm_ra_dec_cor):
    """pm_ra_dec_coralculate the normalized seperation.

    Parameters
    ----------
    pmra/pmdec : proper motion in Right Ascension / Declination
    pmra_err/pmdec_err : formal uncertainty of pmra*cos(Dec)/pmdec
    pm_ra_dec_cor : correlation coeffient between pmra*cos(Dec) and pmdec.

    Returns
    ----------
    X : Normalized proper motion, unit-less.
    """

    # Normalised coordinate difference
    X_a = pmra / pmra_err
    X_d = pmdec / pmdec_err

    # Normalised separation - Mignard's statistics (considering covariance)
    # Now I will use the explict expression
    # Avoid singular
    pm_ra_dec_cor = np.where(pm_ra_dec_cor == -1, -0.99999, pm_ra_dec_cor)
    pm_ra_dec_cor = np.where(pm_ra_dec_cor == 1, 0.99999, pm_ra_dec_cor)
    X2 = (X_a**2 + X_d**2 - 2 * pm_ra_dec_cor *
          X_a * X_d) / (1 - pm_ra_dec_cor**2)
    X = np.sqrt(X2)

    return X


def nor_sep_calc(dRA, dRA_err, dDC, dDC_err, C):
    """Calculate the normalized seperation.

    Parameters
    ----------
    dRA/dDC : Right Ascension / Declination differences in micro-as
    dRA_err/dDC_err : formal uncertainty of dRA*cos(Dec)/dDC in micro-as
    C : correlation coeffient between dRA*cos(Dec) and dDC.

    Returns
    ----------
    ang_sep : angular seperation, in micro-as
    X_a / X_d : normalized coordinate differences in RA / DC, unit-less
    X : Normalized separations, unit-less.
    """

    # Angular seperations
    ang_sep = np.sqrt(dRA**2 + dDC**2)
    # ang_sep = hypot(dRA, dDC) # Only used for scalar

    # Normalised coordinate difference
    X_a = dRA / dRA_err
    X_d = dDC / dDC_err

    # Normalised separation - Mignard's statistics (considering covariance)
#     X = np.zeros_like(X_a)
#
#     for i, (X_ai, X_di, Ci) in enumerate(zip(X_a, X_d, C)):
#         if Ci == -1.:
#             Ci = -0.999
#         if Ci == 1.:
#             Ci = 0.999
#
#         wgt = np.linalg.inv(np.mat([[1, Ci], [Ci, 1]]))
#         Xmat = np.mat([X_ai, X_di])
#         X[i] = np.sqrt(reduce(np.dot, (Xmat, wgt, Xmat.T)))

    # Now I will use the explict expression
    # Avoid singular
    C = np.where(C == -1, -0.99999, C)
    C = np.where(C == 1, 0.99999, C)
    X = np.sqrt((X_a**2 + X_d**2 - 2 * C * X_a * X_d) / (1 - C**2))

    return ang_sep, X_a, X_d, X


def calc_coord_oft(RA1, RA1_err, DC1, DC1_err, Cor1,
                   RA2, RA2_err, DC2, DC2_err, Cor2,
                   arccof=None):
    """Calculate the normalized seperation between VLBI and Gaia positions.


    Parameters
    ----------
    RA / DC : Right Ascension / Declination, degress
    e_RA / e_DC : formal uncertainty of RA * cos(Dec) / DC, mas
    Cor : correlation coeffient between RA and DC.
    arccof : cos(Dec.)

    Note: suffix "G" stands for GaiaDR1 and I for VLBI catalog.

    Returns
    ----------
    ang_sep : angular seperation in micro-as
    X_a / X_d : normalized seperation in RA / DC, unit-less
    X : Normalized separations, unit-less.
    """

    if arccof is None:
        arccof = np.cos(np.deg2rad(DC1))

    # # deg -> uas
    # dRA = (RA1 - RA2) * 3.6e9 * arccof
    # dRA_err = np.sqrt(RA1_err**2 + RA2_err**2)
    # dDC = (DC1 - DC2) * 3.6e9
    # dDC_err = np.sqrt(DC1_err**2 + DC2_err**2)

    # deg -> mas
    dRA = (RA1 - RA2) * 3.6e6 * arccof
    dRA_err = np.sqrt(RA1_err**2 + RA2_err**2)
    dDC = (DC1 - DC2) * 3.6e6
    dDC_err = np.sqrt(DC1_err**2 + DC2_err**2)

    # Correlation coefficient of combined errors
    cov = RA1_err * DC1_err * Cor1 + RA2_err * DC2_err * Cor2
    corf = cov / (dRA_err * dDC_err)

    # Normalised separation
    ang_sep, X_a, X_d, X = nor_sep_calc(dRA, dRA_err,
                                        dDC, dDC_err, corf)

    # return ang_sep, X_a, X_d, X
    return dRA, dDC, dRA_err, dDC_err, cov, ang_sep, X_a, X_d, X


def pa_calc0(dra, ddec, anticw=False):
    """Calculate positional angle from positional offset.

    Ax is used for plot and Ay for output value (positional angle).


    Parametes
    ---------
    dra : ndarray
        positional difference in R.A.(times cos(decl.))
    ddec : ndarray
        positional difference in declination
    anticw : Boolean


    Returns
    -------
    Ax : ndarray
        Angle (in degree) of positional offset vector towards to x-axis anti-clockwisely
    Ay : ndarray
        Angle (in degree) of positional offset vector towards to y-axis anti-clockwisely
    """

    Ax = np.rad2deg(np.arctan2(ddec, dra))  # anti-clockwise
    Ay = np.rad2deg(np.arctan2(dra, ddec))  # anti-clockwise

    if anticw:
        # anticlockwise
        Ax = np.where(Ax < 0, 360 + Ax, Ax)
        Ay = np.where(Ay < 0, -Ay, 360 - Ay)
    else:
        # clockwise
        Ax = np.where(Ax < 0, -Ax, 360 - Ax)
        Ay = np.where(Ay < 0, 360 + Ay, Ay)

    return Ax, Ay


def pa_calc1(dra, ddec, anticw=False):
    """Calculate positional angle from positional offset.

    Ax is used for plot and Ay for output value (positional angle).

    A new implementation.

    Parametes
    ---------
    dra : ndarray
        positional difference in R.A.(times cos(decl.))
    ddec : ndarray
        positional difference in declination
    anticw : Boolean


    Returns
    -------
    Ax : ndarray
        Angle (in degree) of positional offset vector towards to x-axis anti-clockwisely
    Ay : ndarray
        Angle (in degree) of positional offset vector towards to y-axis anti-clockwisely
    """

    if anticw:
        # anticlockwise
        zx = dra + 1j * ddec
        zy = ddec - 1j * dra

        Ax = np.angle(zx, deg=True)
        Ay = np.angle(zy, deg=True)
    else:
        # clockwise
        zx = dra - 1j * ddec
        zy = ddec + 1j * dra

        Ax = np.angle(zx, deg=True)
        Ay = np.angle(zy, deg=True)

    Ax = np.where(Ax < 0, 360 + Ax, Ax)
    Ay = np.where(Ay < 0, 360 + Ay, Ay)

    return Ax, Ay


def pa_calc(dra, ddec):
    """Calculate positional angle from positional offset.

    A new implementation.

    Parametes
    ---------
    dra : ndarray
        positional difference in R.A.(times cos(decl.))
    ddec : ndarray
        positional difference in declination
    anticw : Boolean


    Return
    -------
    PA : ndarray
        Angle (in degree) of positional offset vector towards to y-axis anti-clockwisely
    """

    cen = SkyCoord(0 * u.deg, 0 * u.deg, frame="icrs")
    oft = SkyCoord(dra * u.mas, ddec * u.mas, frame="icrs")

    pa = cen.position_angle(oft)
    pa = pa.to(u.deg)

    return pa.value


def coord_diff_err(dra, ddec, dra_err, ddec_err, cov, rho, phi,
                   eema1, eena1, eepa1, eema2, eena2, eepa2):
    """Calculate formal error for arclength and orientation of position offset vector

    The calaculate formula follows Eq.(1) given in Petrov, Kovalev, Plavin (2020)
    (MNRAS 482, 3023-3031).
    It is quite long and complex and I am not willing to type them here.
    In the code, "a" is represented by "rho", "v" by "1", and "g" by "2".
    """

    # Calculate the uncertainties of arc-length
    tan_ang1 = np.tan(np.deg2rad(eepa1 - phi))**2
    ratio1 = (eema1 / eena1)**2
    tan_ang2 = np.tan(np.deg2rad(eepa2 - phi))**2
    ratio2 = (eema2 / eena2)**2
    sigma_rho2 = (1 + tan_ang1) / (1 + tan_ang1 * ratio1) * eema1**2 + \
        (1 + tan_ang2) / (1 + tan_ang2 * ratio2) * eema2**2
    sigma_rho = np.sqrt(sigma_rho2)

    # Calculate the uncertainty of PA
    term1 = (dra * ddec_err) ** 2
    term2 = (ddec * dra_err) ** 2
    term3 = 2 * dra * ddec * cov
    sigma_phi2 = (term1 + term2 - term3) / rho ** 4
    sigma_phi = np.sqrt(sigma_phi2)

    # radian -> degree
    sigma_phi = np.rad2deg(sigma_phi)

    return sigma_rho, sigma_phi


def calc_pos_diff(table1, table2, sou_name="source_name",
                  label=["1", "2"], ref_err=True):
    """Calculate the positional differences between two catalogs.

    These two catalogs should be stored in the astropy.table.Table object.
    And they should contain the following columns:
        -- "source_name"
        -- "ra", "lon", or "elon"
        -- "dec", "lat", or "elat"
        -- "ra_err", "lon_err", or "elon_err"
        -- "dec_err", "lat_err", or "elat_err"
        -- "ra_dec_corr", "ra_dec_cov" or others alike

    This function is written just for radio source catalogs.

    Parameters
    ----------
    table1/table2 : astropy.table.Table object
        Table of radi source position
    ref_err : Boolean
        Flag to determine if considering the positon uncertainty in the referece
        catalog (cat2) when computing the uncertainty of positional offset.

    Returns
    -------
    com_sou : astropy.table.Table object
        Table of positional difference
    """

    # Table label
    label1, label2 = label

    # Check which coordinate system is used
    if "ra" in table1.colnames:
        lon_str = "ra"
        lat_str = "dec"
    elif "elon" in table1.colnames:
        lon_str = "elon"
        lat_str = "elat"
    elif "lon" in table1.colnames:
        lon_str = "lon"
        lat_str = "lat"
    else:
        print("No recongnized colnames for position. "
              "Plese include one of coordinate names "
              "in your table as 'ra/dec', 'elon/elat', or  'lon/lat'.")
        sys.exit()

    # Keep only position-related columns
    table3 = Table(table1, copy=True)
    table4 = Table(table2, copy=True)

    lonerr_str = "{:s}_err".format(lon_str)
    laterr_str = "{:s}_err".format(lat_str)
    cor_str1 = "{:s}_{:s}_corr".format(lon_str, lat_str)
    cor_str2 = "{:s}_{:s}_cor".format(lon_str, lat_str)
    cov_str = "{:s}_{:s}_cov".format(lon_str, lat_str)

    if cor_str1 in table1.colnames and cor_str1 in table2.colnames:
        table3.keep_columns([sou_name, lon_str, lat_str,
                             lonerr_str, laterr_str, cor_str1])
        table4.keep_columns([sou_name, lon_str, lat_str,
                             lonerr_str, laterr_str, cor_str1])
    elif cor_str2 in table1.colnames and cor_str2 in table2.colnames:
        table3.keep_columns([sou_name, lon_str, lat_str,
                             lonerr_str, laterr_str, cor_str2])
        table4.keep_columns([sou_name, lon_str, lat_str,
                             lonerr_str, laterr_str, cor_str2])
    elif cov_str in table1.colnames and cov_str in table2.colnames:
        table3.keep_columns([sou_name, lon_str, lat_str,
                             lonerr_str, laterr_str, cov_str])
        table4.keep_columns([sou_name, lon_str, lat_str,
                             lonerr_str, laterr_str, cov_str])
    else:
        table3.keep_columns([sou_name, lon_str, lat_str,
                             lonerr_str, laterr_str])
        table4.keep_columns([sou_name, lon_str, lat_str,
                             lonerr_str, laterr_str])

    # Cross-match by the source name
    com_sou = join(table3, table4, keys=sou_name, table_names=label)

    # Cos(decl.)
    arc_fac = np.cos(com_sou["{:s}_{:s}".format(
        lat_str, label2)].to(u.rad).value)
    dra = (com_sou["{:s}_{:s}".format(lon_str, label1)] -
           com_sou["{:s}_{:s}".format(lon_str, label2)]) * arc_fac
    ddec = (com_sou["{:s}_{:s}".format(lat_str, label1)] -
            com_sou["{:s}_{:s}".format(lat_str, label2)])

    ra_err1 = com_sou["{:s}_{:s}".format(lonerr_str, label1)]
    dec_err1 = com_sou["{:s}_{:s}".format(laterr_str, label1)]

    if ref_err:
        ra_err2 = com_sou["{:s}_{:s}".format(lonerr_str, label2)]
        dec_err2 = com_sou["{:s}_{:s}".format(laterr_str, label2)]
    else:
        ra_err2 = np.zeros(len(com_sou))
        dec_err2 = np.zeros(len(com_sou))

    dra_err = np.sqrt(ra_err1**2 + ra_err2**2)
    ddec_err = np.sqrt(dec_err1**2 + dec_err2**2)

    # Correlation coefficient of combined errors
    # When correlation coefficients are provided
    if cor_str1 in table1.colnames and cor_str1 in table2.colnames:
        ra_dec_cor1 = com_sou["{:s}_{:s}".format(cor_str1, label1)]
        if ref_err:
            ra_dec_cor2 = com_sou["{:s}_{:s}".format(cor_str1, label2)]
        else:
            ra_dec_cor2 = np.zeros(len(com_sou))

        ra_dec_cov1 = ra_err1 * dec_err1 * ra_dec_cor1
        ra_dec_cov2 = ra_err2 * dec_err2 * ra_dec_cor2
        cov = ra_dec_cov1 + ra_dec_cov2
        corf = cov / (dra_err * ddec_err)

        com_sou.remove_columns(
            ["{:s}_{:s}".format(cor_str1, label1), "{:s}_{:s}".format(cor_str1, label2)])

    elif cor_str2 in table1.colnames and cor_str2 in table2.colnames:
        ra_dec_cor1 = com_sou["{:s}_{:s}".format(cor_str2, label1)]
        if ref_err:
            ra_dec_cor2 = com_sou["{:s}_{:s}".format(cor_str2, label2)]
        else:
            ra_dec_cor2 = np.zeros(len(com_sou))

        ra_dec_cov1 = ra_err1 * dec_err1 * ra_dec_cor1
        ra_dec_cov2 = ra_err2 * dec_err2 * ra_dec_cor2
        cov = ra_dec_cov1 + ra_dec_cov2
        corf = cov / (dra_err * ddec_err)

        com_sou.remove_columns(
            ["{:s}_{:s}".format(cor_str2, label1), "{:s}_{:s}".format(cor_str2, label2)])

    # When covariances are provided
    elif cov_str in table1.colnames and cov_str in table2.colnames:
        ra_dec_cov1 = com_sou["{:s}_{:s}".format(cov_str, label1)]
        ra_dec_cor1 = ra_dec_cov1 / ra_err1 / dec_err1

        if ref_err:
            ra_dec_cov2 = com_sou["{:s}_{:s}".format(cov_str, label2)]
            ra_dec_cor2 = ra_dec_cov2 / ra_err2 / dec_err2
        else:
            ra_dec_cov2 = np.zeros(len(com_sou))
            ra_dec_cor2 = np.zeros(len(com_sou))

        cov = ra_dec_cov1 + ra_dec_cov2
        corf = cov / (dra_err * ddec_err)

        com_sou.remove_columns(
            ["{:s}_{:s}".format(cov_str, label1), "{:s}_{:s}".format(cov_str, label2)])

    # When no correlation relationship is provided
    else:
        ra_dec_cor1 = np.zeros(len(com_sou))
        ra_dec_cor2 = np.zeros(len(com_sou))
        cov = np.zeros(len(com_sou))
        corf = np.zeros(len(com_sou))

    # Add these columns
    com_sou.add_columns([dra, ddec, dra_err, ddec_err, cov],
                        names=["d{:s}".format(lon_str),
                               "d{:s}".format(lat_str),
                               "d{:s}_err".format(lon_str),
                               "d{:s}_err".format(lat_str),
                               "d{:s}_d{:s}_cov".format(lon_str, lat_str)])

    # Add unit information
    pos_unit = com_sou["{:s}_err_{:s}".format(lon_str, label1)].unit
    com_sou["d{:s}".format(lon_str)].unit = u.deg
    com_sou["d{:s}".format(lat_str)].unit = u.deg
    com_sou["d{:s}".format(lon_str)] = com_sou["d{:s}".format(
        lon_str)].to(pos_unit)
    com_sou["d{:s}".format(lat_str)] = com_sou["d{:s}".format(
        lat_str)].to(pos_unit)

    com_sou["d{:s}_err".format(lon_str)].unit = pos_unit
    com_sou["d{:s}_err".format(lat_str)].unit = pos_unit
    com_sou["d{:s}_d{:s}_cov".format(
        lon_str, lat_str)].unit = pos_unit * pos_unit

    # Normalised separation
    ang_sep, X_a, X_d, X = nor_sep_calc(
        com_sou["d{:s}".format(lon_str)], com_sou["d{:s}_err".format(lon_str)],
        com_sou["d{:s}".format(lat_str)], com_sou["d{:s}_err".format(lat_str)],
        corf)

    # Direction of position offset
    pax, pay = pa_calc1(dra, ddec)
    pa = Column(pay, unit=u.deg)

    # Calculate the parameters of error ellipse
    eema1, eena1, eepa1 = error_ellipse_calc(ra_err1, dec_err1, ra_dec_cor1)
    if ref_err:
        eema2, eena2, eepa2 = error_ellipse_calc(
            ra_err2, dec_err2, ra_dec_cor2)
    else:
        eema2, eena2, eepa2 = 0, 1, 0

    # Calculate uncertainties for rho and PA
    ang_sep_err, pa_err = coord_diff_err(
        com_sou["d{:s}".format(lon_str)], com_sou["d{:s}".format(lon_str)],
        com_sou["d{:s}_err".format(
            lat_str)], com_sou["d{:s}_err".format(lat_str)],
        com_sou["d{:s}_d{:s}_cov".format(lon_str, lat_str)],
        ang_sep, pay, eema1, eena1, eepa1, eema2, eena2, eepa2)

    # Add these columns
    com_sou.add_columns([ang_sep, ang_sep_err, pa, pa_err, X_a, X_d, X],
                        names=["ang_sep", "ang_sep_err", "pa", "pa_err",
                               "nor_{:s}".format(lon_str),
                               "nor_{:s}".format(lat_str), "nor_sep"])

    com_sou["ang_sep"].unit = pos_unit
    com_sou["ang_sep_err"].unit = pos_unit
    com_sou["pa_err"].unit = u.deg
    com_sou["nor_{:s}".format(lon_str)].unit = None
    com_sou["nor_{:s}".format(lat_str)].unit = None
    com_sou["nor_sep"].unit = None

    # Remove some columns
    com_sou.remove_columns(["{:s}_{:s}".format(lon_str, label1),
                            "{:s}_{:s}".format(lat_str, label1), ])

    com_sou.rename_column("{:s}_{:s}".format(lon_str, label2), lon_str)
    com_sou.rename_column("{:s}_{:s}".format(lat_str, label2), lat_str)

    return com_sou


def calc_pm_diff(table1, table2, sou_name="source_name",
                 label=["1", "2"], ref_err=True):
    """Calculate proper motion differences between two catalogs.

    These two catalogs should be stored in the astropy.table.Table object.
    And they should contain the following columns:
        -- "source_name"
        -- "pmra", "pmlon", or "pmelon"
        -- "pmdec", "pmlat", or "pmelat"
        -- "pmra_err", "pmlon_err", or "pmelon_err"
        -- "pmdec_err", "pmlat_err", or "pmelat_err"
        -- "pmra_pmdec_corr", "pmra_pmdec_cov" or others alike

    This function is written just for radio source catalogs.

    Parameters
    ----------
    table1/table2 : astropy.table.Table object
        Table of radi source position
    ref_err : Boolean
        Flag to determine if considering the positon uncertainty in the referece
        catalog (cat2) when computing the uncertainty of positional offset.

    Returns
    -------
    com_sou : astropy.table.Table object
        Table of positional difference
    """

    # Table label
    label1, label2 = label

    # Check which coordinate system is used
    if "pmra" in table1.colnames:
        lon_str = "ra"
        lat_str = "dec"
        pmlon_str = "pmra"
        pmlat_str = "pmdec"
    elif "pmelon" in table1.colnames:
        lon_str = "elon"
        lat_str = "elat"
        pmlon_str = "pmelon"
        pmlat_str = "pmelat"
    elif "pmlon" in table1.colnames:
        lon_str = "lon"
        lat_str = "lat"
        pmlon_str = "pmlon"
        pmlat_str = "pmlat"
    else:
        print("No recongnized colnames for position. "
              "Plese include one of column names "
              "in your table as 'pmra/pmdec', 'pmelon/pmelat', or  'pmlon/pmlat'.")
        sys.exit()

    # Keep only position-related columns
    table3 = Table(table1)
    table4 = Table(table2)

    pmlonerr_str = "{:s}_err".format(pmlon_str)
    pmlaterr_str = "{:s}_err".format(pmlat_str)
    cor_str1 = "{:s}_{:s}_corr".format(pmlon_str, pmlat_str)
    cor_str2 = "{:s}_{:s}_cor".format(pmlon_str, pmlat_str)
    cov_str = "{:s}_{:s}_cov".format(pmlon_str, pmlat_str)

    if cor_str1 in table1.colnames and cor_str1 in table2.colnames:
        table3.keep_columns([sou_name, pmlon_str, pmlat_str,
                            pmlonerr_str, pmlaterr_str, cor_str1])
        table4.keep_columns([sou_name, lon_str, lat_str,
                             pmlon_str, pmlat_str,
                            pmlonerr_str, pmlaterr_str, cor_str1])
    elif cor_str2 in table1.colnames and cor_str2 in table2.colnames:
        table3.keep_columns([sou_name, pmlon_str, pmlat_str,
                            pmlonerr_str, pmlaterr_str, cor_str2])
        table4.keep_columns([sou_name, lon_str, lat_str,
                             pmlon_str, pmlat_str,
                            pmlonerr_str, pmlaterr_str, cor_str2])
    elif cov_str in table1.colnames and cov_str in table2.colnames:
        table3.keep_columns([sou_name, pmlon_str, pmlat_str,
                            pmlonerr_str, pmlaterr_str, cov_str])
        table4.keep_columns([sou_name, lon_str, lat_str,
                             pmlon_str, pmlat_str,
                            pmlonerr_str, pmlaterr_str, cov_str])
    else:
        table3.keep_columns(
            [sou_name, pmlon_str, pmlat_str, pmlonerr_str, pmlaterr_str])
        table4.keep_columns(
            [sou_name, lon_str, lat_str, pmlon_str, pmlat_str, pmlonerr_str, pmlaterr_str])

    # Cross-match by the source name
    com_sou = join(table3, table4, keys=sou_name, table_names=label)

    dra = (com_sou["{:s}_{:s}".format(pmlon_str, label1)] -
           com_sou["{:s}_{:s}".format(pmlon_str, label2)])
    ddec = (com_sou["{:s}_{:s}".format(pmlat_str, label1)] -
            com_sou["{:s}_{:s}".format(pmlat_str, label2)])

    ra_err1 = com_sou["{:s}_err_{:s}".format(pmlon_str, label1)]
    dec_err1 = com_sou["{:s}_err_{:s}".format(pmlat_str, label1)]

    if ref_err:
        ra_err2 = com_sou["{:s}_err_{:s}".format(pmlon_str, label2)]
        dec_err2 = com_sou["{:s}_err_{:s}".format(pmlat_str, label2)]
    else:
        ra_err2 = np.zeros(len(com_sou))
        dec_err2 = np.zeros(len(com_sou))

    dra_err = np.sqrt(ra_err1**2 + ra_err2**2)
    ddec_err = np.sqrt(dec_err1**2 + dec_err2**2)

    # Correlation coefficient of combined errors
    # When correlation coefficients are provided
    if cor_str1 in table1.colnames and cor_str1 in table2.colnames:
        ra_dec_cor1 = com_sou["{:s}_{:s}".format(cor_str1, label1)]
        if ref_err:
            ra_dec_cor2 = com_sou["{:s}_{:s}".format(cor_str1, label2)]
        else:
            ra_dec_cor2 = np.zeros(len(com_sou))

        ra_dec_cov1 = ra_err1 * dec_err1 * ra_dec_cor1
        ra_dec_cov2 = ra_err2 * dec_err2 * ra_dec_cor2
        cov = ra_dec_cov1 + ra_dec_cov2
        corf = cov / (dra_err * ddec_err)

        com_sou.remove_columns(
            ["{:s}_{:s}".format(cor_str1, label1), "{:s}_{:s}".format(cor_str1, label2)])

    elif cor_str2 in table1.colnames and cor_str2 in table2.colnames:
        ra_dec_cor1 = com_sou["{:s}_{:s}".format(cor_str2, label1)]
        if ref_err:
            ra_dec_cor2 = com_sou["{:s}_{:s}".format(cor_str2, label2)]
        else:
            ra_dec_cor2 = np.zeros(len(com_sou))

        ra_dec_cov1 = ra_err1 * dec_err1 * ra_dec_cor1
        ra_dec_cov2 = ra_err2 * dec_err2 * ra_dec_cor2
        cov = ra_dec_cov1 + ra_dec_cov2
        corf = cov / (dra_err * ddec_err)

        com_sou.remove_columns(
            ["{:s}_{:s}".format(cor_str2, label1), "{:s}_{:s}".format(cor_str2, label2)])

    # When covariances are provided
    elif cov_str in table1.colnames and cov_str in table2.colnames:
        ra_dec_cov1 = com_sou["{:s}_{:s}".format(cov_str, label1)]
        ra_dec_cor1 = ra_dec_cov1 / ra_err1 / dec_err1

        if ref_err:
            ra_dec_cov2 = com_sou["{:s}_{:s}".format(cov_str, label2)]
            ra_dec_cor2 = ra_dec_cov2 / ra_err2 / dec_err2
        else:
            ra_dec_cov2 = np.zeros(len(com_sou))
            ra_dec_cor2 = np.zeros(len(com_sou))

        cov = ra_dec_cov1 + ra_dec_cov2
        corf = cov / (dra_err * ddec_err)

        com_sou.remove_columns(
            ["{:s}_{:s}".format(cov_str, label1), "{:s}_{:s}".format(cov_str, label2)])

    # When no correlation relationship is provided
    else:
        ra_dec_cor1 = np.zeros(len(com_sou))
        ra_dec_cor2 = np.zeros(len(com_sou))
        cov = np.zeros(len(com_sou))
        corf = np.zeros(len(com_sou))

    # Add these columns
    com_sou.add_columns([dra, ddec, dra_err, ddec_err, cov],
                        names=["d{:s}".format(pmlon_str),
                               "d{:s}".format(pmlat_str),
                               "d{:s}".format(pmlonerr_str),
                               "d{:s}".format(pmlaterr_str),
                               "d{:s}_d{:s}_cov".format(pmlon_str, pmlat_str)])

    # Add unit information
    pos_unit = com_sou["{:s}_{:s}".format(pmlonerr_str, label1)].unit
    com_sou["d{:s}".format(pmlon_str)].unit = u.mas / u.yr
    com_sou["d{:s}".format(pmlat_str)].unit = u.mas / u.yr
    com_sou["d{:s}".format(pmlon_str)] = com_sou["d{:s}".format(
        pmlon_str)].to(pos_unit)
    com_sou["d{:s}".format(pmlat_str)] = com_sou["d{:s}".format(
        pmlat_str)].to(pos_unit)

    com_sou["d{:s}".format(pmlonerr_str)].unit = pos_unit
    com_sou["d{:s}".format(pmlaterr_str)].unit = pos_unit
    com_sou["d{:s}_d{:s}_cov".format(
        pmlon_str, pmlat_str)].unit = pos_unit * pos_unit

    # Normalised separation
    pm_sep, X_a, X_d, X = nor_sep_calc(
        com_sou["d{:s}".format(pmlon_str)
                ], com_sou["d{:s}".format(pmlonerr_str)],
        com_sou["d{:s}".format(pmlat_str)
                ], com_sou["d{:s}".format(pmlaterr_str)],
        corf)

    # Direction of position offset
    pax, pay = pa_calc1(dra, ddec)
    pa = Column(pay, unit=u.deg)

    # Calculate the parameters of error ellipse
    eema1, eena1, eepa1 = error_ellipse_calc(ra_err1, dec_err1, ra_dec_cor1)
    if ref_err:
        eema2, eena2, eepa2 = error_ellipse_calc(
            ra_err2, dec_err2, ra_dec_cor2)
    else:
        eema2, eena2, eepa2 = 0, 1, 0

    # Calculate uncertainties for rho and PA
    pm_sep_err, pa_err = coord_diff_err(
        com_sou["d{:s}".format(pmlon_str)], com_sou["d{:s}".format(pmlon_str)],
        com_sou["d{:s}".format(pmlaterr_str)
                ], com_sou["d{:s}".format(pmlaterr_str)],
        com_sou["d{:s}_d{:s}_cov".format(pmlon_str, pmlat_str)],
        pm_sep, pay, eema1, eena1, eepa1, eema2, eena2, eepa2)

    # Add these columns
    com_sou.add_columns([pm_sep, pm_sep_err, pa, pa_err, X_a, X_d, X],
                        names=["pm_sep", "pm_sep_err", "pm_pa", "pm_pa_err",
                               "nor_pm_{:s}".format(pmlon_str),
                               "nor_pm_{:s}".format(pmlat_str), "nor_pm_sep"])

    com_sou["pm_sep"].unit = pos_unit
    com_sou["pm_sep_err"].unit = pos_unit
    com_sou["pm_pa_err"].unit = u.deg
    com_sou["nor_pm_{:s}".format(pmlon_str)].unit = None
    com_sou["nor_pm_{:s}".format(pmlat_str)].unit = None
    com_sou["nor_pm_sep"].unit = None

    # Remove some columns
    com_sou.remove_columns(["{:s}_{:s}".format(pmlon_str, label1),
                            "{:s}_{:s}".format(pmlat_str, label1)])

    com_sou.rename_column("{:s}_{:s}".format(pmlon_str, label2), pmlon_str)
    com_sou.rename_column("{:s}_{:s}".format(pmlat_str, label2), pmlat_str)

    return com_sou


def main():
    """Main function.
    """

    print("This code is just a module of functions.")


if __name__ == "__main__":
    main()
# --------------------------------- END --------------------------------
