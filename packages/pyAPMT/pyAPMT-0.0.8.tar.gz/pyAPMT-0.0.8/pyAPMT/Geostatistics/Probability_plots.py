# -*- coding: utf-8 -*-
"""

Module dedicated to Probability plots

"""

# Author: Sebastian Avalos <sebastian.avalos@apmodtech.com>
#         Advanced Predictive Modeling Technology
#         www.apmodtech.com/pyAPMT/
#         May-2022
#
# License: MIT License


# All submodules and packages
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import probscale
import logging
logging.getLogger().setLevel(logging.CRITICAL)

font = {'family' : 'DejaVu Sans',
        'size'   : 8}

matplotlib.rc('font', **font)
#sns.set()
np.set_printoptions(formatter={'float': lambda x: "{0:0.3f}".format(x)})



def ElementsInCategory(DF):
	'''Categorical elements as list on a selected column'''
	Cat = []
	for ii in DF:
		if ii not in Cat:
			Cat.append(ii)
	return Cat

def ExtractDataPerCategory(DF, Element, Category, V1):
	'''Extract subset of the drill hole database per category as numpy array'''
	SubSet1 = DF[DF[Category] == V1]
	V1_m = SubSet1[[Element]].to_numpy()
	return V1_m

def ProbabilityPlot(DH_DB, Dom, Var, CatLabel="X-axis", Label = "Label", \
             mSi = 2, markerscale=5, color="blue", Title="Title",\
             XMinMax = [0.01, 50], X_ticks = [0.01, 0.1, 1, 10, 50],\
             Axes=None, SubDom=None, Log_Scale=True):
	Num = len(SubDom)
	
	
	for ii in range(Num):
		tVec = ExtractDataPerCategory(DF=DH_DB, Element=Var, Category=Dom, V1=SubDom[ii])
		probscale.probplot(tVec, 
			             plottype='prob',
			             problabel='Standard Normal Probabilities',
			             #color = color,
			             weights = None,
			             probax = 'y', 
			             datalabel = None, 
			             scatter_kws = dict(marker='.', linestyle = 'none', \
			                                markersize = mSi),
			             ax = Axes,
			             label = Label+str(SubDom[ii]))


	Axes.grid(True, which="both") 
	Axes.set_xlim(left=XMinMax[0], right=XMinMax[1])
	if Log_Scale == True:
		Axes.set_xscale('log')
	Axes.set_xticks(X_ticks)
	Axes.xaxis.set_major_formatter(ticker.ScalarFormatter())
	Axes.set_ylim(bottom=0.01, top=99.99)
	Axes.set_title(Title)
	Axes.set_xlabel(CatLabel)
	#Axes.legend(loc='upper left', scatterpoints=50)
	Axes.legend(loc='lower right', markerscale=markerscale)

	Axes.grid(True)


	return None




