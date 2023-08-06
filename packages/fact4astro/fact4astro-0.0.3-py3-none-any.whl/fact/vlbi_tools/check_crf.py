#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name: comp_cat.py
"""
Created on Fri Mar 22 15:58:02 2019

@author: Neo(liuniu@smail.nju.edu.cn)
"""

from functools import reduce
import time
import sys


import numpy as np
from numpy import cos, sqrt
from astropy.table import Table, join, Column
import astropy.units as u
from astropy.coordinates import Angle
from astropy.time import Time

from my_progs.catalog import (read_icrf, read_gaia, pos_err, pos_diff,
                              vsh_fit, vsh_output, iers_trans)


# -----------------------------  FUNCTIONS -----------------------------
def root_sum_square(x, y):
    """Calculate the root-sum-square."""

    return np.sqrt(x**2 + y**2)


def nor_sep_calc(dRA, dRA_err, dDC, dDC_err, C):
    '''Calculate the normalized seperation.

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
    '''

    # Angular seperations
    ang_sep = sqrt(dRA**2 + dDC**2)

    # Normalised coordinate difference
    X_a = dRA / dRA_err
    X_d = dDC / dDC_err

    # Normalised separation - Mignard's statistics (considering covariance)
    X = np.zeros_like(X_a)

    for i, (X_ai, X_di, Ci) in enumerate(zip(X_a, X_d, C)):
        if Ci == -1.:
            Ci = -0.99
        if Ci == 1.0:
            Ci = 0.99
        # print(Ci)

        wgt = np.linalg.inv(np.mat([[1, Ci],
                                    [Ci, 1]]))
        Xmat = np.mat([X_ai, X_di])
        X[i] = sqrt(reduce(np.dot, (Xmat, wgt, Xmat.T)))

    return ang_sep, X_a, X_d, X


def boxplot_stats(data):
    """Return five boxplot statistics
    """

    median = np.median(data)
    upper_quartile = np.percentile(data, 75)
    lower_quartile = np.percentile(data, 25)

    iqr = upper_quartile - lower_quartile
    upper_whisker = data[data <= upper_quartile+1.5*iqr].max()
    lower_whisker = data[data >= lower_quartile-1.5*iqr].min()

    return lower_whisker, lower_quartile, median, upper_quartile, upper_whisker


def check_cat_col(t_cat):
    """Check if all necessary column names exist.

    Parameter
    ---------
    t_cat : any objects like Astropy.table.Table object
        CRF datum

    Return None
    """

    # Check if the source name (IERS/IVS/ICRF designation) is given
    sou_names = ["iers_name", "ivs_name", "icrf_name"]

    flag_sou_name = False
    for sou_name in sou_names:
        if sou_name in t_cat.colnames:
            flag_sou_name = True
            break

    if flag_sou_name:
        pass
    else:
        print("Could not find the source name.")
        sys.exit(1)

    # Check if all data columns exist
    dat_names = ["ra", "dec", "ra_err", "dec_err", "ra_dec_corr",
                 "num_obs", "num_ses", "beg_epoch", "end_epoch", "mean_epoch"]

    for dat_name in dat_names:
        if dat_name not in t_cat.colnames:
            print("Column name {} does not exist.".format(dat_name))
            sys.exit(1)


def print_obs_stats(t_cat):
    """Print statistics for observations.

    Parameter
    ---------
    t_cat : any objects like Astropy.table.Table object
        CRF datum

    Return None
    """

    # Observing history
    print("=============== Statistics for observations ===============")
    first_epoch = t_cat["beg_epoch"][t_cat["beg_epoch"] != 0].min()
    last_epoch = t_cat["end_epoch"].max()

    # MJD -> Julian year
    first_epoch = Time(first_epoch, format="mjd").to_value("jyear")
    last_epoch = Time(last_epoch, format="mjd").to_value("jyear")
    mean_epoch = Time(t_cat["mean_epoch"], format="mjd").to_value("jyear")

    print("Observing period: {:.2f}-{:.2f}, spanning {:.2f} year.".format(
        first_epoch, last_epoch, last_epoch-first_epoch))
    print("Median mean epoch for a given source: {:.2f}.".format(
        np.median(mean_epoch)))
    print("Median Nb delays used: {:.0f}.".format(
        np.median(t_cat["num_obs"])))
    print("Median Nb sessions used: {:.0f}.".format(
        np.median(t_cat["num_ses"])))
    print("===========================================================\n\n")


