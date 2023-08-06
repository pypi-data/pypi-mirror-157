#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name: vsh_fit.py
"""
Created on Tue Jul 13 10:01:39 2021

@author: Neo(niu.liu@nju.edu.cn)
"""

import numpy as np
from numpy import sin, cos, pi, concatenate
import sys

# My modules
from .stats_calc import calc_wrms, calc_chi2_2d, calc_gof, calc_mean
from .pos_diff import nor_sep_calc

__all__ = ["residual_calc", "vsh_solve",
           "vsh_fit", "vsh_fit_4_table"]


# ------------------ FUNCTION --------------------------------
def elim_nsigma(y1r, y2r, n=3.0, wgt_flag=False):
    """An outlier elimination using n-sigma criteria.

    Parameters
    ----------
    y1r/y2r : array of float
        residuals of RA and DC
    n : float
        the strength of elimination, default value 3.0
    wgt_flag : True or False, default False
        use the rms or wrms as the unit of n

    Returns
    ----------
    ind_good : array of int
        index of good observations
    """

    if wgt_flag:
        # wrms
        std1 = np.sqrt(np.sum(y1r**2 / y1_err**2) / np.sum(y1_err**-2))
        std2 = np.sqrt(np.sum(y2r**2 / y2_err**2) / np.sum(y2_err**-2))
    else:
        # rms
        std1 = np.sqrt(np.sum(y1r**2) / (y1r.size - 1))
        std2 = np.sqrt(np.sum(y2r**2) / (y2r.size - 1))

    mask1 = np.fabs(y1r) - n * std1 <= 0
    indice2 = np.fabs(y2r) - n * std2 <= 0
    ind_good = (indice1 & indice2)

    return ind_good


# ----------------------------------------------------
def elim_angsep(angsep, pho_max=10.0e3):
    """An outlier elimiantion based optic-radio angular seperation.

    Parameters
    ----------
    ang_sep : array of float
        angular seperation, in micro-as
    pho_max : float
        accepted maximum angular seperation, default 10.0 mas

    Returns
    ----------
    ind_good : array of int
        index of good observations
    """

    # print(pho_max)
    ind_good = angsep <= pho_max

    return ind_good


# ----------------------------------------------------
def elim_norsep(X, X_max=10.0):
    """A outlier elimiantion based the normalized optic-radio seperation.

    Parameters
    ----------
    X : array of float
        normalized separations, unit-less.
    X_max : float
        accepted maximum X, default 10.0

    Returns
    ----------
    ind_good : array of int
        index of good observations
    """

    ind_good = X <= X_max

    return ind_good


# ----------------------------------------------------
def find_good_obs(dRA, dDE, e_dRA, e_dDE, cov, RA, DE, ind_good):
    """Find the good observations based on index.

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
    ind_good : array of int
        index of good observations

    Returns
    ----------
    dRAn/dDEn : array of float
        R.A.(*cos(Dec.))/Dec. differences for good obsevations in uas
    e_dRAn/e_dDEn : array of float
        formal uncertainty of dRA(*cos(DE))/dDE good obsevations in uas
    covn : array of float
        covariance between dRA and dDE good obsevations in uas^2
    RAn/DEn : array of float
        Right ascension/Declination good obsevations in radian
    """

    dRAn = dRA[ind_good]
    dDEn = dDE[ind_good]
    e_dRAn = e_dRA[ind_good]
    e_dDEn = e_dDE[ind_good]
    RAn = RA[ind_good]
    DEn = DE[ind_good]

    if cov is None:
        covn = None
    else:
        covn = cov[ind_good]

    return dRAn, dDEn, e_dRAn, e_dDEn, covn, RAn, DEn


