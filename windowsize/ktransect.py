# %%
import geemap
import ee
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# %% display map
Map = geemap.Map()
Map

'''
get a profile of the k-transect
'''
# %%
latLonImg = ee.Image.pixelLonLat()
greenlandmask = ee.Image('OSU/GIMP/2000_ICE_OCEAN_MASK') \
                   .select('ice_mask').eq(1) #'ice_mask', 'ocean_mask'
arcticDEM = ee.Image('UMN/PGC/ArcticDEM/V3/2m_mosaic').addBands(latLonImg)
arcticDEMgreenland = arcticDEM.updateMask(greenlandmask)
visPara = {'min': 0,  'max': 3000.0, 'palette': ['0d13d8', '60e1ff', 'ffffff']}
Map.addLayer(arcticDEMgreenland.select('elevation'), visPara, 'arctic dem')

# %% define k transect
ktransect = ee.Geometry.LineString(
    [[-50.1, 67.083333], [-48, 67.083333]]
)
Map.addLayer(ktransect, {}, 'ktransect')
Map.center_object(ktransect, zoom=8)

# %% get the elevation profile
elevTransect = arcticDEMgreenland.reduceRegion(**{
    'reducer': ee.Reducer.toList(),
    'geometry': ktransect,
    'scale': 10,
    'tileScale': 6
})
dfdem = pd.DataFrame(elevTransect.getInfo())
# %% plot the profile
sns.set_theme()
dfdem = dfdem.sort_values("longitude")
dfdem.plot.area(x="longitude", y='elevation')



# %%
'''
get the albedo profile
'''


date_start = ee.Date.fromYMD(2019,1,1)
date_end = ee.Date.fromYMD(2021,12,31)

# %%
rmaCoefficients = {
  'itcpsL7': ee.Image.constant([-0.0084, -0.0065, 0.0022, -0.0768, -0.0314, -0.0022]),
  'slopesL7': ee.Image.constant([1.1017, 1.0840, 1.0610, 1.2100, 1.2039, 1.2402]),
  'itcpsS2': ee.Image.constant([0.0210, 0.0167, 0.0155, -0.0693, -0.0039, -0.0112]),
  'slopesS2': ee.Image.constant([1.0849, 1.0590, 1.0759, 1.1583, 1.0479, 1.0148])
}; #rma

# %%
def addTotalAlbedo(image):
    albedo = image.expression(
        '0.8706 * Blue + 2.7889 * Green - 4.6727 * Red + 1.6917 * NIR + 0.0318 * SWIR1 - 0.5348 * SWIR2 + 0.2438',
        {
            'Blue': image.select('Blue'),
            'Green': image.select('Green'),
            'Red': image.select('Red'),
            'NIR': image.select('NIR'),
            'SWIR1': image.select('SWIR1'),
            'SWIR2': image.select('SWIR2')
        }
    ).rename('totalAlbedo')
    return image.addBands(albedo).copyProperties(image, ['system:time_start'])

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