def print_err_stats(t_cat):
    """Print statistics for positional uncertainty.

    Parameter
    ---------
    t_cat : any objects like Astropy.table.Table object
        CRF datum

    Return None
    """
    # Positional uncertainty
    print("========== Statistics for positional uncertainty ==========")
    print("Nb. Sources: {}".format(len(t_cat)))

    pos_err_max = pos_err.pos_err_calc(
        t_cat["ra_err"], t_cat["dec_err"], t_cat["ra_dec_corr"])
    print("-----------------------------------------------------------")
    print("                  Min       Q1       Q2       Q3      Max")
    print("R.A.*cos(dec)  {:7.3f}  {:7.3f}  {:7.3f}  {:7.3f}  {:7.3f}".format(
        *boxplot_stats(t_cat["ra_err"])))
    print("Decl.          {:7.3f}  {:7.3f}  {:7.3f}  {:7.3f}  {:7.3f}".format(
        *boxplot_stats(t_cat["dec_err"])))
    print("EEMA           {:7.3f}  {:7.3f}  {:7.3f}  {:7.3f}  {:7.3f}".format(
        *boxplot_stats(t_cat["pos_err"])))
    print("-----------------------------------------------------------")
    print("Note: EEMA stands for the semi-major axis of error ellipse.\n"
          "      Statistics are given by the boxplot.\n"
          "      Unit: {}.".format(t_cat["ra_err"].unit))
    print("===========================================================\n\n")


