# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  2 16:00:08 2017

Positional transformation.

@author: Neo

Oct 29, 2018: re-write all the codes
Apr 19, 2021: use 'curve_fit' to do the lsq fitting
"""

import sys
from scipy.optimize import curve_fit
import numpy as np
from numpy import sin, cos, pi, concatenate

from astropy.table import Table
from astropy import units as u

# My modules
# from .cov_mat import calc_wgt_mat, read_cov_mat
from .stats_calc import calc_chi2_2d, calc_gof


__all__ = ["iers_tran_fit", "iers_tran_fit_4_table", "print_iers1995_result_4_dict",
           "iers_tran_fit_4_table1", "iers_tran_fit_4_table2", "iers_tran_fit_4_table3"]


# =========================IERS Transformation Functions =========================
def rotation1(X, **kwargs):
    """A sample code

    Parameters
    ----------
    x : 1-D array
        (ra, dec) in radian
    """

    ra, dec = X
    dra = -locals["r1"] * cos(ra) * sin(dec) - locals["r2"] * sin(ra) * sin(dec) + \
        locals["r3"] * cos(dec)
    ddec = + locals["r1"] * sin(ra) - locals["r2"] * cos(ra)

    return np.concatenate((dra, ddec))


def tran_func1(pos, rx, ry, rz):
    """IERS Coordinate transformation function version 01.

    The transformation function considering onl the rigid rotation
    is given by
    d_RA^* = -r_x*sin(dec)*cos(ra) - r_y*sin(dec)*sin(ra) + r_z*cos(dec)
    d_DE   = +r_x*sin(ra) - r_y*cos(ra)

    Parameters
    ----------
    ra/dec : array of float
        right ascension/declination in radian
    rx/ry/rz : float
        rotational angles around X-, Y-, and Z-axis

    Returns
    -------
    dra/ddec : array of float
        R.A.(*cos(Dec.))/Dec. differences
    """

    N = len(pos) // 2
    ra, dec = pos[:N], pos[N:]

    dra = -rx * cos(ra) * sin(dec) - ry * sin(ra) * sin(dec) + rz * cos(dec)
    ddec = rx * sin(ra) - ry * cos(ra)
    dpos = np.concatenate((dra, ddec))

    return dpos


def tran_func2(pos, rx, ry, rz, dz):
    """IERS Coordinate transformation function version 02.

    The transformation equation considers a rigid rotation together with
    one declination bias, which could be given by the following
    d_RA^* = -r_x*sin(dec)*cos(ra) - r_y*sin(dec)*sin(ra) + r_z*cos(dec)
    d_DE   = +r_x*sin(ra)          - r_y*cos(ra) + dz

    Parameters
    ----------
    ra/dec : array of float
        right ascension/declination in radian
    rx/ry/rz : float
        rotational angles around X-, Y-, and Z-axis
    dz : float
        bias in declination

    Returns
    -------
    dra/ddec : array of float
        R.A.(*cos(Dec.))/Dec. differences
    """

    N = len(pos) // 2
    ra, dec = pos[:N], pos[N:]

    dra = [-rx * cos(ra) * sin(dec) - ry *
           sin(ra) * sin(dec) + rz * cos(dec)][0]
    ddec = [rx * sin(ra) - ry * cos(ra) + dz][0]
    dpos = np.concatenate((dra, ddec))

    return dpos


def tran_func3a(pos, rx, ry, rz, d1, d2, b2):
    """IERS Coordinate transformation function version 03(a).

    The transformation equation considers a rigid rotation together with
    two declination-dependent slopes and one declination bias, which could
    be given by the following
    d_RA^* = -r_x*sin(dec)*cos(ra) - r_y*sin(dec)*sin(ra) + r_z*cos(dec)
             + D_1*(dec-DE0)*cos(dec)
    d_DE   = +r_x*sin(ra)         - r_y*cos(ra)
             + D_2*(dec-DE0) + B_2
    where the reference declination is choosen as DE0 = 0.0.

    Parameters ----------
    ra/dec : array of float right ascension/declination in radian
    rx/ry/rz : float rotational angles around X-, Y-, and Z-axis
    d1/d2 : float
        two declination-dependent slopes in right ascension/declination
    b2 : float
        one bias in declination

    Returns
    -------
    dra/ddec : array of float
        R.A.(*cos(Dec.))/Dec. differences
    """

    N = len(pos) // 2
    ra, dec = pos[:N], pos[N:]
    dec0 = 0
    delta_dec = dec - dec0

    dra = [-rx * cos(ra) * sin(dec) - ry *
           sin(ra) * sin(dec) + rz * cos(dec)
           + d1 * delta_dec * cos(dec)][0]
    ddec = [rx * sin(ra) - ry * cos(ra)
            + d2 * delta_dec + b2][0]
    dpos = np.concatenate((dra, ddec))

    return dpos


def tran_func3b(pos, rx, ry, rz, d1, d2, b2):
    """IERS Coordinate transformation function version 03(b).

    The transformation equation considers a rigid rotation together with
    two declination-dependent slopes and one declination bias, which could
    be given by the following
    d_RA^* = -r_x*sin(dec)*cos(ra) - r_y*sin(dec)*sin(ra) + r_z*cos(dec)
             + D_1*(dec-DE0)
    d_DE   = +r_x*sin(ra)         - r_y*cos(ra)
             + D_2*(dec-DE0) + B_2
    where the reference declination is choosen as DE0 = 0.0.
    The difference between v03 and v03-00 is the defination of the slope
    in the right ascension.

    Parameters
    ----------
    ra/dec : array of float
        right ascension/declination in radian
    rx/ry/rz : float
        rotational angles around X-, Y-, and Z-axis
    d1/d2 : float
        two declination-dependent slopes in right ascension/declination
    b2 : float
        one bias in declination

    Returns
    -------
    dra/ddec : array of float
        R.A.(*cos(Dec.))/Dec. differences
    """

    N = len(pos) // 2
    ra, dec = pos[:N], pos[N:]
    dec0 = 0
    delta_dec = dec - dec0

    dra = [-rx * cos(ra) * sin(dec) - ry *
           sin(ra) * sin(dec) + rz * cos(dec)
           + d1 * delta_dec][0]
    ddec = [rx * sin(ra) - ry * cos(ra)
            + d2 * delta_dec + b2][0]
    dpos = np.concatenate((dra, ddec))

    return dpos


# ========================= Resolve Results =========================
def pmt_name_init(tran_type="1"):
    """Initialize parameter name.
    """

    if tran_type == "1":
        para_name = ["rx", "ry", "rz"]
    elif tran_type == "2":
        para_name = ["rx", "ry", "rz", "dz"]
    elif tran_type in ["3", "3a", "3b"]:
        para_name = ["rx", "ry", "rz", "d1", "d2", "dz"]
    else:
        print("Undefined tran_type")
        sys.system(1)

    return para_name


def pmt_name_guess(pmt):
    """Initialize parameter name.
    """

    N = len(pmt)

    if N == 3:
        para_name = pmt_name_init(tran_type="1")
    elif N == 4:
        para_name = pmt_name_init(tran_type="2")
    elif N == 6:
        para_name = pmt_name_init(tran_type="3")
    else:
        print("Could not guess the parameter names.")
        sys.system(1)

    return para_name


def resolve_result(output, popt, pcov, tran_type, pos_chi2_rdc):
    """Resolve the result
    """

    para_name = pmt_name_init(tran_type)

    # Covariance matrix -> Correlation matrix
    sig = np.sqrt(pcov.diagonal())

    # Rescale the formal error
    # Correlation coefficient.
    corr_mat = np.array([pcov[i, j] / sig[i] / sig[j]
                         for j in range(len(sig))
                         for i in range(len(sig))])
    corr_mat.resize((len(sig), len(sig)))

    # Rescale the formal error
    sig = sig * np.sqrt(pos_chi2_rdc)

    output["pmt"] = popt
    output["sig"] = sig
    output["cor_mat"] = corr_mat

    for i, par in enumerate(para_name):
        output[par] = popt[i]
        output[par+"_err"] = sig[i]

    for i, pari in enumerate(para_name):
        for j, parj in enumerate(para_name[i+1:]):
            output[pari+parj+"_cor"] = corr_mat[i, j]

    return output


# ========================= LSQ fitting =========================
def iers_tran_fit(dra, ddec, ra, dec,
                  dra_err=None, ddec_err=None, dra_ddec_cor=None, flog=sys.stdout,
                  unit_deg=True, tran_type="1"):
    """Least square fitting of transformation equation.

    The transformation function considering onl the rigid rotation
    is given by
    d_RA^* = -r_x*sin(dec)*cos(ra) - r_y*sin(dec)*sin(ra) + r_z*cos(dec)
    d_DE   = +r_x*sin(ra) - r_y*cos(ra)

    Parameters
    ----------
    dra/ddec : array of float
        offset in right ascension/declination
    ra/dec : array of float
        right ascension/declination in radian
    dra_err/ddec_err : array of float
        formal uncertainties of dra/ddec, default value is None
    corr_arr : array of float
        correlation between dra and ddec, default value is None

    Returns
    -------
    opt : array of (3,)
        estimation of three rotational angles
    sig : array of (3,)
        formal uncertainty of estimations
    corr_mat : array of (3,3)
        correlation coefficients between estimations
    """

    # Degree -> radian
    if unit_deg:
        ra = np.deg2rad(ra)
        dec = np.deg2rad(dec)

    # Position vector
    pos = np.concatenate((ra, dec))
    dpos = np.concatenate((dra, ddec))
    N = len(dra)

    # Create covariance matrix
    if dra_err is not None:
        cov_mat = np.diag(np.concatenate((dra_err ** 2, ddec_err**2)))

        if dra_ddec_cor is not None:
            # Consider the correlation between dra and ddec
            dra_ddec_cov = dra_err * ddec_err * dra_ddec_cor
            for i, dra_ddec_covi in enumerate(dra_ddec_cov):
                cov_mat[i, i+N] = dra_ddec_covi
                cov_mat[i+N, i] = dra_ddec_covi

    # Do the LSQ fit
    if tran_type == "1":
        trans_func = tran_func1
    elif tran_type == "2":
        trans_func = tran_func2
    elif tran_type == "3a":
        trans_func = tran_func3a
    elif tran_type in ["3", "3b"]:
        trans_func = tran_func3b
    else:
        print("Undefined tran_type!")
        sys.system(1)

    if dra_err is None:
        popt, pcov = curve_fit(trans_func, pos, dpos)
    else:
        popt, pcov = curve_fit(trans_func, pos, dpos,
                               sigma=cov_mat, absolute_sigma=False)

    M = len(popt)

    output = {}
    # Prediction
    predict = trans_func(pos, *popt)
    output["predict_ra"] = predict[:N]
    output["predict_dec"] = predict[N:]

    # Residual
    output["residual_ra"] = dra - output["predict_ra"]
    output["residual_dec"] = ddec - output["predict_dec"]
    rsd_ra, rsd_ddec = output["residual_ra"], output["residual_dec"]

    # Chi squared per dof
    if dra_err is None:
        # Calculate chi2/ndof
        output["chi2_dof_ra"] = np.sum(output["residual_ra"]) / (N - M)
        output["chi2_dof_dec"] = np.sum(output["residual_dec"]) / (N - M)

        unit_wgt = np.ones_like(dra)
        zero_cov = np.zeros_like(dra)
        apr_chi2_rdc = calc_chi2_2d(dra, unit_wgt, ddec, unit_wgt, zero_cov,
                                    reduced=True, num_fdm=2*N-1-M)
        pos_chi2_rdc = calc_chi2_2d(dra, unit_wgt, ddec, unit_wgt, zero_cov,
                                    reduced=True, num_fdm=2*N-1-M)
        pos_chi2 = calc_chi2_2d(dra, unit_wgt, ddec, unit_wgt, zero_cov)

    else:
        # Calculate chi2/ndof
        output["chi2_dof_ra"] = np.sum(output["residual_ra"] / dra_err) / (N - M)
        output["chi2_dof_dec"] = np.sum(output["residual_dec"] / ddec_err) / (N - M)

        apr_chi2_rdc = calc_chi2_2d(dra, dra_err, ddec, ddec_err, dra_ddec_cov,
                                    reduced=True, num_fdm=2*N-1-M)
        pos_chi2_rdc = calc_chi2_2d(rsd_ra, dra_err, rsd_ddec, ddec_err,
                                    dra_ddec_cov, reduced=True, num_fdm=2*N-1-M)

        pos_chi2 = calc_chi2_2d(rsd_ra, dra_err, rsd_ddec, ddec_err, dra_ddec_cov)

    if flog is not None:
        print("# apriori reduced Chi-square for: %10.3f\n"
              "# posteriori reduced Chi-square for: %10.3f" %
              (apr_chi2_rdc, pos_chi2_rdc), file=flog)

        # Calculate the goodness-of-fit
        print("# goodness-of-fit is %10.3f" %
              calc_gof(2*N-1-M, pos_chi2), file=flog)

    # Rescale the formal errors
    output = resolve_result(output, popt, pcov, tran_type, pos_chi2_rdc)

    return output


def iers_tran_fit_4_table(data_tab, tran_type="1"):
    """IERS-1995 model fit for Atstropy.Table

    Parameters
    ----------
    data_tab : Astropy.table-like
        must contain column names of ["dra", "ddec", "ra", "dec",
        "dra_err", "ddec_err"]
    tran_type : string
        flag to determine which parameters to be fitted

    Returns
    ----------
    output : dict
        results of the fit
    """

    # Transform astropy.Column into np.array
    if "dra" in data_tab.colnames:
        dra = np.array(data_tab["dra"])
    elif "pmra" in data_tab.colnames:
        dra = np.array(data_tab["pmra"])
    else:
        print("'dra' or 'pmra' is not specificed.")
        sys.exit(1)

    if "ddec" in data_tab.colnames:
        ddec = np.array(data_tab["ddec"])
    elif "pmdec" in data_tab.colnames:
        ddec = np.array(data_tab["pmdec"])
    else:
        print("'ddec' or 'pmdec' is not specificed.")
        sys.exit(1)

    ra = np.array(data_tab["ra"])
    dec = np.array(data_tab["dec"])

    if "dra_err" in data_tab.colnames:
        dra_err = np.array(data_tab["dra_err"])
    elif "dra_error" in data_tab.colnames:
        dra_err = np.array(data_tab["dra_error"])
    elif "pmra_err" in data_tab.colnames:
        dra_err = np.array(data_tab["pmra_err"])
    elif "pmra_error" in data_tab.colnames:
        dra_err = np.array(data_tab["pmra_error"])
    else:
        print("'dra_err', 'dra_error', 'pmra_err' or 'pmra_error' is not specificed.")
        print("So that I will use an equal weights.")
        dra_err = np.ones(len(data_tab))

    if "ddec_err" in data_tab.colnames:
        ddec_err = np.array(data_tab["ddec_err"])
    elif "ddec_error" in data_tab.colnames:
        ddec_err = np.array(data_tab["ddec_error"])
    elif "pmdec_err" in data_tab.colnames:
        ddec_err = np.array(data_tab["pmdec_err"])
    elif "pmdec_error" in data_tab.colnames:
        ddec_err = np.array(data_tab["pmdec_error"])
    else:
        print("'ddec_err', 'ddec_error', 'pmdec_err' or 'pmdec_error' is not specificed.")
        print("So that I will use an equal weights.")
        ddec_err = np.ones(len(data_tab))

    if "dra_ddec_cov" in data_tab.colnames:
        dra_ddc_cov = np.array(data_tab["dra_ddec_cov"])
        dra_ddc_cor = dra_ddc_cov / dra_err / ddec_err
    elif "dra_ddec_cor" in data_tab.colnames:
        dra_ddc_cor = np.array(data_tab["dra_ddec_cor"])
    elif "pmra_pmdec_corr" in data_tab.colnames:
        dra_ddc_cor = np.array(data_tab["pmra_pmdec_corr"])
    elif "pmra_pmdec_cor" in data_tab.colnames:
        dra_ddc_cor = np.array(data_tab["pmra_pmdec_cor"])
    else:
        print("'dra_ddec_cov', 'dra_ddec_cor', 'pmra_pmdec_corr' or "
              "'pmra_pmdec_cor' is not specificed.")
        print("So that I will consider the covariance matrix as a diagonal one.")
        dra_ddc_cor = None

    # Do the LSQ fitting
    output = iers_tran_fit(dra, ddec, ra, dec, dra_err, ddec_err, dra_ddc_cor,
                           unit_deg=True, tran_type=tran_type, flog=None)

    return output


def iers_tran_fit_4_table1(data_tab):
    """
    """

    output = iers_tran_fit_4_table(data_tab, tran_type="1")

    return output


def iers_tran_fit_4_table2(data_tab):
    """
    """

    output = iers_tran_fit_4_table(data_tab, tran_type="2")

    return output


def iers_tran_fit_4_table3(data_tab):
    """
    """

    output = iers_tran_fit_4_table(data_tab, tran_type="3")

    return output


# ========================= Output =========================
def print_tran_model_info(tran_type="1"):
    """Print the transformation model
    """

    if tran_type == "1":
        print("\nThe transformation function is given as\n"
              "d_RA ^ * = -r_x*sin(dec)*cos(ra) - r_y*sin(dec)*sin(ra) + r_z*cos(dec),\n"
              "d_DE     = +r_x*sin(ra) - r_y*cos(ra),\n"
              "where the unknowns are rotation angle around X-, Y-, Z-axis "
              "which are r_x, r_y, and r_x.")
    elif tran_type == "2":
        print("\nThe transformation function is given as\n"
              "d_RA ^ * = -r_x*sin(dec)*cos(ra) - r_y*sin(dec)*sin(ra) + r_z*cos(dec),\n"
              "d_DE     = +r_x*sin(ra) - r_y*cos(ra) + dz,\n"
              "where the unknowns are rotation angle around X-, Y-, Z-axis "
              "which are r_x, r_y, and r_x, dz the declination bias.")
    elif tran_type == "3a":
        print("\nThe transformation function is given as\n"
              "d_RA ^ * = -r_x*sin(dec)*cos(ra) - r_y*sin(dec)*sin(ra) + r_z*cos(dec)\n"
              "           + D_1*(dec-DE0)*cos(dec),\n"
              "d_DE     = +r_x*sin(ra) - r_y*cos(ra)\n"
              "           + D_2*(dec-DE0) + B_2,\n"
              "where the unknowns are rotation angle around X-, Y-, Z-axis "
              "which are r_x, r_y, and r_x,"
              "B_2 the declination bias, D_1 and D_2 the slope."
              "The reference declination is choosen as DE0 = 0.")
    elif tran_type in ["3", "3b"]:
        print("\nThe transformation function is given as\n"
              "d_RA ^ * = -r_x*sin(dec)*cos(ra) - r_y*sin(dec)*sin(ra) + r_z*cos(dec)\n"
              "           + D_1*(dec-DE0),\n"
              "d_DE     = +r_x*sin(ra) - r_y*cos(ra)\n"
              "           + D_2*(dec-DE0) + B_2,\n"
              "where the unknowns are rotation angle around X-, Y-, Z-axis "
              "which are r_x, r_y, and r_x,"
              "B_2 the declination bias, D_1 and D_2 the slope."
              "The reference declination is choosen as DE0 = 0.")
    else:
        print("Undefined tran_type!")
        sys.system(1)


def print_corr(names, parcorrs, deci_digit=2, included_one=True,
               opt=sys.stdout):
    """Print the correlation coefficient in the screen.

    Parameters
    ----------
    names : array
        names or labels of the parameters
    parcorrs : array of N * N
        matrix or correlation coefficient
    deci_digit : int
        decimal digits. Only 1 and 2 are supported. Default is 2.
    included_one : boolean
        to include the correlation between the same parameters (of course the
        value equals to 1) or not. True for yes.
    opt : file handling
        Default to print all the output on the screen.
    """

    parnb = len(names)

    print("\nCorrelation coefficient", file=opt)
    print("---------------------------------------------------------", file=opt)

    # If the correlation matrix is an object of np.mat type,
    # convert it to np.ndarray
    if type(parcorrs) is np.mat or type(parcorrs) is np.matrix:
        parcorrs = np.array(parcorrs)

    if deci_digit == 1:
        # Now begin to print the correlation coefficient
        if included_one:
            # The first line
            print(("  %4s" * (parnb+1)) % ("    ", *names), file=opt)

            # Include the correlation coefficient of one
            for i, pmt_namei in enumerate(names):
                line_fmt = "  %4s" + "  %+4.1f" * (i + 1)
                print(line_fmt % (pmt_namei, *parcorrs[i, :i+1]), file=opt)
        else:
            # The first line
            print(("  %4s" * parnb) % ("    ", *names[:-1]), file=opt)

            for i in range(1, parnb):
                line_fmt = "  %4s" + "  %+4.1f" * i
                print(line_fmt % (names[i], *parcorrs[i, :i]), file=opt)

    elif deci_digit == 2:

        # Now begin to print the correlation coefficient
        if included_one:
            # The first line
            print(("  %5s" * (parnb+1)) % ("    ", *names), file=opt)

            for i, pmt_namei in enumerate(names):
                line_fmt = "  %5s" + "  %+5.2f" * (i + 1)
                print(line_fmt % (pmt_namei, *parcorrs[i, :i+1]), file=opt)
        else:
            # The first line
            print(("  %5s" * parnb) % ("    ", *names[:-1]), file=opt)

            for i in range(1, parnb):
                line_fmt = "  %5s" + "  %+5.2f" * i
                print(line_fmt % (names[i], *parcorrs[i, :i]), file=opt)
    else:
        print("The decimal digit of only 1 or 2 is supported!")
        sys.exit()


def print_iers1995_corr(parcorrs, parnames):
    """Print the correlation coefficient of VSH02 parameters in the screen.

    Parameters
    ----------
    parcorrs : array of N * N
        matrix or correlation coefficient
    deci_digit : int
        decimal digits. Only 1 and 2 are supported. Default is 2.
    included_one : boolean
        to include the correlation between the same parameters (of course the
        value equals to 1) or not. True for yes.
    """

    parnb = len(parnames)

    # Check the shape of the matrix
    a, b = parcorrs.shape
    if a != b or a != parnb:
        print(
            "The shape of the correlation matrix should be (N, N)(N={:d})!".format(parnb))
        sys.exit()

    print_corr(parnames, parcorrs, deci_digit=1, included_one=True, opt=sys.stdout)


def print_iers1995_result(pmts, sigs, parcorrs,
                          tran_type="1", opt=sys.stdout, fmt="%5.0f"):
    """Print estmates and corresponding formal errors of vsh01 parameters.

    Parameters
    ----------
    parnames : array of string
        parnames or labels of the parameters
    pmts : array of float
        estimates of parameters
    sigs : array of float
        formal errors of estimates
    opt : file handling
        Default to print all the output on the screen.
    fmt : string
        specifier of the output format
    """

    parnb = len(pmts)
    parnames = pmt_name_guess(pmts)

    tpmt = Table([parnames, pmts, sigs], names=[
        "Parameter", "Estimate", "Error"])
    tpmt["Estimate"].format = fmt
    tpmt["Error"].format = fmt
    tpmt["Estimate"].unit = u.uas
    tpmt["Error"].unit = u.uas

    print(tpmt, file=opt)

    print_iers1995_corr(parcorrs, parnames)


def print_iers1995_result_4_dict(output, parnames=None, tran_type="1", opt=sys.stdout, fmt="%5.0f"):
    """Print estmates and corresponding formal errors of vsh01 parameters.

    Parameters
    ----------
    parnames : array of string
        parnames or labels of the parameters
    pmts : array of float
        estimates of parameters
    sigs : array of float
        formal errors of estimates
    opt : file handling
        Default to print all the output on the screen.
    fmt : string
        specifier of the output format
    """

    pmts = output["pmt"]
    sigs = output["sig"]
    parcorrs = output["cor_mat"]

    parnb = len(pmts)
    parnames = pmt_name_guess(pmts)

    tvsh = Table([parnames, pmts, sigs], names=[
        "Parameter", "Estimate", "Error"])
    tvsh["Estimate"].format = fmt
    tvsh["Error"].format = fmt
    tvsh["Estimate"].unit = u.uas
    tvsh["Error"].unit = u.uas

    print_tran_model_info(tran_type)
    print("\n")
    print(tvsh, file=opt)
    print_iers1995_corr(parcorrs, parnames)


def main():
    pass


if __name__ == "__main__":
    main()

# -------------------- END -----------------------------------