# %%
''''if vis-nir bands albedo'''
rmaCoefficients = {
  'itcpsL7': ee.Image.constant([-0.0084, -0.0065, 0.0022, -0.0768]),
  'slopesL7': ee.Image.constant([1.1017, 1.0840, 1.0610, 1.2100]),
  'itcpsS2': ee.Image.constant([0.0210, 0.0167, 0.0155, -0.0693]),
  'slopesS2': ee.Image.constant([1.0849, 1.0590, 1.0759, 1.1583])
}; #rma
# Function to get and rename bands of interest from OLI.
def renameOli(img):
  return img.select(
    ['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'QA_PIXEL', 'QA_RADSAT'], #'QA_PIXEL', 'QA_RADSAT'
    ['Blue',  'Green', 'Red',   'NIR',   'QA_PIXEL', 'QA_RADSAT']) #'QA_PIXEL', 'QA_RADSAT'

# Function to get and rename bands of interest from ETM+, TM.
def renameEtm(img):
  return img.select(
    ['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'QA_PIXEL', 'QA_RADSAT'], #,   'QA_PIXEL', 'QA_RADSAT'
    ['Blue',  'Green', 'Red',   'NIR',   'QA_PIXEL', 'QA_RADSAT']) #, 'QA_PIXEL', 'QA_RADSAT'

# Function to get and rename bands of interest from Sentinel 2.
def renameS2(img):
  return img.select(
    ['B2',   'B3',    'B4',  'B8',  'QA60', 'SCL'],
    ['Blue', 'Green', 'Red', 'NIR', 'QA60', 'SCL']
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
  return image.select(['Blue', 'Green', 'Red', 'NIR']).multiply(0.0000275).add(-0.2) \
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
  return image.select(['Blue', 'Green', 'Red', 'NIR']).multiply(0.0000275).add(-0.2) \
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


# %% stddev 


def landsatStdDev(image):
    albedo = image.select('visnirAlbedo')
    std3 = albedo.reduceNeighborhood(**{
        'reducer': ee.Reducer.stdDev(),
        'kernel': ee.Kernel.square(3)
    }).rename('std3') # dummy
    std5 = albedo.reduceNeighborhood(**{
        'reducer': ee.Reducer.stdDev(),
        'kernel': ee.Kernel.square(5)
    }).rename('std5') # dummy
    std9 = albedo.reduceNeighborhood(**{
        'reducer': ee.Reducer.stdDev(),
        'kernel': ee.Kernel.square(3)
    }).rename('std9') # to match with s2
    std15 = albedo.reduceNeighborhood(**{
        'reducer': ee.Reducer.stdDev(),
        'kernel': ee.Kernel.square(5)
    }).rename('std15') # to match with s2
    return image.addBands([std3, std5, std9, std15])    

def s2StdDev(image):
    albedo = image.select('visnirAlbedo')
    std3 = albedo.reduceNeighborhood(**{
        'reducer': ee.Reducer.stdDev(),
        'kernel': ee.Kernel.square(3)
    }).rename('std3')
    std5 = albedo.reduceNeighborhood(**{
        'reducer': ee.Reducer.stdDev(),
        'kernel': ee.Kernel.square(5)
    }).rename('std5')
    std9 = albedo.reduceNeighborhood(**{
        'reducer': ee.Reducer.stdDev(),
        'kernel': ee.Kernel.square(9)
    }).rename('std9')
    std15 = albedo.reduceNeighborhood(**{
        'reducer': ee.Reducer.stdDev(),
        'kernel': ee.Kernel.square(15)
    }).rename('std15')
    return image.addBands([std3, std5, std9, std15])    

# %%
# Define function to prepare OLI images.
def prepOli(img):
  orig = img
  img = renameOli(img)
  img = maskL8sr(img)
  img = oli2oli(img)
  img = imRangeFilter(img)
  # img = addTotalAlbedo(img)
  img = addVisnirAlbedo(img)
  return ee.Image(img.copyProperties(orig, orig.propertyNames()))

# Define function to prepare ETM+/TM images.
def prepEtm(img):
  orig = img
  img = renameEtm(img)
  img = maskL457sr(img)
  img = etm2oli(img)
  img = imRangeFilter(img)
  # img = addTotalAlbedo(img)
  img = addVisnirAlbedo(img)
  return ee.Image(img.copyProperties(orig, orig.propertyNames()))

# Define function to prepare S2 images.
def prepS2(img):
  orig = img
  img = renameS2(img)
  img = maskS2sr(img)
  img = s22oli(img)
  img = imRangeFilter(img)
  # img = addTotalAlbedo(img)
  img = addVisnirAlbedo(img)
  return ee.Image(img.copyProperties(orig, orig.propertyNames()).set('SATELLITE', 'SENTINEL_2'))



# create filter for image collection
colFilter = ee.Filter.And(
    ee.Filter.geometry(ktransect), # filterbounds not available on python api https://github.com/google/earthengine-api/issues/83
    ee.Filter.date(date_start, date_end)
    # ee.Filter.calendarRange(5, 9, 'month'),
    # ee.Filter.lt('CLOUD_COVER', 50)
)

s2colFilter =  ee.Filter.And(
    ee.Filter.geometry(ktransect), # filterbounds not available on python api https://github.com/google/earthengine-api/issues/83
    ee.Filter.date(date_start, date_end),
    # ee.Filter.calendarRange(5, 9, 'month'),
    ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 50)
)

oliCol = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2') \
            .filter(colFilter) \
            .map(prepOli) \
            .select(['visnirAlbedo']) \
            .map(landsatStdDev) \
            .sort('system:time_start', True) 

s2Col = ee.ImageCollection('COPERNICUS/S2_SR') \
            .filter(s2colFilter) \
            .map(prepS2) \
            .select(['visnirAlbedo']) \
            .map(s2StdDev) \
            .sort('system:time_start', True) 

# %% transect values from 2019 to 2021
oliList = oliCol.toList(oliCol.size())
for i in range(oliCol.size().getInfo()):
  
  img = ee.Image(oliList.get(i)).addBands(latLonImg)
  transectMask = img.select('visnirAlbedo').gt(0) # keep only valid values
  transectDaily = img.updateMask(transectMask).reduceRegion(**{
  'reducer': ee.Reducer.toList(),
  'geometry': ktransect,
  'scale': 30,
  'tileScale': 6
  })
  df = pd.DataFrame(transectDaily.getInfo()).sort_values("longitude")

  df['time'] = img.get('system:time_start').getInfo()
  df['satellite'] = 'Landsat'

  print("This is the: %.0f Landsat image" % i)

  if i==0:
    df.to_csv("/data/shunan/github/Remote-Sensing-of-Albedo/windowsize/ktransect.csv", 
              mode='w', index=False, header=True)
  else:
    df.to_csv("/data/shunan/github/Remote-Sensing-of-Albedo/windowsize/ktransect.csv", 
              mode='a', index=False, header=False)

s2List = s2Col.toList(s2Col.size())
for i in range(s2Col.size().getInfo()):
  img = ee.Image(s2List.get(i)).addBands(latLonImg)
  transectMask = img.select('visnirAlbedo').gt(0) # keep only valid values
  transectDaily = img.updateMask(transectMask).reduceRegion(**{
  'reducer': ee.Reducer.toList(),
  'geometry': ktransect,
  'scale': 10,
  'tileScale': 6
  })
  df = pd.DataFrame(transectDaily.getInfo()).sort_values("longitude")
  
  df['time'] = img.get('system:time_start').getInfo()
  df['satellite'] = 'Sentinel2'
  print("This is the: %.0f S2 image" % i)

  df.to_csv("/data/shunan/github/Remote-Sensing-of-Albedo/windowsize/ktransect.csv", 
            mode='a', index=False, header=False)

# %%