def print_oft_wrt_apriori(t_cat, ref_cat="ICRF3 SX", trans_mod="VSH01"):
    """Check VLBI radio catalog wrt. a priori catalog

    Parameters
    ----------
    t_cat : Astropy.table.Table object
        Astrometric information from radio catalog
    ref_cat : str
        Name of a priori catalog
    trans_mod : str
        Name of transformation model

    Returns
    -------
    None
    """

    # Convert into upper case
    ref_cat_upper = ref_cat.upper()
    trans_mod_upper = trans_mod.upper()

    if ref_cat_upper in ["ICRF3 SX"]:
        ref_cat_name = "ICRF3 S/X (Charlot et al. 2020)"
        ref_cat_data = read_icrf.read_icrf3(wv="sx")
    elif ref_cat_upper in ["ICRF3 K"]:
        ref_cat_name = "ICRF3 K (Charlot et al. 2020)"
        ref_cat_data = read_icrf.read_icrf3(wv="k")
    elif ref_cat_upper in ["ICRF3 XKA"]:
        ref_cat_name = "ICRF3 X/Ka (Charlot et al. 2020)"
        ref_cat_data = read_icrf.read_icrf3(wv="xka")
    elif ref_cat_upper in ["ICRF2"]:
        ref_cat_name = "ICRF2 (Fey et al. 2015)"
        ref_cat_data = read_icrf.read_icrf2()
    elif ref_cat_upper in ["ICRF", "ICRF1"]:
        ref_cat_name = "ICRF (Ma et al. 1998)"
        ref_cat_data = read_icrf.read_icrf1()
    # elif ref_cat_upper in ["rfc", "RFC"]:
        # ref_cat_name = "RFC"
    # OPA, and other IVS catalog
    elif ref_cat_upper in ["GAIA DR1"]:
        ref_cat_name = "Gaia DR1 Quasar Auxilliary solution (Mignard et al. 2016)"
        ref_cat_data = read_gaia.read_dr1_qso()
    elif ref_cat_upper in ["GAIA DR2"]:
        ref_cat_name = "Gaia DR2 ICRF3-prototype subset (Gaia Collaboration et al. 2018)"
        ref_cat_data = read_gaia.read_dr2_iers()
    elif ref_cat_upper in ["GAIA", "GAIA EDR3"]:
        ref_cat_name = "Gaia EDR3 ICRF3 source (Gaia Collaboration et al. 2021)"
        ref_cat_data = read_gaia.read_edr3_icrf_sou()
    else:
        print("ref_cat can only be one of the following:")
        print("'ICRF3 SX', 'ICRF3 K', 'ICRF3 XKA', 'ICRF2', 'ICRF', 'ICRF1', "
              "'Gaia', 'Gaia DR1', 'Gaia DR2', 'Gaia EDR3' (case insensitive).")

    if trans_mod_upper in ["VSH01", "VSH"]:
        trans_mod_name = "First degree of vector spherical harmonics"
        trans_mod_func = vsh_fit.vsh_fit_4_table_deg01
        print_pmt_func = vsh_output.print_vsh_result_4_dict
    elif trans_mod_upper in ["VSH02"]:
        trans_mod_name = "First two degrees of vector spherical harmonics"
        trans_mod_func = vsh_fit.vsh_fit_4_table_deg02
        print_pmt_func = vsh_output.print_vsh_result_4_dict
    elif trans_mod_upper in ["IERS-1"]:
        trans_mod_name = "IERS-1995 model (pure rotation)"
        trans_mod_func = iers_trans.iers_tran_fit_4_table1
        print_pmt_func = iers_trans.print_iers1995_result_4_dict
    elif trans_mod_upper in ["IERS-2"]:
        trans_mod_name = "IERS-1995 model (pure rotation + declination bias)"
        trans_mod_func = iers_trans.iers_tran_fit_4_table2
        print_pmt_func = iers_trans.print_iers1995_result_4_dict
    elif trans_mod_upper in ["IERS-3"]:
        trans_mod_name = "IERS-1995 model (pure rotation + declination bias + linear drift)"
        trans_mod_func = iers_trans.iers_tran_fit_4_table3
        print_pmt_func = iers_trans.print_iers1995_result_4_dict
    else:
        print("trans_mod can only be one of the following:")
        print("'VSH01', 'VSH02', 'VSH'.")

    # Calculate positional offset
    t_oft = pos_diff.radio_cat_diff_calc(
        t_cat, ref_cat_data, sou_name="iers_name")

    print("========== Comparison with the reference catalog ==========")
    print("Ref. catalog:", ref_cat_name)
    print("Nb Common source:", len(t_oft))
    print("\nPositional offset wrt. the reference catalog")
    print("-----------------------------------------------------------")
    print("                  Min       Q1       Q2       Q3      Max")
    print("R.A.*cos(dec)  {:7.3f}  {:7.3f}  {:7.3f}  {:7.3f}  {:7.3f}".format(
        *boxplot_stats(t_oft["dra_err"])))
    print("Decl.          {:7.3f}  {:7.3f}  {:7.3f}  {:7.3f}  {:7.3f}".format(
        *boxplot_stats(t_oft["ddec_err"])))
    print("rho            {:7.3f}  {:7.3f}  {:7.3f}  {:7.3f}  {:7.3f}".format(
        *boxplot_stats(t_oft["ang_sep"])))
    print("X_ra           {:7.3f}  {:7.3f}  {:7.3f}  {:7.3f}  {:7.3f}".format(
        *boxplot_stats(t_oft["nor_ra"])))
    print("X_dec          {:7.3f}  {:7.3f}  {:7.3f}  {:7.3f}  {:7.3f}".format(
        *boxplot_stats(t_oft["nor_dec"])))
    print("X              {:7.3f}  {:7.3f}  {:7.3f}  {:7.3f}  {:7.3f}".format(
        *boxplot_stats(t_oft["nor_sep"])))
    print("-----------------------------------------------------------")

    print("\nGlobal difference wrt. the reference catalog")
    print("Transformation model:", trans_mod_name)
    # print("Transformation parameters:")
    output = trans_mod_func(t_oft)

    # mas -> uas
    output["pmt"] = output["pmt"] * 1000
    output["sig"] = output["sig"] * 1000
    print_pmt_func(output)
    print("===========================================================\n\n")