# ----------------------------------------------------
def jac_mat_deg01(RA, DE, fit_type="full"):
    """Generate the Jacobian matrix of 1st VSH function.

    Parameters
    ----------
    RA : array of float
        right ascension in radian
    DE : array of float
        declination in radian
    fit_type : string
        flag to determine which parameters to be fitted
        "full" for full 6 parameters
        "rotation" for only 3 rotation parameters
        "glide" for only 3 glide parameters

    Returns
    ----------
    JacMat/JacMatT : matrix
        Jacobian matrix and its transpose matrix
    """

    # Partial array dRA and dDE, respectively.
    if fit_type == "full":
        # For RA
        # glide
        par1_d1 = -sin(RA)
        par1_d2 = cos(RA)
        par1_d3 = np.zeros_like(RA)
        # rotation
        par1_r1 = -cos(RA) * sin(DE)
        par1_r2 = -sin(RA) * sin(DE)
        par1_r3 = cos(DE)

        # For DE
        # glide
        par2_d1 = -cos(RA) * sin(DE)
        par2_d2 = -sin(RA) * sin(DE)
        par2_d3 = cos(DE)
        # rotation
        par2_r1 = sin(RA)
        par2_r2 = -cos(RA)
        par2_r3 = np.zeros_like(RA)

        # (dRA, dDE).
        pard1 = concatenate((par1_d1, par2_d1), axis=0)
        pard2 = concatenate((par1_d2, par2_d2), axis=0)
        pard3 = concatenate((par1_d3, par2_d3), axis=0)
        parr1 = concatenate((par1_r1, par2_r1), axis=0)
        parr2 = concatenate((par1_r2, par2_r2), axis=0)
        parr3 = concatenate((par1_r3, par2_r3), axis=0)

        # transpose of Jacobian matrix.
        # JacMatT = np.vstack((pard1, pard2, pard3,
        #                      parr1, parr2, parr3))
        N = pard1.size
        JacMatT = concatenate(
            (pard1.reshape(1, N), pard2.reshape(1, N), pard3.reshape(1, N),
             parr1.reshape(1, N), parr2.reshape(1, N), parr3.reshape(1, N)),
            axis=0)

    elif fit_type == "rotation":
        # For RA
        par1_r1 = -cos(RA) * sin(DE)
        par1_r2 = -sin(RA) * sin(DE)
        par1_r3 = cos(DE)

        # For DE
        par2_r1 = sin(RA)
        par2_r2 = -cos(RA)
        par2_r3 = np.zeros_like(RA)

        # (dRA, dDE).
        parr1 = concatenate((par1_r1, par2_r1), axis=0)
        parr2 = concatenate((par1_r2, par2_r2), axis=0)
        parr3 = concatenate((par1_r3, par2_r3), axis=0)

        # transpose of Jacobian matrix.
        N = parr1.size
        JacMatT = concatenate(
            (parr1.reshape(1, N), parr2.reshape(1, N), parr3.reshape(1, N)),
            axis=0)

    elif fit_type == "glide":
        # For RA
        par1_d1 = -sin(RA)
        par1_d2 = cos(RA)
        par1_d3 = np.zeros_like(RA)

        # For DE
        par2_d1 = -cos(RA) * sin(DE)
        par2_d2 = -sin(RA) * sin(DE)
        par2_d3 = cos(DE)

        # (dRA, dDE).
        pard1 = concatenate((par1_d1, par2_d1), axis=0)
        pard2 = concatenate((par1_d2, par2_d2), axis=0)
        pard3 = concatenate((par1_d3, par2_d3), axis=0)

        # transpose of Jacobian matrix.
        # JacMatT = np.vstack((pard1, pard2, pard3))
        N = pard1.size
        JacMatT = concatenate(
            (pard1.reshape(1, N), pard2.reshape(1, N), pard3.reshape(1, N)),
            axis=0)

    else:
        print("Error in the fit_type parameter.")
        sys.exit(1)

    # Jacobian matrix.
    JacMat = np.transpose(JacMatT)

    return JacMat, JacMatT


