'''
This part of script is to display the albedo at k transect.
Users will need QGIS and the qgis-earthengine-plugin: https://gee-community.github.io/qgis-earthengine-plugin/

Shunan Feng (shunan.feng@envs.au.dk)
'''
#%% import library and prepare mask
import ee
# import geemap
from ee_plugin import Map

#%%
# Map = geemap.map()
# Map
greenlandmask = ee.Image('OSU/GIMP/2000_ICE_OCEAN_MASK') \
                   .select('ice_mask').eq(1) #'ice_mask', 'ocean_mask'
arcticDEM = ee.Image('UMN/PGC/ArcticDEM/V3/2m_mosaic')
visPara = {'min': 0,  'max': 3000.0, 'palette': ['0d13d8', '60e1ff', 'ffffff']}
Map.addLayer(arcticDEM.select('elevation'), visPara, 'arctic dem')

#%% GLIMS
glims = ee.FeatureCollection('GLIMS/current')
Map.addLayer(arcticDEM.select('elevation').clip(glims), visPara, 'arctic dem glims')