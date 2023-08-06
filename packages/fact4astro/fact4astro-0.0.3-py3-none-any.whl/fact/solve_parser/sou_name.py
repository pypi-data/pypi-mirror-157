#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name: souname_xmatch.py
"""
Created on Thu Apr 26 15:55:00 2018

@author: Neo(liuniu@smail.nju.edu.cn)

Read radio source name from data list. Obsolete!
"""

from astropy.io import fits
from astropy import table
from astropy.table import Table
import numpy as np
import os
import time

# My modules
from .get_dir import get_aux_dir
# from get_dir import get_aux_dir


__all__ = ["get_souname"]


# -----------------------------  FUNCTIONS -----------------------------
def get_souname():
    """Read source names.

        Parameters
        ----------
        None

        Returns
        -------
        sou_name: table object
            different designations of radio source names
        """

    data_dir = get_aux_dir()
    data_fil = "{}/source.names".format(data_dir)

    # empty array to store data
    sou_name = Table.read(data_fil, format="ascii.fixed_width_no_header",
                          names=["ivs_name", "j2000_name",
                                 "iers_name", "class"],
                          col_starts=(0, 10, 22, 42),
                          col_ends=(8, 20, 30, 42))

    # Eliminate duplicate sources
    sou_name = table.unique(sou_name, keys="ivs_name")

# Fill the empty filed of IERS name by the IVS name
#     for i in sou_name["iers_name"].mask.nonzero()[0]:
#         sou_name[i]["iers_name"] = sou_name[i]["ivs_name"]

    return sou_name


def get_souname2():
    """Read source names.

        Parameters
        ----------
        None

        Returns
        -------
        sou_name: table object
            different designations of radio source names
        """

    data_dir = get_aux_dir()
    data_fil = "{}/IVS_SrcNamesTable.csv".format(data_dir)

    # empty array to store data
    sou_name = Table.read(data_fil, format="ascii.no_header",
                          names=["ivs_name", "j2000_name_long",
                                 "j2000_name", "iers_name"],
                          comment="#")

    return sou_name


def reform_ivsname():
    """Reformate the IVS name translation file
    """

    fip = open("aux_files/IVS_SrcNamesTable.txt", "r")
    fop = open("aux_files/IVS_SrcNamesTable.csv", "w")

    lines = fip.readlines()

    for line in lines:
        if line[0] == "#":
            continue

        ivs_name = line[0:8]
        j20_name1 = line[10:26]
        j20_name2 = line[30:38]

        if line[40] == "-" or line[40] == " ":
            b50_name = ivs_name
        else:
            b50_name = line[40:48]

        print("{:s},{:s},{:s},{:s}".format(
            ivs_name, j20_name1, j20_name2, b50_name),
            file=fop)

    fip.close()
    fop.close()


if __name__ == "__main__":
    reform_ivsname()
# --------------------------------- END --------------------------------
