# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  2 22:54:38 2017

@author: Neo

VSH function.
The full covariance matrix is used.

# Notice !!!
# unit for RA and DE are rad.

History

N.Liu, 22/02/2018 : add some comments;
                    add new funtion 'test_code';
                    calculate the rms of residuals and reduced chi-squares.
N.Liu, 31/03/2018 : add new elimination criterior of outliers,
                      i.e., functions 'elim_angsep' and 'elim_norsep';
                    add some comments to understand these codes;
N.Liu, 04/04/2018 : add a new input parameter 'wgt' to function
                      'elim_nsigma';
                    add 2 new input parameters to functions
                      'VSHdeg01_fitting' and 'VSHdeg02_fitting';
                    add a new function 'find_good_obs';
                    functions 'VSHdeg01_fitting' and 'VSHdeg02_fitting'
                      now can use different outlier elimination algorithm;
N.Liu, 04/04/2018 : divide this code into two files "vsh_deg1_cor" and
                    "vsh_deg2_cor";
N.Liu, 16/07/2018 : printing output to a file is optional.
N.Liu, 27/09/2018 : add a new output "gof" of the function "vsh_deg02_fitting";
                    change the function name: "VSHdeg02" -> "vsh_deg02_solve",
                             "VSHdeg02_fitting" -> "vsh_deg02_fitting";
                    change the order of inputs for the function "vsh_deg01_fitting";
N.Liu, 09/09/2019: add new argument 'return_aux' to function
                    'vsh_deg02_fitting'
