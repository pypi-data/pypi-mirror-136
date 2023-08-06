#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: T. Malfatti <malfatti@disroot.org>
@date: 20210614
@license: GNU GPLv3 <https://gitlab.com/malfatti/SciScripts/raw/master/LICENSE>
@homepage: https://gitlab.com/Malfatti/SciScripts
"""

print('[Analysis.DLC] Importing dependencies...')
import os
import pandas as pd
print('[Analysis.DLC] Done.')


def GetXYLh(File):
    Data = pd.read_hdf(File)
    BodyParts = Data.columns.get_level_values("bodyparts").unique().tolist()
    X, Y, Lh = Data.values.reshape((len(Data.index), -1, 3)).T
    X, Y, Lh = X.T, Y.T, Lh.T
    return(X,Y,Lh,BodyParts)