# ----------------------------------------------------
def jac_mat_deg02(RA, DE, fit_type="full"):
    """Generate the Jacobian matrix

    Parameters
    ----------
    RA : array of float
        right ascension in radian
    DE : array of float
        declination in radian

    Returns
    ----------
    jacMat/jacMatT : matrix
        Jacobian matrix and its transpose matrix
    """

    # Partial array dRA and dDE, respectively.
    # For RA
    # glide
    par1_11ER = -sin(RA)
    par1_11EI = cos(RA)  # a_{1,-1}^E
    par1_10E = np.zeros_like(RA)
    # rotation
    par1_11MR = -cos(RA) * sin(DE)
    par1_11MI = -sin(RA) * sin(DE)  # a_{1,-1}^M
    par1_10M = cos(DE)

    # quadrupole
    par1_22ER = -2 * sin(2 * RA) * cos(DE)
    par1_22EI = -2 * cos(2 * RA) * cos(DE)
    par1_21ER = sin(RA) * sin(DE)
    par1_21EI = cos(RA) * sin(DE)
    par1_20E = np.zeros_like(RA)
    par1_22MR = -cos(2 * RA) * sin(2 * DE)
    par1_22MI = sin(2 * RA) * sin(2 * DE)
    par1_21MR = -cos(RA) * cos(2 * DE)
    par1_21MI = sin(RA) * cos(2 * DE)
    par1_20M = sin(2 * DE)

    # For DE
    # glide
    par2_11ER = par1_11MR
    par2_11EI = par1_11MI
    par2_10E = par1_10M
    # rotation
    par2_11MR = -par1_11ER
    par2_11MI = -par1_11EI
    par2_10M = -par1_10E

    # quadrupole
    par2_22ER = par1_22MR
    par2_22EI = par1_22MI
    par2_21ER = par1_21MR
    par2_21EI = par1_21MI
    par2_20E = par1_20M
    par2_22MR = -par1_22ER
    par2_22MI = -par1_22EI
    par2_21MR = -par1_21ER
    par2_21MI = -par1_21EI
    par2_20M = -par1_20E

    if fit_type == "full":
        # (dRA, dDE).
        # glide
        par11ER = concatenate((par1_11ER, par2_11ER), axis=0)
        par11EI = concatenate((par1_11EI, par2_11EI), axis=0)
        par10E = concatenate((par1_10E, par2_10E), axis=0)
        # rotation
        par11MR = concatenate((par1_11MR, par2_11MR), axis=0)
        par11MI = concatenate((par1_11MI, par2_11MI), axis=0)
        par10M = concatenate((par1_10M, par2_10M), axis=0)
        # quadrupole
        par22ER = concatenate((par1_22ER, par2_22ER), axis=0)
        par22EI = concatenate((par1_22EI, par2_22EI), axis=0)
        par21ER = concatenate((par1_21ER, par2_21ER), axis=0)
        par21EI = concatenate((par1_21EI, par2_21EI), axis=0)
        par20E = concatenate((par1_20E, par2_20E), axis=0)
        par22MR = concatenate((par1_22MR, par2_22MR), axis=0)
        par22MI = concatenate((par1_22MI, par2_22MI), axis=0)
        par21MR = concatenate((par1_21MR, par2_21MR), axis=0)
        par21MI = concatenate((par1_21MI, par2_21MI), axis=0)
        par20M = concatenate((par1_20M, par2_20M), axis=0)

        N = par11ER.size
        jacMatT = concatenate((
            # dipole glide
            par11ER.reshape(1, N), par11EI.reshape(1, N), par10E.reshape(1, N),
            # dipole rotation
            par11MR.reshape(1, N), par11MI.reshape(1, N), par10M.reshape(1, N),
            # quadrupole
            par22ER.reshape(1, N),
            par22EI.reshape(1, N), par21ER.reshape(1, N),
            par21EI.reshape(1, N), par20E.reshape(1, N),
            par22MR.reshape(1, N),
            par22MI.reshape(1, N), par21MR.reshape(1, N),
            par21MI.reshape(1, N), par20M.reshape(1, N)), axis=0)

    elif fit_type == "rotation":
        # (dRA, dDE).
        # rotation
        par11MR = concatenate((par1_11MR, par2_11MR), axis=0)
        par11MI = concatenate((par1_11MI, par2_11MI), axis=0)
        par10M = concatenate((par1_10M, par2_10M), axis=0)

        # quadrupole
        par22MR = concatenate((par1_22MR, par2_22MR), axis=0)
        par22MI = concatenate((par1_22MI, par2_22MI), axis=0)
        par21MR = concatenate((par1_21MR, par2_21MR), axis=0)
        par21MI = concatenate((par1_21MI, par2_21MI), axis=0)
        par20M = concatenate((par1_20M, par2_20M), axis=0)

        N = par11MR.size
        jacMatT = concatenate((
            # dipole rotation
            par11MR.reshape(1, N), par11MI.reshape(1, N), par10M.reshape(1, N),
            # quadrupole
            par22MR.reshape(1, N),
            par22MI.reshape(1, N), par21MR.reshape(1, N),
            par21MI.reshape(1, N), par20M.reshape(1, N)), axis=0)

    elif fit_type == "glide":
        # (dRA, dDE).
        # glide
        par11ER = concatenate((par1_11ER, par2_11ER), axis=0)
        par11EI = concatenate((par1_11EI, par2_11EI), axis=0)
        par10E = concatenate((par1_10E, par2_10E), axis=0)

        # quadrupole
        par22ER = concatenate((par1_22ER, par2_22ER), axis=0)
        par22EI = concatenate((par1_22EI, par2_22EI), axis=0)
        par21ER = concatenate((par1_21ER, par2_21ER), axis=0)
        par21EI = concatenate((par1_21EI, par2_21EI), axis=0)
        par20E = concatenate((par1_20E, par2_20E), axis=0)

        N = par11ER.size
        jacMatT = concatenate((
            # glide
            par11ER.reshape(1, N), par11EI.reshape(1, N), par10E.reshape(1, N),
            # quadrupole
            par22ER.reshape(1, N),
            par22EI.reshape(1, N), par21ER.reshape(1, N),
            par21EI.reshape(1, N), par20E.reshape(1, N)), axis=0)

    else:
        print("Error in the fit_type parameter.")
        sys.exit(1)

    # Jacobian matrix.
    jacMat = np.transpose(jacMatT)

    return jacMat, jacMatT


