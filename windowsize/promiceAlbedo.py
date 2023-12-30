# %% [markdown]
# This notebook first displays the location of PROMICE AWSs and calculated the annual velocity based on the GPS record.
# Then it will extract the satellite pixel values.
# Results will be saved in csv files under the promice folder. 
# 
# 
# Users should change the size of spatial window when extracting the pixel values. 

# %%
import geemap
import ee
import pandas as pd
import utm
import numpy as np
import plotly.express as px

# %% [markdown]
# # PROMICE

# %%
df = pd.read_csv('/data/shunan/github/Remote-Sensing-of-Albedo/script/promice/promice.csv')
df['Longitude'] = df['Longitude'] * -1
df['velocity(m/y)'] = df['Longitude'] # just create a new column by copying longitude

# %%
i = 0
for station in df.Station:
    # url = df.iloc[i]['url']
    url = df.url[i]
    dfs = pd.read_table(url, sep=r'\s{1,}', engine='python')
    dfs = dfs[(dfs['Albedo_theta<70d'] > 0) & (dfs['LatitudeGPS_HDOP<1(degN)'] > 0) & (dfs['LatitudeGPS_HDOP<1(degN)'] >0)]
    dfs['LongitudeGPS_HDOP<1(degW)'] = dfs['LongitudeGPS_HDOP<1(degW)'] * -1
    lat = dfs['LatitudeGPS_HDOP<1(degN)']
    lon = dfs['LongitudeGPS_HDOP<1(degW)']
    utmx, utmy, utmzoneNum, utmzoneLetter = utm.from_latlon(lat.values, lon.values)
    dist = np.sqrt((utmx[0] - utmx[-1])**2 + (utmy[0] - utmy[-1])**2) / (dfs.DayOfCentury.tail(1).values - dfs.DayOfCentury.head(1).values) * 365
    df.at[i, 'velocity(m/y)'] = np.around(dist, 2)
    print('The station is: %s lat: %f, lon: %f' % (df.Station[i],  lat.mean(),  lon.mean()) )
    print("the annual average ice flow rate is %.2f m\N{DOT OPERATOR}a\u207B\N{SUPERSCRIPT ONE}" %dist)
    i += 1
    

# %%
fig = px.scatter_mapbox(df,
                     lat=df.Latitude,
                     lon=df.Longitude,
                    #  color="", # which column to use to set the color of markers
                     hover_name="Station",
                     hover_data=["m.a.s.l", "velocity(m/y)"],
                     zoom=2,
                     width=650,
                     height=500,
                     center=dict(
                         lat=72.603506,
                         lon=-41.352658
                     )) # column added to hover information)
# fig.update_layout(mapbox_style="stamen-terrain") 
# fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(
    mapbox_style="white-bg",
    mapbox_layers=[
        {
            "below": 'traces',
            "sourcetype": "raster",
            "sourceattribution": "United States Geological Survey",
            "source": [
                "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
            ]
        }
      ])
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})                    
fig.show()
# fig.write_html(r'C:\Users\au686295\Documents\GitHub\personal\shunan.feng\assets\interactive_figure\promice.html')


# %% [markdown]
# # GEE

# %%
Map = geemap.Map()
Map

