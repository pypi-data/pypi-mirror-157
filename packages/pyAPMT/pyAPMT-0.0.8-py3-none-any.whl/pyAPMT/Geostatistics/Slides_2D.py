# -*- coding: utf-8 -*-
"""

Module dedicated to Slide visualization in 2D

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


def Plot2DSlides(dB, Var, scale_factor=5, BWidth = 20, cmap = "rainbow",\
                 Axes=None, East_lims = None, North_lims = None, Elev_lims = None,\
                 VMin = 0, VMax = None, East="midx", North="midy", Elevation="midz"):
	if East_lims != None and North_lims != None:
		tempDH = dB[(dB[East] > East_lims[0]) & (dB[East] < East_lims[1])]
		tempDH = tempDH[(tempDH[North] > North_lims[0]) & (tempDH[North] < North_lims[1])]	
	elif East_lims != None and North_lims == None:
		tempDH = dB[(dB[East] > East_lims[0]) & (dB[East] < East_lims[1])]
	elif East_lims == None and North_lims != None:
		tempDH = dB[(dB[North] > North_lims[0]) & (dB[North] < North_lims[1])]		
	else:
		tempDH = dB
	if VMax == None:
		VMax = np.max(tempDH[Var])
	
	Ctr_Down = [np.percentile(tempDH[Elevation], kk) for kk in [75, 50, 25]]
	Ctr_North = [np.percentile(tempDH[North], kk) for kk in [75, 50, 25]]
	Ctr_East = [np.percentile(tempDH[East], kk) for kk in [75, 50, 25]]

	for jj in range(3):
		Axes[00,jj].set_title("%s - Looking down - %s (m)"%(Var, np.around(Ctr_Down[jj], decimals=0)))
		tempDH_2 = tempDH[(tempDH[Elevation] > Ctr_Down[jj]-BWidth) & (tempDH[Elevation] < Ctr_Down[jj]+BWidth)]
		im =Axes[00,jj].scatter(tempDH_2[East], tempDH_2[North], s=1, c=tempDH_2[Var], cmap = cmap, vmin=VMin, vmax=VMax)
		divider = make_axes_locatable(Axes[0,jj])
		cax = divider.append_axes('right', size='5%', pad=0.05)
		plt.colorbar(im, cax=cax, orientation='vertical')			
		Axes[00,jj].set_xlabel("East (m)")
		Axes[00,jj].set_ylabel("North (m)")
		Axes[00,jj].set_xlim(East_lims)
		Axes[00,jj].set_ylim(North_lims)
	
	for jj in range(3):
		Axes[1,jj].set_title("%s - Looking North - %s (m)"%(Var, np.around(Ctr_North[jj], decimals=0)))
		tempDH_2 = tempDH[(tempDH[North] > Ctr_North[jj]-BWidth) & (tempDH[North] < Ctr_North[jj]+BWidth)]
		im = Axes[1,jj].scatter(tempDH_2[East], tempDH_2[Elevation], s=1, c=tempDH_2[Var], cmap = cmap, vmin=VMin, vmax=VMax)
		divider = make_axes_locatable(Axes[1,jj])
		cax = divider.append_axes('right', size='5%', pad=0.05)
		plt.colorbar(im, cax=cax, orientation='vertical')
		
		Axes[1,jj].set_xlabel("East (m)")
		Axes[1,jj].set_ylabel("Elevation (m)")
		Axes[1,jj].set_xlim(East_lims)
		Axes[1,jj].set_ylim(Elev_lims)
		
	for jj in range(3):
		Axes[2,jj].set_title("%s - Looking East - %s (m)"%(Var, np.around(Ctr_East[jj], decimals=0)))
		tempDH_2 = tempDH[(tempDH[East] > Ctr_East[jj]-BWidth) & (tempDH[East] < Ctr_East[jj]+BWidth)]
		im = Axes[2,jj].scatter(tempDH_2[North], tempDH_2[Elevation], s=1, c=tempDH_2[Var], cmap = cmap,  vmin=VMin, vmax=VMax)
		divider = make_axes_locatable(Axes[2,jj])
		cax = divider.append_axes('right', size='5%', pad=0.05)
		plt.colorbar(im, cax=cax, orientation='vertical')			
		Axes[2,jj].set_xlabel("North (m)")
		Axes[2,jj].set_ylabel("Elevation (m)")
		Axes[2,jj].set_xlim(North_lims)
		Axes[2,jj].set_ylim(Elev_lims)	
	
	return None
	