# ---------------------------------------------------
def vsh_func01(ra, dec, param, fit_type="full"):
    # r1, r2, r3, g1, g2, g3):
    """VSH function of the first degree.

    Parameters
    ----------
    ra/dec : array of float
        Right ascension/Declination in radian
    param :
        r1, r2, r3 : float
            rotation parameters
        g1, g2, g3 : float
            glide parameters
    fit_type : string
        flag to determine which parameters to be fitted
        "full" for full 6 parameters
        "rotation" for only 3 rotation parameters
        "glide" for only 3 glide parameters

    Returns
    ----------
    dra/ddec : array of float
        R.A.(*cos(Dec.))/Dec. differences in uas
    """

    if fit_type == "full":
        g1, g2, g3, r1, r2, r3 = param
        dra = [-r1 * cos(ra) * sin(dec) - r2 * sin(ra) * sin(dec) +
               r3 * cos(dec) -
               g1 * sin(ra) + g2 * cos(ra)][0]
        ddec = [+ r1 * sin(ra) - r2 * cos(ra) -
                g1 * cos(ra) * sin(dec) - g2 * sin(ra) * sin(dec) +
                g3 * cos(dec)][0]
    elif fit_type == "rotation":
        r1, r2, r3 = param
        dra = [-r1 * cos(ra) * sin(dec) - r2 * sin(ra) * sin(dec) +
               r3 * cos(dec)][0]
        ddec = [+ r1 * sin(ra) - r2 * cos(ra)][0]
    elif fit_type == "glide":
        g1, g2, g3 = param
        dra = [- g1 * sin(ra) + g2 * cos(ra)][0]
        ddec = [- g1 * cos(ra) * sin(dec) - g2 * sin(ra) * sin(dec) +
                g3 * cos(dec)][0]
    else:
        print("ERROR in parameter fit_type(function 'vsh_func01')!")
        exit()
    return dra, ddec


