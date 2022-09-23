# %% [markdown]
# This script will extract the time series of albedo at the site of AWSs. 

# shunan.feng@envs.au.dk (https://www.glacier-hub.com/)

# %%
import geemap
import ee
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import plotly.express as px

#%% map of aws sites
df = pd.read_excel("insitu_list.xlsx", sheet_name="awsList")


fig = plt.figure(figsize=(12, 8), edgecolor='w')
m = Basemap(projection='mill', resolution=None,
            llcrnrlat=-85, urcrnrlat=85,
            llcrnrlon=-180, urcrnrlon=180)
m.bluemarble(scale=0.5);     
m.scatter(df.Lon, df.Lat, latlon=True, label=df.Site)    
# draw parallels and meridians.
# label parallels on right and top
# meridians on bottom and left
parallels = np.arange(-90,90,30);
# labels = [left,right,top,bottom]
m.drawparallels(parallels,labels=[False,True,True,False], color="w");
meridians = np.arange(0,360,30);
m.drawmeridians(meridians,labels=[True,False,False,True], color="w");
#%%
df = pd.read_excel("insitu_list.xlsx", sheet_name="awsList")
fig = px.scatter_geo(df, lat="Lat", lon="Lon", color="Region",projection="natural earth")
fig.show()
# %%
awsLat = 28.23436667
awsLon = 85.62083333
date_start = '2018-11-28'
date_end = '2019-12-31'
pointValueFile = "Yala glacier.csv"

# %% [markdown]
# # GEE

# %%
Map = geemap.Map()
Map

# %% [markdown]
# ## Albedo

# %%
def addVisnirAlbedo(image):
    albedo = image.expression(
        '0.7963 * Blue + 2.2724 * Green - 3.8252 * Red + 1.4143 * NIR + 0.2053',
        {
            'Blue': image.select('Blue'),
            'Green': image.select('Green'),
            'Red': image.select('Red'),
            'NIR': image.select('NIR')
        }
    ).rename('visnirAlbedo')
    return image.addBands(albedo).copyProperties(image, ['system:time_start'])
''''if vis-nir bands albedo'''
rmaCoefficients = {
  'itcpsL7': ee.Image.constant([-0.0084, -0.0065, 0.0022, -0.0768]),
  'slopesL7': ee.Image.constant([1.1017, 1.0840, 1.0610, 1.2100]),
  'itcpsS2': ee.Image.constant([0.0210, 0.0167, 0.0155, -0.0693]),
  'slopesS2': ee.Image.constant([1.0849, 1.0590, 1.0759, 1.1583])
}; #rma
# rmaCoefficients = {
#   'itcpsL7': ee.Image.constant([-0.0084, -0.0065, 0.0022, -0.0768, -0.0314, -0.0022]),
#   'slopesL7': ee.Image.constant([1.1017, 1.0840, 1.0610, 1.2100, 1.2039, 1.2402]),
#   'itcpsS2': ee.Image.constant([0.0210, 0.0167, 0.0155, -0.0693, -0.0039, -0.0112]),
#   'slopesS2': ee.Image.constant([1.0849, 1.0590, 1.0759, 1.1583, 1.0479, 1.0148])
# }; #rma



# %%
# Function to get and rename bands of interest from OLI.
def renameOli(img):
  return img.select(
    ['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5'], #'QA_PIXEL', 'QA_RADSAT'
    ['Blue',  'Green', 'Red',   'NIR']) #'QA_PIXEL', 'QA_RADSAT'

# Function to get and rename bands of interest from ETM+, TM.
def renameEtm(img):
  return img.select(
    ['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4'], #,   'QA_PIXEL', 'QA_RADSAT'
    ['Blue',  'Green', 'Red',   'NIR']) #, 'QA_PIXEL', 'QA_RADSAT'

# Function to get and rename bands of interest from Sentinel 2.
def renameS2(img):
  return img.select(
    ['B2',   'B3',    'B4',  'B8',   'QA60', 'SCL'],
    ['Blue', 'Green', 'Red', 'NIR',  'QA60', 'SCL']
  )

