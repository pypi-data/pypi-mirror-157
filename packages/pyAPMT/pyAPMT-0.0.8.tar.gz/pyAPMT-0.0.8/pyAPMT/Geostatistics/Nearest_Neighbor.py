# -*- coding: utf-8 -*-
"""

Module dedicated to Nearest Neighbor

"""

# Author: Sebastian Avalos <sebastian.avalos@apmodtech.com>
#         Advanced Predictive Modeling Technology
#         www.apmodtech.com/pyAPMT/
#         Jun-2022
#
# License: MIT License


# All submodules and packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from sklearn.neighbors import KNeighborsRegressor

def ComputeNearestNeighbor(db_DH, db_BH, VarBH, NNVar='NN'):
	
	BH_XYZ = db_BH.DB[[db_BH.East, db_BH.North, db_BH.Elevation, VarBH]].to_numpy()
	
	db_DH.DB[NNVar] = 0		
	DH_XYZ = db_DH.DB[[db_DH.East, db_DH.North, db_DH.Elevation, NNVar]].to_numpy()

	print("Computing the Nearest Neighbor")

	neigh = KNeighborsRegressor(n_neighbors=1)
	neigh.fit(BH_XYZ[:,:-1], BH_XYZ[:,-1])

	for ii in range(DH_XYZ.shape[0]):
		if ii%50000==0:
			print(ii,  " of", DH_XYZ.shape[0], " points")		
		BH_Point = DH_XYZ[ii,:3]
		BH_Point = BH_Point[np.newaxis,:]
		predValue = neigh.predict(BH_Point)
		DH_XYZ[ii, -1] = predValue[0]	
	
	db_DH.DB[NNVar] = pd.Series(DH_XYZ[:, -1] )

	print("... Done \n")

	return db_DH.DB