# ---------------------------------------------------
def vsh02_calc(ra, dec, param, fit_type="full"):
    """VSH function of the second degree.

    Parameters
    ----------
    ra/dec : array of float
        Right ascension/Declination in radian
    E_20, ER_21, EI_21, ER_22, EI_22 : float
        quadrupolar parameters of electric type
    M_20, MR_21, MI_21, MR_22, MI_22 : float
        quadrupolar parameters of magnetic type

    Returns
    ----------
    dra/ddec : array of float
        R.A.(*cos(Dec.))/Dec. differences in uas
    """

    if fit_type == "full":
        [ER_22, EI_22, ER_21, EI_21, E_20, MR_22,
            MI_22, MR_21, MI_21, M_20] = param
        dra = [+M_20 * sin(2 * dec) -
               (MR_21 * cos(ra) - MI_21 * sin(ra)) * cos(2 * dec) +
               (ER_21 * sin(ra) + EI_21 * cos(ra)) * sin(dec) -
               (MR_22 * cos(2 * ra) - MI_22 * sin(2 * ra)) * sin(2 * dec) -
               2 * (ER_22 * sin(2 * ra) + EI_22 * cos(2 * ra)) * cos(dec)][0]
        ddec = [+E_20 * sin(2 * dec) -
                (MR_21 * sin(ra) + MI_21 * cos(ra)) * sin(dec) -
                (ER_21 * cos(ra) - EI_21 * sin(ra)) * cos(2 * dec) +
                2 * (MR_22 * sin(2 * ra) + MI_22 * cos(2 * ra)) * cos(dec) -
                (ER_22 * cos(2 * ra) - EI_22 * sin(2 * ra)) * sin(2 * dec)][0]
    elif fit_type == "glide":
        [ER_22, EI_22, ER_21, EI_21, E_20] = param
        dra = [+ (ER_21 * sin(ra) + EI_21 * cos(ra)) * sin(dec) -
               2 * (ER_22 * sin(2 * ra) + EI_22 * cos(2 * ra)) * cos(dec)][0]
        ddec = [+E_20 * sin(2 * dec) -
                (ER_21 * cos(ra) - EI_21 * sin(ra)) * cos(2 * dec) -
                (ER_22 * cos(2 * ra) - EI_22 * sin(2 * ra)) * sin(2 * dec)][0]
    elif fit_type == "rotation":
        [MR_22, MI_22, MR_21, MI_21, M_20] = param
        dra = [+M_20 * sin(2 * dec) -
               (MR_21 * cos(ra) - MI_21 * sin(ra)) * cos(2 * dec) -
               (MR_22 * cos(2 * ra) - MI_22 * sin(2 * ra)) * sin(2 * dec)][0]
        ddec = [- (MR_21 * sin(ra) + MI_21 * cos(ra)) * sin(dec) +
                2 * (MR_22 * sin(2 * ra) + MI_22 * cos(2 * ra)) * cos(dec)][0]
    else:
        print("ERROR in parameter fit_type(function 'vsh_func01')!")
        exit()
    return dra, ddec


# ---------------------------------------------------
def vsh_func02(ra, dec, param, fit_type):
    """VSH function of the second degree.

    Parameters
    ----------
    ra/dec : array of float
        Right ascension/Declination in radian
    param : array of float
        estimation of rotation, glide, and quadrupolar parameters

    Returns
    ----------
    dra/ddec : array of float
        R.A.(*cos(Dec.))/Dec. differences in uas
    """

    dra1, ddec1 = vsh_func01(ra, dec, param[:6], fit_type)
    dra2, ddec2 = vsh02_calc(ra, dec, param[6:], fit_type)

    return dra1 + dra2, ddec1 + ddec2


# ----------------------------------------------------
def wgt_mat(e_dRA, e_dDE, cov=None):
    """Generate the weighted matrix.

    Parameters
    ----------
    e_dRA/e_dDE : array of float
        formal uncertainty of dRA(*cos(DE))/dDE in uas
    cov : array of float
        covariance between dRA and dDE in uas^2, default is None

    Returns
    ----------
    wgt : matrix
        weighted matrix used in the least squares fitting.
    """

    err = np.concatenate((e_dRA, e_dDE), axis=0)

    # Covariance matrix.
    covmat = np.diag(err**2)

    if cov is not None:
        # Take the correlation into consideration.
        num = e_dRA.size
        for i, C in enumerate(cov):
            covmat[i, i + num] = C
            covmat[i + num, i] = C

    # Inverse it to obtain weighted matrix.
    wgt = np.linalg.inv(covmat)

    return wgt


# ---------------------------------------------------
def normal_matrix_calc(dRA, dDE, e_dRA, e_dDE, RA, DE,
                       cov=None, fit_type="full", jac_func=None):
    """Calculate the normal matrix

    Parameters
    ----------
    dRA/dDE : array of float
        R.A.(*cos(Dec.))/Dec. differences in uas
    e_dRA/e_dDE : array of float
        formal uncertainty of dRA(*cos(DE))/dDE in uas
    RA/DE : array of float
        Right ascension/Declination in radian
    cov : array of float
        covariance between dRA and dDE in uas^2, default is None
    fit_type : string
        flag to determine which parameters to be fitted
        "full" for full 6 parameters
        "rotation" for only 3 rotation parameters
        "glide" for only 3 glide parameters

    Returns
    ----------
    A : array of float
        normal matrix
    b : array of float
        observational matrix
    """

    # print("normal_matrix_calc")
    # print(cov, cov.shape)

    if jac_func is None:
        print("The function of calculating the Jacobian matrix should be given!")
        sys.exit(1)

    # Jacobian matrix and its transpose.
    JacMat, JacMatT = jac_func(RA, DE, fit_type)

    # Weighted matrix.
    WgtMat = wgt_mat(e_dRA, e_dDE, cov)

    # Calculate matrix A and b of matrix equation:
    # A * x = b.
    A = np.dot(np.dot(JacMatT, WgtMat), JacMat)

    dPos = np.concatenate((dRA, dDE), axis=0)
    b = np.dot(np.dot(JacMatT, WgtMat), dPos)

    return A, b