# %% [markdown]
# ## Landsat and Sentinel 


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
for i in range(len(df.Station)):
    stationName = df.Station[i]
    url = df.url[i]
    url = df.url[i]
    dfall = pd.read_table(url, sep=r'\s{1,}', engine='python')
    dfs = dfall[['Year', 'MonthOfYear', 'DayOfMonth', 'Albedo_theta<70d', 'LatitudeGPS_HDOP<1(degN)', 'LongitudeGPS_HDOP<1(degW)']]
    dfs = dfs[(dfs['Albedo_theta<70d'] > 0)]
    dfs = dfs.replace(-999, np.nan)
    # dfs = dfs.interpolate(method='bfill')
    dfs['LatitudeGPS_HDOP<1(degN)'] = dfs['LatitudeGPS_HDOP<1(degN)'].interpolate(limit_direction='both')
    dfs['LongitudeGPS_HDOP<1(degW)'] = dfs['LongitudeGPS_HDOP<1(degW)'].interpolate(limit_direction='both')
    dfs['lat'] = dfs['LatitudeGPS_HDOP<1(degN)']
    dfs['lon'] = dfs['LongitudeGPS_HDOP<1(degW)'] * -1
    dfs['time'] = pd.to_datetime(dict(year=dfs.Year, month=dfs.MonthOfYear, day = dfs.DayOfMonth))
    # utmx, utmy, utmzoneNum, utmzoneLetter = utm.from_latlon(dfs.lat.values, dfs.lon.values)
    # dist = np.sqrt((utmx[0] - utmx[-1])**2 + (utmy[0] - utmy[-1])**2) / (dfs.Year.tail(1).values - dfs.Year.head(1).values)

    print('The station is: %s' %df.Station[i])
    print('start from: %s end on: %s' % (dfs.time.head(1).values, dfs.time.tail(1).values))
    # print("the annual average ice flow rate is %.2f m\N{DOT OPERATOR}a\u207B\N{SUPERSCRIPT ONE}" %dist)

    dfsYear = dfs.groupby(['Year']).mean() 
    dfsYear.reset_index(inplace=True)
    
    '''
    This part could help examine the annual ice velocity calculated from promice data.
    '''
    # for j in range(len(dfsYear)):
    #     # aoi = ee.Geometry.Point([dfsYear.lon[i], dfsYear.lat[i]]).buffer(300)
    #     # Map.addLayer(aoi, {}, str(dfsYear.Year[i]))
    #     utmx, utmy, utmzoneNum, utmzoneLetter = utm.from_latlon(dfsYear.lat[j], dfsYear.lon[j])
    #     dist = np.sqrt((utmx - utmx)**2 + (utmy - utmy)**2) / (dfsYear.Year.tail(1).values - dfs.Year.head(1).values)
    #     print('year: %d, coordinates:(%f, %f)' %(dfsYear.Year[j], dfsYear.lon[j], dfsYear.lat[j]))
    #     print("the average ice flow rate is %.2f m\N{DOT OPERATOR}a\u207B\N{SUPERSCRIPT ONE}" %dist)

    for j in range(len(dfsYear)):
        aoi = ee.Geometry.Point([dfsYear.lon[j], dfsYear.lat[j]])
        Map.addLayer(aoi, {}, str(dfsYear.Year[j]))
        date_start = str(dfsYear.Year[j]) + '-' + str(1) + '-' + str(1) 
        date_end = str(dfsYear.Year[j]) + '-' + str(12) + '-' + str(31) 
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
                    .select(['Blue', 'Green', 'Red', 'NIR', 'visnirAlbedo']) \
                    .map(landsatStdDev)
        etmCol = ee.ImageCollection('LANDSAT/LE07/C02/T1_L2') \
                    .filter(colFilter) \
                    .map(prepEtm) \
                    .select(['Blue', 'Green', 'Red', 'NIR', 'visnirAlbedo']) \
                    .map(landsatStdDev)
        tmCol = ee.ImageCollection('LANDSAT/LT05/C02/T1_L2') \
                    .filter(colFilter) \
                    .map(prepEtm) \
                    .select(['Blue', 'Green', 'Red', 'NIR', 'visnirAlbedo']) \
                    .map(landsatStdDev)
        tm4Col = ee.ImageCollection('LANDSAT/LT04/C02/T1_L2') \
                    .filter(colFilter) \
                    .map(prepEtm) \
                    .select(['Blue', 'Green', 'Red', 'NIR', 'visnirAlbedo']) \
                    .map(landsatStdDev)
        s2Col = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
                    .filter(s2colFilter) \
                    .map(prepS2) \
                    .select(['Blue', 'Green', 'Red', 'NIR', 'visnirAlbedo']) \
                    .sort('system:time_start', True) \
                    .map(s2StdDev)

        # landsatCol = etmCol.merge(tmCol)
        landsatCol = oliCol.merge(etmCol).merge(tmCol).merge(tm4Col).sort('system:time_start', True)
        # multiSat = landsatCol.merge(s2Col).sort('system:time_start', True) # // Sort chronologically in descending order.
    

        if landsatCol.size().getInfo()==0:
            continue

        pointValue = landsatCol.getRegion(aoi, 150).getInfo() # The number e.g. 500 is the buffer size
        dflandsat = ee_array_to_df(pointValue, ['Blue', 'Green', 'Red', 'NIR', 'visnirAlbedo', 'std3', 'std5', 'std9', 'std15'])
        dflandsat['satellite'] = 'Landsat'

        if s2Col.size().getInfo()==0:
            dfpoint = dflandsat
        else:
            pointValue = s2Col.getRegion(aoi, 150).getInfo() # The number e.g. 500 is the buffer size
            dfs2 = ee_array_to_df(pointValue, ['Blue', 'Green', 'Red', 'NIR', 'visnirAlbedo', 'std3', 'std5', 'std9', 'std15'])
            dfs2['satellite'] = 'Sentinel2'
            dfpoint = (pd.concat([dflandsat, dfs2])).sort_values(by="time")


        pointValueFile = 'promice/multiSat150m/' + stationName.replace("*", "-") + '.csv'
        # if os.path.exists(pointValueFile):
        if j==0:
            dfpoint.to_csv(pointValueFile, mode='w', index=False, header=True)
        else:
            dfpoint.to_csv(pointValueFile, mode='a', index=False, header=False)

# %%