def oli2oli(img):
  return img.select(['Blue', 'Green', 'Red', 'NIR']) \
    .toFloat()

def etm2oli(img):
  return img.select(['Blue', 'Green', 'Red', 'NIR']) \
    .multiply(rmaCoefficients["slopesL7"]) \
    .add(rmaCoefficients["itcpsL7"]) \
    .toFloat()
    # .round() \
    # .toShort() 
    # .addBands(img.select('pixel_qa'))

def s22oli(img):
  return img.select(['Blue', 'Green', 'Red', 'NIR']) \
    .multiply(rmaCoefficients["slopesS2"]) \
    .add(rmaCoefficients["itcpsS2"]) \
    .toFloat()
    # .round() \
    # .toShort() # convert to Int16
    # .addBands(img.select('pixel_qa'))

def imRangeFilter(image):
  maskMax = image.lt(1)
  maskMin = image.gt(0)
  return image.updateMask(maskMax).updateMask(maskMin)

'''
Cloud mask for Landsat data based on fmask (QA_PIXEL) and saturation mask 
based on QA_RADSAT.
Cloud mask and saturation mask by sen2cor.
Codes provided by GEE official. '''

# the Landsat 8 Collection 2
def maskL8sr(image):
  # Bit 0 - Fill
  # Bit 1 - Dilated Cloud
  # Bit 2 - Cirrus
  # Bit 3 - Cloud
  # Bit 4 - Cloud Shadow
  qaMask = image.select('QA_PIXEL').bitwiseAnd(int('11111', 2)).eq(0)
  saturationMask = image.select('QA_RADSAT').eq(0)

  # Apply the scaling factors to the appropriate bands.
  # opticalBands = image.select('SR_B.').multiply(0.0000275).add(-0.2)
  # thermalBands = image.select('ST_B.*').multiply(0.00341802).add(149.0)

  # Replace the original bands with the scaled ones and apply the masks.
  #image.addBands(opticalBands, {}, True) \ maybe not available in python api
  return image.select('SR_B.').multiply(0.0000275).add(-0.2) \
    .updateMask(qaMask) \
    .updateMask(saturationMask)

  
# the Landsat 4, 5, 7 Collection 2
def maskL457sr(image):
  # Bit 0 - Fill
  # Bit 1 - Dilated Cloud
  # Bit 2 - Unused
  # Bit 3 - Cloud
  # Bit 4 - Cloud Shadow
  qaMask = image.select('QA_PIXEL').bitwiseAnd(int('11111', 2)).eq(0)
  saturationMask = image.select('QA_RADSAT').eq(0)

  # Apply the scaling factors to the appropriate bands.
  # opticalBands = image.select('SR_B.')
  # opticalBands = image.select('SR_B.').multiply(0.0000275).add(-0.2)
  # thermalBand = image.select('ST_B6').multiply(0.00341802).add(149.0)

  # Replace the original bands with the scaled ones and apply the masks.
  return image.select('SR_B.').multiply(0.0000275).add(-0.2) \
      .updateMask(qaMask) \
      .updateMask(saturationMask)
 #
 # Function to mask clouds using the Sentinel-2 QA band
 # @param {ee.Image} image Sentinel-2 image
 # @return {ee.Image} cloud masked Sentinel-2 image
 #
def maskS2sr(image):
  qa = image.select('QA60')

  # Bits 10 and 11 are clouds and cirrus, respectively.
  cloudBitMask = 1 << 10
  cirrusBitMask = 1 << 11
  # Bits 1 is saturated or defective pixel
  not_saturated = image.select('SCL').neq(1)
  # Both flags should be set to zero, indicating clear conditions.
  mask = qa.bitwiseAnd(cloudBitMask).eq(0) \
      .And(qa.bitwiseAnd(cirrusBitMask).eq(0)) 

  return image.updateMask(mask).updateMask(not_saturated).divide(10000)