"""

import numpy as np
from numpy import sin, cos, pi, concatenate
import sys
# My modules
from .stats_calc import calc_wrms, calc_chi2_2d, calc_gof, calc_mean
from .pos_diff import nor_sep_calc
from .vsh_common_func import (elim_nsigma, elim_angsep, elim_norsep,
                              wgt_mat, find_good_obs, normal_matrix_calc)

__all__ = ["residual_calc02", "vsh_deg02_solve",
           "vsh_deg02_fitting", "vsh_deg02_fitting_4_table"]


# ------------------ FUNCTION --------------------------------


# ---------------------------------------------------
def vsh_func01(ra, dec,
               g1, g2, g3, r1, r2, r3):
    '''VSH function of the first degree.

    Parameters
    ----------
    ra/dec : array of float
        Right ascension/Declination in radian
    r1, r2, r3 : float
        rotation parameters
    g1, g2, g3 : float
        glide parameters

    Returns
    ----------
    dra/ddec : array of float
        R.A.(*cos(Dec.))/Dec. differences in uas
    '''

    dra = [-r1 * cos(ra) * sin(dec) - r2 * sin(ra) * sin(dec)
           + r3 * cos(dec)
           - g1 * sin(ra) + g2 * cos(ra)][0]
    ddec = [+ r1 * sin(ra) - r2 * cos(ra)
            - g1 * cos(ra) * sin(dec) - g2 * sin(ra) * sin(dec)
            + g3 * cos(dec)][0]

    return dra, ddec


# ---------------------------------------------------
def residual_calc02(dRA, dDE, RA, DE, param02):
    '''Calculate the residuals of RA/Dec

    Parameters
    ----------
    dRA/dDE : array of float
        R.A.(*cos(Dec.))/Dec. differences in uas
    RA/DE : array of float
        Right ascension/Declination in radian
    param02 : array of float
        estimation of rotation, glide, and quadrupolar parameters

    Returns
    ----------
    ResRA/ResDE : array of float
        residual array of dRA(*cos(Dec))/dDec in uas.
    '''

    # Theoritical value
    dra, ddec = vsh_func_calc02(RA, DE, param02)

    # Calculate the residual. ( O - C )
    ResRA, ResDE = dRA - dra, dDE - ddec

    return ResRA, ResDE


# ---------------------------------------------------
def vsh_deg02_solve(dRA, dDE, e_dRA, e_dDE, RA, DE, cov=None, fit_type="full"):
    '''2rd degree of VSH function: glide and rotation.

    The 2nd degree of VSH function: glide and rotation + quadrupole.

    Parameters
    ----------
    dRA/dDE : array of float
        R.A.(*cos(Dec.))/Dec. differences in uas
    e_dRA/e_dDE : array of float
        formal uncertainty of dRA(*cos(DE))/dDE in uas
    cov : array of float
        covariance between dRA and dDE in uas^2
    RA/DE : array of float
        Right ascension/Declination in radian

    Returns
    ----------
    x : array of float
        estimation of (d1, d2, d3,
                        r1, r2, r3,
                        ER_22, EI_22, ER_21, EI_21, E_20,
                        MR_22, MI_22, MR_21, MI_21, M_20) in uas
    sig : array of float
        uncertainty of x in uas
    corrmat : matrix
        matrix of correlation coefficient.
    '''

    # Maxium number of calculation the matrix
    max_num = 500

    if dRA.size > max_num:
        div = dRA.size // max_num
        rem = dRA.size % max_num

        if cov is None:
            A, b = normal_matrix_calc(dRA[:rem], dDE[:rem],
                                      e_dRA[:rem], e_dDE[:rem],
                                      RA[:rem], DE[:rem], cov, fit_type, jac_mat_deg02)
        else:
            A, b = normal_matrix_calc(dRA[:rem], dDE[:rem],
                                      e_dRA[:rem], e_dDE[:rem],
                                      RA[:rem], DE[:rem], cov[:rem], fit_type, jac_mat_deg02)

        for i in range(div):
            ista = rem + i * max_num
            iend = ista + max_num

            if cov is None:
                An, bn = normal_matrix_calc(dRA[ista:iend], dDE[ista:iend],
                                            e_dRA[ista:iend], e_dDE[ista:iend],
                                            RA[ista:iend], DE[ista:iend],
                                            cov, fit_type, jac_mat_deg02)
            else:
                An, bn = normal_matrix_calc(dRA[ista:iend], dDE[ista:iend],
                                            e_dRA[ista:iend], e_dDE[ista:iend],
                                            RA[ista:iend], DE[ista:iend],
                                            cov[ista:iend], fit_type, jac_mat_deg02)
            A = A + An
            b = b + bn
    else:

        A, b = normal_matrix_calc(dRA, dDE, e_dRA, e_dDE, RA, DE, cov, fit_type, jac_mat_deg02)

    # Solve the equations.
    # x = (d1, d2, d3,
    #      r1, r2, r3,
    #      ER_22, EI_22, ER_21, EI_21, E_20,
    #      MR_22, MI_22, MR_21, MI_21, M_20)
    x = np.linalg.solve(A, b)

    # Covariance.
    pcov = np.linalg.inv(A)
    sig = np.sqrt(pcov.diagonal())

    # Correlation coefficient.
    corrmat = np.array([pcov[i, j] / sig[i] / sig[j]
                        for j in range(len(x))
                        for i in range(len(x))])
    corrmat.resize((len(x), len(x)))

    # Return the result.
    return x, sig, corrmat


# ----------------------------------------------------
def vsh_deg02_fitting(dRA, dDE, RA, DE, e_dRA=None, e_dDE=None,
                      cov=None, flog=None,
                      elim_flag="sigma", N=3.0, return_aux=False, fit_type="full"):
    '''2rd-degree vsh fitting.

    Parameters
    ----------
    dRA/dDE : array of float
        R.A.(*cos(Dec.))/Dec. differences in uas
    e_dRA/e_dDE : array of float
        formal uncertainty of dRA(*cos(DE))/dDE in uas
    cov : array of float
        covariance between dRA and dDE in uas^2
    RA/DE : array of float
        Right ascension/Declination in radian
    flog :
        handlings of output file.
    elim_flag : string
        "sigma" uses n-sigma principle
        "angsep" uses angular seperation as the criteria
        "norsep" uses normalized seperation as the criteria
        "nor_ang" uses both normalized and angular seperation as the criteria
        "None" or "none" doesn't use any criteria
    N : float
        N-sigma principle for eliminating the outliers
        or
        the maximum seperation (uas)
   return_aux : Boolean
        If true, return the post-fit residuals besides the parameter estimates

    Returns
    ----------
    x : array of float
        estimaation of (d1, d2, d3, r1, r2, r3) in uas
    sig : array of float
        uncertainty of x in uas
    cofmat : matrix
        matrix of correlation coefficient.
    ind_outl : array of int
        index of outliers
    dRAres/dDEres: array of float
        residual array of dRA(*cos(Dec))/dDec in uas.
    '''

    # If we don't know the individual error
    if e_dRA is None:
        e_dRA = np.ones_like(dRA)
        gof_known = True  # Assume the gof is 1
    else:
        gof_known = False

    if e_dDE is None:
        e_dDE = np.ones_like(dDE)
        gof_known = True  # Assume the gof is 1
    else:
        gof_known = False

    # Calculate the apriori wrms
    if flog is not None:
        meanRA = calc_mean(dRA)
        rmsRA = calc_wrms(dRA)
        wrmsRA = calc_wrms(dRA, e_dRA)
        stdRA = np.std(dRA)
        meanDE = calc_mean(dDE)
        rmsDE = calc_wrms(dDE)
        wrmsDE = calc_wrms(dDE, e_dDE)
        stdDE = np.std(dDE)
        print("# apriori statistics (weighted)\n"
              "#         mean for RA: %10.3f \n"
              "#          rms for RA: %10.3f \n"
              "#         wrms for RA: %10.3f \n"
              "#          std for RA: %10.3f \n"
              "#        mean for Dec: %10.3f \n"
              "#         rms for Dec: %10.3f \n"
              "#        wrms for Dec: %10.3f \n"
              "#         std for Dec: %10.3f   " %
              (meanRA, rmsRA, wrmsRA, stdRA, meanDE, rmsDE, wrmsDE, stdDE), file=flog)

    # Calculate the reduced Chi-square
    if flog is not None:
        apr_chi2 = calc_chi2_2d(dRA, e_dRA, dDE, e_dDE, cov, reduced=True)
        print("# apriori reduced Chi-square for: %10.3f\n" % apr_chi2, file=flog)

    # Now we can use different criteria of elimination.
    if elim_flag is "None" or elim_flag is "none":
        x, sig, cofmat = vsh_deg02_solve(dRA, dDE, e_dRA, e_dDE, RA, DE, cov, fit_type)
        ind_good = np.arange(dRA.size)

    elif elim_flag is "sigma":
        x, sig, cofmat = vsh_deg02_solve(dRA, dDE, e_dRA, e_dDE, RA, DE, cov, fit_type)
        # Iteration.
        num1 = 1
        num2 = 0
        while(num1 != num2):
            num1 = num2

            # Calculate the residual. ( O - C )
            rRA, rDE = residual_calc02(dRA, dDE, RA, DE, x)
            ind_good = elim_nsigma(rRA, rDE, N, wgt_flag=True,
                                   y1_err=e_dRA, y2_err=e_dDE)
            # ind_good = elim_nsigma(rRA, rDE, N)
            num2 = dRA.size - ind_good.size
            # num2 = dRA.size - len(ind_good)

            dRAn, dDEn, e_dRAn, e_dDEn, covn, RAn, DEn = find_good_obs(
                dRA, dDE, e_dRA, e_dDE, cov, RA, DE, ind_good)

            xn, sign, corrmatn = vsh_deg02_solve(dRAn, dDEn, e_dRAn, e_dDEn,
                                                 RAn, DEn, covn, fit_type)

            x, sig, cofmat = xn, sign, corrmatn

            if flog is not None:
                print("# Number of sample: %d" % (dRA.size-num2),
                      file=flog)

    else:
        ang_sep, X_a, X_d, X = nor_sep_calc(dRA, dDE, e_dRA, e_dDE, cov)

        if ang_sep is None:
            ang_sep, X_a, X_d, X = nor_sep_calc(dRA, dDE, e_dRA, e_dDE, cov)

        if elim_flag is "angsep":
            ind_good = elim_angsep(ang_sep, 10)
        elif elim_flag is "norsep":
            ind_good = elim_norsep(X, 3)
        elif elim_flag is "nor_ang":
            ind_go_nor = elim_norsep(X, 3)
            ind_go_ang = elim_angsep(ang_sep, 10)
            ind_good = (ind_go_nor & ind_go_ang)
        else:
            print("ERROR: elim_flag can only be sigma, angsep, norsep,"
                  " or nor_ang!")
            exit()

        # Find all good observations
        dRAn, dDEn, e_dRAn, e_dDEn, covn, RAn, DEn = find_good_obs(
            dRA, dDE, e_dRA, e_dDE, cov, RA, DE, ind_good)
        x, sig, cofmat = vsh_deg02_solve(dRAn, dDEn, e_dRAn, e_dDEn,
                                         RAn, DEn, covn, fit_type)

        if flog is not None:
            print("# Number of sample: %d" % dRAn.size,
                  file=flog)

    ind_outl = np.setxor1d(np.arange(dRA.size), ind_good)
    dRAres, dDEres = residual_calc02(dRA, dDE, RA, DE, x)

    # Calculate the posteriori wrms
    if flog is not None:
        meanRA = calc_mean(dRAres)
        rmsRA = calc_wrms(dRAres)
        wrmsRA = calc_wrms(dRAres, e_dRA)
        stdRA = np.std(dRAres)
        meanDE = calc_mean(dDEres)
        rmsDE = calc_wrms(dDEres)
        wrmsDE = calc_wrms(dDEres, e_dDE)
        stdDE = np.std(dDEres)
        print("# posteriori statistics  of vsh01 fit (weighted)\n"
              "#         mean for RA: %10.3f \n"
              "#          rms for RA: %10.3f \n"
              "#         wrms for RA: %10.3f \n"
              "#          std for RA: %10.3f \n"
              "#        mean for Dec: %10.3f \n"
              "#         rms for Dec: %10.3f \n"
              "#        wrms for Dec: %10.3f \n"
              "#         std for Dec: %10.3f   " %
              (meanRA, rmsRA, wrmsRA, stdRA, meanDE, rmsDE, wrmsDE, stdDE), file=flog)

    # Calculate the reduced Chi-square
    M = 16
    pos_chi2_rdc = calc_chi2_2d(dRAres, e_dRA, dDEres, e_dDE, cov,
                                reduced=True, num_fdm=2*dRAres.size-1-M)

    if flog is not None:
        print("# posteriori reduced Chi-square for: %10.3f\n" %
              pos_chi2_rdc, file=flog)

    # Calculate the goodness-of-fit
    if flog is not None:
        pos_chi2 = calc_chi2_2d(dRAres, e_dRA, dDEres, e_dDE, cov)
        print("# goodness-of-fit is %10.3f\n" %
              calc_gof(2*dRAres.size-1-M, pos_chi2), file=flog)

    # Rescale the formal errors
    sig = sig * np.sqrt(pos_chi2_rdc)

    # Return the result
    if return_aux:
        return x, sig, cofmat, ind_outl, dRAres, dDEres
    else:
        return x, sig, cofmat


def vsh_deg02_fitting_4_table(data_tab, fit_type="full", return_aux=False):
    """VSH fit for Atstropy.Table

    Parameters
    ----------
    data_tab : Astropy.table-like
        must contain column names of ["dra", "ddec", "ra", "dec",
        "dra_err", "ddec_err"]
    fit_type : string
        flag to determine which parameters to be fitted
        "full" for T- and S-vectors both
        "T" for T-vectors only
        "S" for S-vectors only
    pos_in_rad : Boolean
        tell if positions are given in radian, mostly False
    num_iter : int
        number of source once processed. 100 should be fine

    Returns
    ----------
    pmt : array of float
        estimation of (d1, d2, d3, r1, r2, r3) in dex
    sig : array of float
        uncertainty of x in dex
    cor_mat : matrix
        matrix of correlation coefficient.
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

    ra = np.deg2rad(np.array(data_tab["ra"]))
    dec = np.deg2rad(np.array(data_tab["dec"]))

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
    elif "dra_ddec_cor" in data_tab.colnames:
        dra_ddc_cor = np.array(data_tab["dra_ddec_cor"])
        dra_ddc_cov = dra_ddc_cor * dra_err * ddec_err
    elif "pmra_pmdec_corr" in data_tab.colnames:
        dra_ddc_cor = np.array(data_tab["pmra_pmdec_corr"])
        dra_ddc_cov = dra_ddc_cor * dra_err * ddec_err
    elif "pmra_pmdec_cor" in data_tab.colnames:
        dra_ddc_cor = np.array(data_tab["pmra_pmdec_cor"])
        dra_ddc_cov = dra_ddc_cor * dra_err * ddec_err
    else:
        print("'dra_ddec_cov', 'dra_ddec_cor', 'pmra_pmdec_corr' or "
              "'pmra_pmdec_cor' is not specificed.")
        print("So that I will consider the covariance matrix as a diagonal one.")
        dra_ddc_cov = None

    # Do the LSQ fitting
    output_data = vsh_deg02_fitting(dra, ddec, ra, dec, e_dRA=dra_err, e_dDE=ddec_err,
                                    cov=dra_ddc_cov, elim_flag="nor_ang",
                                    ang_sep=np.array(data_tab["ang_sep"]),
                                    X=np.array(data_tab["nor_sep"]),
                                    fit_type=fit_type, return_aux=return_aux)

    output = {}
    output["pmt"] = output_data[0]
    output["sig"] = output_data[1]
    output["cor_mat"] = output_data[2]

    if return_aux:
        output["outlier_index"] = output_data[3]
        output["dra_residual"] = output_data[4]
        output["ddec_residual"] = output_data[5]

    return output


# ------------------------- MAIN ---------------------------------------
if __name__ == "__main__":
    print("Nothing to do!")
# ------------------------- END ----------------------------------------
