#!/usr/bin/env ipython
# -*- coding: utf-8 -*-
# File name: vsh_common_func.py
"""
Created on Fri Oct 22 09:49:57 2021

@author: Neo(niu.liu@nju.edu.cn)
"""

import numpy as np


def elim_nsigma(y1r, y2r, n=3.0, wgt_flag=False,
                y1_err=None, y2_err=None):
    '''An outlier elimination using n-sigma criteria.
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
    ind_go : array of int
        index of good observations
    '''

    if wgt_flag:
        # wrms
        # std1 = np.sqrt(np.sum(y1r**2 / y1_err**2) / np.sum(y1_err**-2))
        # std2 = np.sqrt(np.sum(y2r**2 / y2_err**2) / np.sum(y2_err**-2))
        indice1 = np.where(np.fabs(y1r) - n * y1_err <= 0)
        indice2 = np.where(np.fabs(y2r) - n * y2_err <= 0)
        # y = np.sqrt(y1r**2 + y2r ** 2)
        # y_err = np.sqrt(y1_err**2 + y2_err**2)
        # ind_go = np.where(y - n * y_err <= 0)[0]
    else:
        # rms
        std1 = np.sqrt(np.sum(y1r**2) / (y1r.size - 1))
        std2 = np.sqrt(np.sum(y2r**2) / (y2r.size - 1))

    # indice1 = np.where(np.fabs(y1r) - n * std1 <= 0)
    # indice2 = np.where(np.fabs(y2r) - n * std2 <= 0)
    ind_go = np.intersect1d(indice1, indice2)

    # return ind_go, std1, std2
    return ind_go


# ----------------------------------------------------
def elim_angsep(angsep, pho_max=10.0e3):
    '''An outlier elimiantion based optic-radio angular seperation.
    Parameters
    ----------
    ang_sep : array of float
        angular seperation, in micro-as
    pho_max : float
        accepted maximum angular seperation, default 10.0 mas
    Returns
    ----------
    ind_go : array of int
        index of good observations
    '''

    ind_go = np.where(angsep <= pho_max)

    return ind_go


# ----------------------------------------------------
def elim_norsep(X, X_max=10.0):
    '''A outlier elimiantion based the normalized optic-radio seperation.
    Parameters
    ----------
    X : array of float
        normalized separations, unit-less.
    X_max : float
        accepted maximum X, default 10.0
    Returns
    ----------
    ind_go : array of int
        index of good observations
    '''

    ind_go = np.where(X <= X_max)

    return ind_go


def find_good_obs(dRA, dDE, e_dRA, e_dDE, cov, RA, DE, ind_go):
    '''Find the good observations based on index.
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
    ind_go : array of int
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
    '''

    dRAn, dDEn, e_dRAn, e_dDEn = [np.take(dRA, ind_go),
                                  np.take(dDE, ind_go),
                                  np.take(e_dRA, ind_go),
                                  np.take(e_dDE, ind_go)]
    if cov is not None:
        covn = np.take(cov, ind_go)
    else:
        covn = None
    RAn, DEn = np.take(RA, ind_go), np.take(DE, ind_go)

    return dRAn, dDEn, e_dRAn, e_dDEn, covn, RAn, DEn


# ----------------------------------------------------
def wgt_mat(e_dRA, e_dDE, cov=None):
    '''Generate the weighted matrix.
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
    '''

    err = concatenate((e_dRA, e_dDE), axis=0)

    # Covariance matrix.
    covmat = np.diag(err**2)
    # print(covmat.shape)

    if cov is not None:
        # Take the correlation into consideration.
        num = e_dRA.size
        for i, covi in enumerate(cov):
            covmat[i, i + num] = covi
            covmat[i + num, i] = covi

    # Inverse it to obtain weighted matrix.
    wgt = np.linalg.inv(covmat)

    return wgt


# ---------------------------------------------------
def normal_matrix_calc(dRA, dDE, e_dRA, e_dDE, RA, DE,
                       cov=None):
    '''Calculate the normal matrix
    dRA/dDE : array of float
        R.A.(*cos(Dec.))/Dec. differences in uas
    e_dRA/e_dDE : array of float
        formal uncertainty of dRA(*cos(DE))/dDE in uas
    RA/DE : array of float
        Right ascension/Declination in radian
    cov : array of float
        covariance between dRA and dDE in uas^2, default is None
    Returns
    ----------
    A : array of float
        normal matrix
    b : array of float
        observational matrix
    '''

    # print("normal_matrix_calc")
    # print(cov, cov.shape)

    # Jacobian matrix and its transpose.
    # jacMat, jacMatT = jac_mat_deg02(RA, DE, fit_type)
    jacMat, jacMatT = jac_mat_deg02(RA, DE)

    # Weighted matrix.
    WgtMat = wgt_mat(e_dRA, e_dDE, cov)

    # Calculate matrix A and b of matrix equation:
    # A * x = b.
    mat_tmp = np.dot(jacMatT, WgtMat)
    A = np.dot(mat_tmp, jacMat)

    dPos = concatenate((dRA, dDE), axis=0)
    b = np.dot(mat_tmp,  dPos)

    return A, b
