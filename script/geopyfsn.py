# -*- coding: utf-8 -*-
"""
Created on Wed May 13 15:48:06 2020

@author: shunan feng
"""
import numpy as np
import rasterio
import glob
import os

def getxy(rasterfile):
  """
  getxy is used for getting the x and y coordinates of the rasterfile.
  
  Parameters
  ----------
  [rasterfile]: variable read by rasterio

  Returns
  -------
  [x,y]: the x, y coordinates of the input

  e.g.
  import rasterio 
  src = rasterio.open('image.tif')
  x, y = getxy(src)
  """
  rasterbound = rasterfile.bounds
  x = np.linspace(rasterbound.left, rasterbound.right, rasterfile.width)
  y = np.linspace(rasterbound.bottom, rasterbound.top, rasterfile.height)
  return x, y





def getBand(folderPath):
    """
    getBand is used for getting image exported from gee.
    
    Parameters
    ----------
    [folderPath]: variable read by rasterio
    Returns
    -------
    [b1,b2]: the target layer
    """
    # read images in the folder
    searchCriteria = "*.tif"
    globInput = os.path.join(folderPath, searchCriteria)
    tifList = glob.glob(globInput)

    b1 = np.array([], dtype=np.double)
    b2 = np.array([], dtype=np.double)

    for impath in tifList:
        src = rasterio.open(impath)
        band1 = src.read(1).reshape(-1)
        band2 = src.read(2).reshape(-1)

        index1 = (band1 > 0) & (band1 < 1) & (band2 > 0) & (band2 < 1)
        band1 = band1[index1]
        band2 = band2[index1]

        index2 = np.abs( (band2 - band1) / (band2 + band1) ) < 0.5
        band2 = band2[index2]
        band1 = band1[index2]

        if band1.size == 0:
            continue
        else:
            b1 = np.append(b1, band1)
            b2 = np.append(b2, band2)

    return b1, b2  

def getBandNoFilter(folderPath):
    """
    getBand is used for getting image exported from gee.
    
    Parameters
    ----------
    [folderPath]: variable read by rasterio
    Returns
    -------
    [b1,b2]: the target layer
    """
    # read images in the folder
    searchCriteria = "*.tif"
    globInput = os.path.join(folderPath, searchCriteria)
    tifList = glob.glob(globInput)

    b1 = np.array([])
    b2 = np.array([])

    for impath in tifList:
        src = rasterio.open(impath)
        band1 = src.read(1).reshape(-1)
        band2 = src.read(2).reshape(-1)

        # index1 = (band1 > 1) & (band1 < 0) & (band2 > 1) & (band2 < 0)
        # band1[index1] = np.nan
        # band2[index1] = np.nan

        # index2 = np.abs( (band2 - band1) / (band2 + band1) ) >= 0.5
        # band1[index2] = np.nan
        # band2[index2] = np.nan

        if band1.size == 0:
            continue
        else:
            b1 = np.append(b1, band1)
            b2 = np.append(b2, band2)

    return b1, b2      