# %%
# Define function to prepare OLI images.
def prepOli(img):
  orig = img
  img = maskL8sr(img)
  img = renameOli(img)
  img = oli2oli(img)
  img = imRangeFilter(img)
  img = addVisnirAlbedo(img)
  return ee.Image(img.copyProperties(orig, orig.propertyNames()))

# Define function to prepare ETM+/TM images.
def prepEtm(img):
  orig = img
  img = maskL457sr(img)
  img = renameEtm(img)
  img = etm2oli(img)
  img = imRangeFilter(img)
  img = addVisnirAlbedo(img)
  return ee.Image(img.copyProperties(orig, orig.propertyNames()))

# Define function to prepare S2 images.
def prepS2(img):
  orig = img
  img = renameS2(img)
  img = maskS2sr(img)
  img = s22oli(img)
  img = imRangeFilter(img)
  img = addVisnirAlbedo(img)
  return ee.Image(img.copyProperties(orig, orig.propertyNames()).set('SATELLITE', 'SENTINEL_2'))


# %%
# https://developers.google.com/earth-engine/tutorials/community/intro-to-python-api-guiattard by https://github.com/guiattard
def ee_array_to_df(arr, list_of_bands):
    """Transforms client-side ee.Image.getRegion array to pandas.DataFrame."""
    df = pd.DataFrame(arr)

    # Rearrange the header.
    headers = df.iloc[0]
    df = pd.DataFrame(df.values[1:], columns=headers)

    # Remove rows without data inside.
    df = df[['longitude', 'latitude', 'time', *list_of_bands]].dropna()

    # Convert the data to numeric values.
    for band in list_of_bands:
        df[band] = pd.to_numeric(df[band], errors='coerce')

    # Convert the time field into a datetime.
    df['datetime'] = pd.to_datetime(df['time'], unit='ms')

    # Keep the columns of interest.
    df = df[['time','datetime',  *list_of_bands]]

    return df

# %%
aoi = ee.Geometry.Point(awsLon, awsLat)

# print(date_start)

# create filter for image collection
colFilter = ee.Filter.And(
    ee.Filter.geometry(aoi), # filterbounds not available on python api https://github.com/google/earthengine-api/issues/83
    ee.Filter.date(date_start, date_end)
    # ee.Filter.calendarRange(5, 9, 'month'),
    # ee.Filter.lt('CLOUD_COVER', 50)
)

s2colFilter =  ee.Filter.And(
    ee.Filter.geometry(aoi), # filterbounds not available on python api https://github.com/google/earthengine-api/issues/83
    ee.Filter.date(date_start, date_end),
    # ee.Filter.calendarRange(5, 9, 'month'),
    ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 50)
)

oliCol = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2') \
            .filter(colFilter) \
            .map(prepOli) \
            .select(['visnirAlbedo'])
etmCol = ee.ImageCollection('LANDSAT/LE07/C02/T1_L2') \
            .filter(colFilter) \
            .map(prepEtm) \
            .select(['visnirAlbedo'])
tmCol = ee.ImageCollection('LANDSAT/LT05/C02/T1_L2') \
            .filter(colFilter) \
            .map(prepEtm) \
            .select(['visnirAlbedo'])
tm4Col = ee.ImageCollection('LANDSAT/LT04/C02/T1_L2') \
            .filter(colFilter) \
            .map(prepEtm) \
            .select(['visnirAlbedo'])
s2Col = ee.ImageCollection('COPERNICUS/S2_SR') \
            .filter(s2colFilter) \
            .map(prepS2) \
            .select(['visnirAlbedo'])
# landsatCol = etmCol.merge(tmCol)
landsatCol = oliCol.merge(etmCol).merge(tmCol).merge(tm4Col)
multiSat = landsatCol.merge(s2Col).sort('system:time_start', True) # // Sort chronologically in descending order.




pointValue = multiSat.getRegion(aoi, 90).getInfo() # The number e.g. 500 is the buffer size
dfpoint = ee_array_to_df(pointValue, ['visnirAlbedo'])

dfpoint.to_csv(pointValueFile, mode='w', index=False, header=True)
# dfpoint.to_csv(pointValueFile, mode='a', index=False, header=False)

# %%