# ---------------------------------------------------
def residual_calc(dRA, dDE, RA, DE, param, fit_type="full", l_max=1):
    """Calculate the residuals of RA/Dec

    Parameters
    ----------
    dRA/dDE : array of float
        R.A.(*cos(Dec.))/Dec. differences in uas
    RA/DE : array of float
        Right ascension/Declination in radian
    param : array of float
        estimation of rotation and glide parameters
    fit_type : string
        flag to determine which parameters to be fitted
        "full" for full 6 parameters
        "rotation" for only 3 rotation parameters
        "glide" for only 3 glide parameters

    Returns
    ----------
    ResRA/ResDE : array of float
        residual array of dRA(*cos(Dec))/dDec in uas.
    """

    if l_max == 1:
        vsh_func = vsh_func01
    elif l_max == 2:
        vsh_func = vsh_func02
    else:
        print("Sorry l_max >= 2 is mot supported here.")
        sys.exit(1)

    # Theoritical value
    dra, ddec = vsh_func(RA, DE, param, fit_type)

    # Calculate the residual. ( O - C )
    ResRA, ResDE = dRA - dra, dDE - ddec

    return ResRA, ResDE


# ---------------------------------------------------
def vsh_solve(dRA, dDE, e_dRA, e_dDE, RA, DE, cov=None, fit_type="full", l_max=1):
    # ), max_num=int(1e3)):
    """The 1st degree of VSH function: glide and rotation.

    Parameters
    ----------
    dRA/dDE : array of float
        R.A.(*cos(Dec.))/Dec. differences in uas
    e_dRA/e_dDE : array of float
        formal uncertainty of dRA(*cos(DE))/dDE in uas
    RA/DE : array of float
        Right ascension/Declination in radian
    cov : array of float
        covariance between dRA and dDE in uas^2, default is None
    fit_type : string
        flag to determine which parameters to be fitted
        "full" for full 6/16 parameters
        "rotation" for only 3/8 rotation parameters
        "glide" for only 3/8 glide parameters

    Returns
    ----------
    x : array of float
        estimation of x
        l_max = 1
        x = (d1, d2, d3, r1, r2, r3)
        l_max = 2
        x = (d1, d2, d3, r1, r2, r3,
             ER_22, EI_22, ER_21, EI_21, E_20,
             MR_22, MI_22, MR_21, MI_21, M_20)
    sig : array of float
        uncertainty of x in uas
    corr_mat : matrix
        matrix of correlation coefficient.
    """

    # Maxium number of calculation the matrix
    max_num = 1000

    if l_max == 1:
        jac_mat_func = jac_mat_deg01
    elif l_max == 2:
        jac_mat_func = jac_mat_deg02
    else:
        print("Sorry l_max >= 2 is mot supported here.")
        sys.exit(1)

    if dRA.size > max_num:
        div = dRA.size // max_num
        rem = dRA.size % max_num

        if cov is None:
            A, b = normal_matrix_calc(dRA[:rem], dDE[:rem],
                                      e_dRA[:rem], e_dDE[:rem],
                                      RA[:rem], DE[:rem],
                                      cov, fit_type, jac_mat_func)
        else:
            A, b = normal_matrix_calc(dRA[:rem], dDE[:rem],
                                      e_dRA[:rem], e_dDE[:rem],
                                      RA[:rem], DE[:rem],
                                      cov[:rem], fit_type, jac_mat_func)

        for i in range(div):
            ista = rem + i * max_num
            iend = ista + max_num

            if cov is None:
                An, bn = normal_matrix_calc(dRA[ista:iend], dDE[ista:iend],
                                            e_dRA[ista:iend], e_dDE[ista:iend],
                                            RA[ista:iend], DE[ista:iend],
                                            cov, fit_type, jac_mat_func)
            else:
                An, bn = normal_matrix_calc(dRA[ista:iend], dDE[ista:iend],
                                            e_dRA[ista:iend], e_dDE[ista:iend],
                                            RA[ista:iend], DE[ista:iend],
                                            cov[ista:iend], fit_type, jac_mat_func)
            A = A + An
            b = b + bn
    else:

        A, b = normal_matrix_calc(dRA, dDE, e_dRA, e_dDE, RA, DE,
                                  cov, fit_type, jac_mat_func)

    # Solve the equations.
    """Components of estimation
    fit_type     |           x
    "full"       |(d1, d2, d3, r1, r2, r3)
    "rotation"   |      (r1, r2, r3)
    "glide"      |      (d1, d2, d3)
    """
    x = np.linalg.solve(A, b)

    # Covariance.
    pcov = np.linalg.inv(A)
    sig = np.sqrt(pcov.diagonal())

    # Correlation coefficient.
    corr_mat = np.array([pcov[i, j] / sig[i] / sig[j]
                         for j in range(len(x))
                         for i in range(len(x))])
    corr_mat.resize((len(x), len(x)))

    # Return the result.
    return x, sig, corr_mat