def calc_cat_offset(t_cat1,  t_cat2, souname="iers_name"):
    """Calculate the radio source position differences between two catalogs.



    Parameters
    ----------
    t_cat1, t_cat2: astropy.table object
        radio source positions from two catalogs

    Return
    ------
    t_cat_oft: astropy.table object
        radio source position differences
    """

    # Copy the original tables and keep only the source position information.
    t_cat3 = Table(t_cat1)
    t_cat3.keep_columns([souname, "ra",
                         "dec", "ra_err", "dec_err", "ra_dec_corr",
                         "used_sess", "used_obs"])

    t_cat4 = Table(t_cat2)
    t_cat4.keep_columns([souname, "ra", "dec",
                         "ra_err", "dec_err", "ra_dec_corr"])

    # Cross-match between two tables
    soucom = join(t_cat3, t_cat4, keys=souname)

    print("There are %d and %d sources in two catalogs, respectively,"
          "between which %d are common."
          % (len(t_cat1), len(t_cat2), len(soucom)))

    # Calculate the offset and the uncertainties
    arcfac = cos(Angle(soucom["dec_1"]).radian)
    dra = (soucom["ra_1"] - soucom["ra_2"]) * arcfac

    ddec = soucom["dec_1"] - soucom["dec_2"]
    dra_err = root_sum_square(soucom["ra_err_1"], soucom["ra_err_2"])
    ddec_err = root_sum_square(soucom["dec_err_1"], soucom["dec_err_2"])

    dra_ddec_cov = soucom["ra_err_1"] * soucom["dec_err_1"] * soucom["ra_dec_corr_1"] + \
        soucom["ra_err_2"] * soucom["dec_err_2"] * soucom["ra_dec_corr_2"]

    dra_ddec_corr = dra_ddec_cov / \
        root_sum_square(soucom["ra_err_1"], soucom["dec_err_1"]) / \
        root_sum_square(soucom["ra_err_2"], soucom["dec_err_2"])

    # Convert the unit
    dra.convert_unit_to(u.uas)
    dra_err.convert_unit_to(u.uas)
    ddec.convert_unit_to(u.uas)
    ddec_err.convert_unit_to(u.uas)
    dra_ddec_corr.unit = None
    dra_ddec_cov.unit = u.mas * u.mas
    dra_ddec_cov.convert_unit_to(u.uas * u.uas)

    # Calculate the angular seperation
    ang_sep, X_a, X_d, X = nor_sep_calc(
        dra, dra_err, ddec, ddec_err, dra_ddec_corr)

    # sou_nb = len(soucom)
    ang_sep = Column(ang_sep, unit=u.uas)
    X_a = Column(X_a)
    X_d = Column(X_d)
    X = Column(X)

    # Add these columns to the combined table.
    t_cat_oft = Table([soucom[souname],
                       soucom["ra_1"], soucom["dec_1"],
                       dra, dra_err, ddec, ddec_err,
                       dra_ddec_cov, dra_ddec_corr,
                       ang_sep, X, X_a, X_d],
                      names=["ivs_name", "ra", "dec",
                             "dra", "dra_err", "ddec", "ddec_err",
                             "dra_ddec_cov", "dra_ddec_corr",
                             "ang_sep", "nor_sep",
                             "nor_sep_ra", "nor_sep_dec"])

    return t_cat_oft


def check_crf(t_cat, ref_cat="ICRF3 SX", trans_mod="VSH01"):
    """A quick check of the VLBI radio source catalog.
    """

    # Check if all necessary columns available
    check_cat_col(t_cat)

    # Statistics of the VLBI observations
    print_obs_stats(t_cat)

    # Statistics of the formal uncertainty
    print_err_stats(t_cat)

    # Positional offset wrt. a priori catalog
    print_oft_wrt_apriori(t_cat, ref_cat, trans_mod)


if __name__ == "__main__":
    pass
# --------------------------------- END --------------------------------