# ----------------------------------------------------
def vsh_fit(dRA, dDE, RA, DE, e_dRA=None, e_dDE=None, cov=None, flog=None,
            elim_flag="sigma", N=3.0, ang_sep=None, X=None, fit_type="full",
            return_aux=False, l_max=1):
    """First two degrees vsh fitting.

    Parameters
    ----------
    dRA/dDE : array of float
        R.A.(*cos(Dec.))/Dec. differences in uas
    e_dRA/e_dDE : array of float
        formal uncertainty of dRA(*cos(DE))/dDE in uas
    RA/DE : array of float
        Right ascension/Declination in radian
    flog :
        handlings of output file. If None, print to the screen
    cov : array of float
        covariance between dRA and dDE in uas^2, default is None
    elim_flag : string
        "sigma" uses n-sigma principle
        "angsep" uses angular seperation as the criteria
        "norsep" uses normalized seperation as the criteria
        "nor_ang" uses both normalized and angular seperation as the criteria
        "None" or "none" doesn't use any criteria
    N : float
        N-sigma principle for eliminating the outliers
        or
        Maximum seperation
    fit_type : string
        flag to determine which parameters to be fitted
        "full" for full 6 parameters
        "rotation" for only 3 rotation parameters
        "glide" for only 3 glide parameters
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
    """

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
        print("# apriori reduced Chi-square for: %10.3f" % apr_chi2, file=flog)

    # Now we can use different criteria of elimination.
    if elim_flag is None or elim_flag is "None":
        x, sig, cofmat = vsh_solve(dRA, dDE, e_dRA, e_dDE, RA, DE, cov,
                                   fit_type, l_max)
        # fit_type, max_num)
        ind_good = np.arange(dRA.size)

    elif elim_flag is "sigma":
        x, sig, cofmat = vsh_solve(dRA, dDE, e_dRA, e_dDE, RA, DE,
                                   cov, fit_type, l_max)
        # Iteration.
        num1 = 1
        num2 = 0
        while(num1 != num2):
            num1 = num2

            # Calculate the residual. ( O - C )
            rRA, rDE = residual_cal(dRA, dDE, RA, DE, x, fit_type, l_max)
            ind_good = elim_nsigma(rRA, rDE, N)
            num2 = dRA.size - ind_good.size

            dRAn, dDEn, e_dRAn, e_dDEn, covn, RAn, DEn = find_good_obs(
                dRA, dDE, e_dRA, e_dDE, cov, RA, DE, ind_good)
            # [dRAn, dDEn, e_dRAn, e_dDEn] = [np.take(dRA, ind_good),
            #                                 np.take(dDE, ind_good),
            #                                 np.take(e_dRA, ind_good),
            #                                 np.take(e_dDE, ind_good)]
            # covn = np.take(cov, ind_good)
            # RAn, DEn = np.take(RA, ind_good), np.take(DE, ind_good)

            xn, sign, cofmatn = vsh_solve(dRAn, dDEn, e_dRAn, e_dDEn,
                                          RAn, DEn, covn, fit_type, l_max)

            x, sig, cofmat = xn, sign, cofmatn

            if flog is not None:
                print("# Number of sample: %d" % (dRA.size - num2),
                      file=flog)
    else:
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
            print("ERROR: elim_flag can only be sigma, angsep, or norsep!")
            exit()

        # Find all good observations
        dRAn, dDEn, e_dRAn, e_dDEn, covn, RAn, DEn = find_good_obs(
            dRA, dDE, e_dRA, e_dDE, cov, RA, DE, ind_good)
        x, sig, cofmat = vsh_solve(dRAn, dDEn, e_dRAn, e_dDEn, RAn, DEn,
                                   covn, fit_type, l_max)

        if flog is not None:
            print("# Number of sample: %d" % dRAn.size,
                  file=flog)

    full_true = np.ones(len(dRA), dtype=bool)
    mask_outl = (full_true & ind_good)
    ind_outl = np.arange(len(dRA))[mask_outl]

    dRAres, dDEres = residual_calc(dRA, dDE, RA, DE, x, fit_type, l_max)

    if flog is not None:
        # Calculate the posteriori wrms
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
    M = 6
    pos_chi2_rdc = calc_chi2_2d(dRAres, e_dRA, dDEres, e_dDE, cov,
                                reduced=True, num_fdm=2 * dRAres.size - 1 - M)
    if flog is not None:
        print("# posteriori reduced Chi-square for: %10.3f\n" %
              pos_chi2_rdc, file=flog)

    # Calculate the goodness-of-fit
    if flog is not None:
        pos_chi2 = calc_chi2_2d(dRAres, e_dRA, dDEres, e_dDE, cov)
        print("# goodness-of-fit is %10.3f\n" %
              calc_gof(2 * dRAres.size - 1 - M, pos_chi2), file=flog)

    # Rescale the formal errors
    sig = sig * np.sqrt(pos_chi2_rdc)

    # Return the result
    if return_aux:
        return x, sig, cofmat, ind_outl, dRAres, dDEres
    else:
        return x, sig, cofmat


def vsh_fit_4_table(data_tab, fit_type="full", return_aux=False, l_max=1):
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
    output_data = vsh_fit(dra, ddec, ra, dec, e_dRA=dra_err, e_dDE=ddec_err,
                          cov=dra_ddc_cov, elim_flag="nor_ang",
                          ang_sep=np.array(data_tab["ang_sep"]),
                          X=np.array(data_tab["nor_sep"]),
                          fit_type=fit_type, return_aux=return_aux,
                          l_max=l_max)

    output = {}
    output["pmt"] = output_data[0]
    output["sig"] = output_data[1]
    output["cor_mat"] = output_data[2]

    if return_aux:
        output["outlier_index"] = output_data[3]
        output["dra_residual"] = output_data[4]
        output["ddec_residual"] = output_data[5]

    return output


def vsh_fit_4_table_deg01(data_tab):
    """
    """

    output = vsh_fit_4_table(data_tab, l_max=1)

    return output


def vsh_fit_4_table_deg02(data_tab):
    """
    """

    output = vsh_fit_4_table(data_tab, l_max=2)

    return output


# ----------------------------------------------------
def test_code():
    """Code testing
    """

    # Check the result with Titov &Lambert (2013)
    # Log file.
    flog = open("../logs/Titov_Lambert2013_check_vsh01.log", "w")

    # Read data
    RAdeg, DEdeg, pmRA, pmDE, e_pmRA, e_pmDE = np.genfromtxt(
        "/Users/Neo/Astronomy/Works/201711_GDR2_ICRF3/data/list429.dat",
        usecols=range(2, 8), unpack=True)

    # degree -> rad
    RArad, DErad = np.deg2rad(RAdeg), np.deg2rad(DEdeg)
    cor = np.zeros_like(RArad)

    # Using VSH degree 01.
    print("VSH deg01:")
    w, sig, corrcoef, _, _, _ = vsh_deg01_fitting(
        pmRA, pmDE, e_pmRA, e_pmDE, cor, RArad, DErad,
        flog, elim_flag="None")
    print("Estimations: ")
    print("Dipole: ", w[:3])
    print("Rotation: ", w[3:])
    print("sigma: ", sig)
    print("correlation: ", corrcoef)
    flog.close()
    print("Done!")

    """
    Result in paper:
    glide:  (-0.4 + /- 0.7, -5.7 + /- 0.8, -2.8 + /- 0.9)
    rotation: -(-1.1 + /- 0.9, +1.4 + /- 0.8, +0.7 + /- 0.6)

    My result
    Estimations:
    Dipole:  [-0.42655902 - 5.74274308 - 2.7982711]
    Rotation:  [1.1286308 - 1.40004549 - 0.71103623]
    sigma:  [0.72724984 0.79054006 0.90500037
             0.93086674 0.84906682 0.64386228]

    # Same result
    """


if __name__ == "__main__":
    test_code()
# -------------------- END -----------------------------------
