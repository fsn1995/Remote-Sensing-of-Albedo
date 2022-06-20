/*
This tutorial is made to demonstrate the workflow of harmonizing Landsat 4-7 and Sentinel 2 to Landsat 8 
time series of datasets.
It will display the charts of the harmonized satellite albedo (All Observations) and original albedo 
(All Observations Original).
The linear trendline will be plotted on a separate chart. 

ref:
This script is adapted from the excellent tutorial made by Justin Braaten.
https://github.com/jdbcode
https://developers.google.com/earth-engine/tutorials/community/landsat-etm-to-oli-harmonization

Shunan Feng
shunan.feng@envs.au.dk
*/

/*
prepare harmonized satellite data
*/

// Function to get and rename bands of interest from OLI.
function renameOli(img) {
  return img.select(
    ['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7', 'QA_PIXEL', 'QA_RADSAT'], // 'QA_PIXEL', 'QA_RADSAT'
    ['Blue',  'Green', 'Red',   'NIR',   'SWIR1', 'SWIR2', 'QA_PIXEL', 'QA_RADSAT']);//'QA_PIXEL', 'QA_RADSAT';
}
// Function to get and rename bands of interest from ETM+, TM.
function renameEtm(img) {
  return img.select(
    ['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B7', 'QA_PIXEL', 'QA_RADSAT'], //#,   'QA_PIXEL', 'QA_RADSAT'
    ['Blue',  'Green', 'Red',   'NIR',   'SWIR1', 'SWIR2', 'QA_PIXEL', 'QA_RADSAT']); // #, 'QA_PIXEL', 'QA_RADSAT'
}
// Function to get and rename bands of interest from Sentinel 2.
function renameS2(img) {
  return img.select(
    ['B2',   'B3',    'B4',  'B8',  'B11',   'B12',   'QA60', 'SCL'],
    ['Blue', 'Green', 'Red', 'NIR', 'SWIR1', 'SWIR2', 'QA60', 'SCL']
  );
}

/* RMA transformation */
var rmaCoefficients = {
  itcpsL7: ee.Image.constant([-0.0084, -0.0065, 0.0022, -0.0768, -0.0314, -0.0022]),
  slopesL7: ee.Image.constant([1.1017, 1.0840, 1.0610, 1.2100, 1.2039, 1.2402]),
  itcpsS2: ee.Image.constant([0.0210, 0.0167, 0.0155, -0.0693, -0.0039, -0.0112]),
  slopesS2: ee.Image.constant([1.0849, 1.0590, 1.0759, 1.1583, 1.0479, 1.0148])
}; // #rma

function oli2oli(img) {
  return img.select(['Blue', 'Green', 'Red', 'NIR', 'SWIR1', 'SWIR2'])
            .toFloat();
}

function etm2oli(img) {
  return img.select(['Blue', 'Green', 'Red', 'NIR', 'SWIR1', 'SWIR2'])
    .multiply(rmaCoefficients.slopesL7)
    .add(rmaCoefficients.itcpsL7)
    .toFloat();
}
function s22oli(img) {
  return img.select(['Blue', 'Green', 'Red', 'NIR', 'SWIR1', 'SWIR2'])
    .multiply(rmaCoefficients.slopesS2)
    .add(rmaCoefficients.itcpsS2)
    .toFloat();
}

function imRangeFilter(image) {
  var maskMax = image.lte(1);
  var maskMin = image.gt(0);
  return image.updateMask(maskMax).updateMask(maskMin);
}


/* 
Cloud mask for Landsat data based on fmask (QA_PIXEL) and saturation mask 
based on QA_RADSAT.
Cloud mask and saturation mask by sen2cor.
Codes provided by GEE official.
*/

// This example demonstrates the use of the Landsat 8 Collection 2, Level 2
// QA_PIXEL band (CFMask) to mask unwanted pixels.

function maskL8sr(image) {
  // Bit 0 - Fill
  // Bit 1 - Dilated Cloud
  // Bit 2 - Cirrus
  // Bit 3 - Cloud
  // Bit 4 - Cloud Shadow
  var qaMask = image.select('QA_PIXEL').bitwiseAnd(parseInt('11111', 2)).eq(0);
  var saturationMask = image.select('QA_RADSAT').eq(0);

  // Apply the scaling factors to the appropriate bands.
  // var opticalBands = image.select(['Blue', 'Green', 'Red', 'NIR']).multiply(0.0000275).add(-0.2);
  // var thermalBands = image.select('ST_B.*').multiply(0.00341802).add(149.0);

  // Replace the original bands with the scaled ones and apply the masks.
  return image.select(['Blue', 'Green', 'Red', 'NIR', 'SWIR1','SWIR2']).multiply(0.0000275).add(-0.2)
      // .addBands(thermalBands, null, true)
      .updateMask(qaMask)
      .updateMask(saturationMask);
}

// This example demonstrates the use of the Landsat 4, 5, 7 Collection 2,
// Level 2 QA_PIXEL band (CFMask) to mask unwanted pixels.

function maskL457sr(image) {
  // Bit 0 - Fill
  // Bit 1 - Dilated Cloud
  // Bit 2 - Unused
  // Bit 3 - Cloud
  // Bit 4 - Cloud Shadow
  var qaMask = image.select('QA_PIXEL').bitwiseAnd(parseInt('11111', 2)).eq(0);
  var saturationMask = image.select('QA_RADSAT').eq(0);

  // Apply the scaling factors to the appropriate bands.
  // var opticalBands = image.select('SR_B.').multiply(0.0000275).add(-0.2);
  // var thermalBand = image.select('ST_B6').multiply(0.00341802).add(149.0);

  // Replace the original bands with the scaled ones and apply the masks.
  return image.select(['Blue', 'Green', 'Red', 'NIR', 'SWIR1','SWIR2']).multiply(0.0000275).add(-0.2)
      // .addBands(thermalBand, null, true)
      .updateMask(qaMask)
      .updateMask(saturationMask);
}


/**
 * Function to mask clouds using the Sentinel-2 QA band
 * @param {ee.Image} image Sentinel-2 image
 * @return {ee.Image} cloud masked Sentinel-2 image
 */
function maskS2sr(image) {
  var qa = image.select('QA60');

  // Bits 10 and 11 are clouds and cirrus, respectively.
  var cloudBitMask = 1 << 10;
  var cirrusBitMask = 1 << 11;
  // 1 is saturated or defective pixel
  var not_saturated = image.select('SCL').neq(1);
  // Both flags should be set to zero, indicating clear conditions.
  var mask = qa.bitwiseAnd(cloudBitMask).eq(0)
      .and(qa.bitwiseAnd(cirrusBitMask).eq(0));

  // return image.updateMask(mask).updateMask(not_saturated);
  return image.updateMask(mask).updateMask(not_saturated).divide(10000);
}

// // narrow to broadband conversion
function addVisnirAlbedo(image) {
  var albedo = image.expression(
    '0.7963 * Blue + 2.2724 * Green - 3.8252 * Red + 1.4143 * NIR + 0.2053',
    {
      'Blue': image.select('Blue'),
      'Green': image.select('Green'),
      'Red': image.select('Red'),
      'NIR': image.select('NIR')
    }
  ).rename('visnirAlbedo');
  return image.addBands(albedo).copyProperties(image, ['system:time_start']);
}
// function addNDSI(image) {
//   // var indice = image.normalizedDifference(['Green', 'SWIR1']).rename('NDSI');
//     return image.normalizedDifference(['Green', 'SWIR1']).rename('NDSI');
//   }

/* get harmonized image collection */

// Define function to prepare OLI images.
function prepOli(img) {
  var orig = img;
  img = renameOli(img);
  img = maskL8sr(img);
  img = oli2oli(img);
  img = imRangeFilter(img);
  img = addVisnirAlbedo(img);
  return ee.Image(img.copyProperties(orig, orig.propertyNames()).set('SATELLITE', 'LANDSAT_8'));
}
// Define function to prepare ETM+ images.
function prepEtm(img) {
  var orig = img;
  img = renameEtm(img);
  img = maskL457sr(img);
  img = etm2oli(img);
  img = imRangeFilter(img);
  img = addVisnirAlbedo(img);
  return ee.Image(img.copyProperties(orig, orig.propertyNames()).set('SATELLITE', 'LANDSAT_7'));
}
// Define function to prepare TM images.
function prepTm(img) {
  var orig = img;
  img = renameEtm(img);
  img = maskL457sr(img);
  img = etm2oli(img);
  img = imRangeFilter(img);
  img = addVisnirAlbedo(img);
  return ee.Image(img.copyProperties(orig, orig.propertyNames()).set('SATELLITE', 'LANDSAT_4/5'));
}
// Define function to prepare S2 images.
function prepS2(img) {
  var orig = img;
  img = renameS2(img);
  img = maskS2sr(img);
  img = s22oli(img);
  img = imRangeFilter(img);
  img = addVisnirAlbedo(img);
  return ee.Image(img.copyProperties(orig, orig.propertyNames()).set('SATELLITE', 'SENTINEL_2'));
}


var date_start = ee.Date.fromYMD(1984, 1, 1);
var date_end = ee.Date.fromYMD(2020, 12, 31);

// var aoi = ee.Geometry.Point([-49.3476433532785, 67.0775206116519]);
var aoi = ee.Geometry.Point([-48.8355, 67.0670]); // KAN_M

// Display AOI on the map.
Map.centerObject(aoi, 4);
Map.addLayer(aoi, {color: 'f8766d'}, 'AOI');
Map.setOptions('HYBRID');

var colFilter = ee.Filter.and(
  ee.Filter.bounds(aoi),
  ee.Filter.date(date_start, date_end)
  // ee.Filter.calendarRange(6, 8, 'month')
);

var s2colFilter =  ee.Filter.and(
  ee.Filter.bounds(aoi),
  ee.Filter.date(date_start, date_end),
  // ee.Filter.calendarRange(6, 8, 'month'),
  ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 50)
);

var oliCol = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2') 
              .filter(colFilter) 
              .map(prepOli)
              .select(['visnirAlbedo']); //# .select(['totalAlbedo']) or  .select(['visnirAlbedo'])
var etmCol = ee.ImageCollection('LANDSAT/LE07/C02/T1_L2') 
            .filter(colFilter) 
            .filter(ee.Filter.calendarRange(1999, 2020, 'year')) // filter out L7 imagaes acquired after 2020 due to orbit drift
            .map(prepEtm)
            .select(['visnirAlbedo']); // # .select(['totalAlbedo']) or  .select(['visnirAlbedo'])
var tmCol = ee.ImageCollection('LANDSAT/LT05/C02/T1_L2') 
            .filter(colFilter) 
            .map(prepTm)
            .select(['visnirAlbedo']); //# .select(['totalAlbedo']) or  .select(['visnirAlbedo'])
var tm4Col = ee.ImageCollection('LANDSAT/LT04/C02/T1_L2') 
            .filter(colFilter) 
            .map(prepTm)
            .select(['visnirAlbedo']); //# .select(['totalAlbedo']) or  .select(['visnirAlbedo'])
var s2Col = ee.ImageCollection('COPERNICUS/S2_SR') 
            .filter(s2colFilter) 
            .map(prepS2)
            .select(['visnirAlbedo']); //# .select(['totalAlbedo']) or  .select(['visnirAlbedo'])

var landsatCol = oliCol.merge(etmCol).merge(tmCol).merge(tm4Col);
var multiSat = landsatCol.merge(s2Col).sort('system:time_start', true); // Sort chronologically in descending order.
  
// prepare the chart of harmonized satellite albedo
var allObs = multiSat.map(function(img) {
  var obs = img.reduceRegion(
      {geometry: aoi, 
      reducer: ee.Reducer.median(), 
      scale: 30});
  return img.set('visnirAlbedo', obs.get('visnirAlbedo'));
});

var allObsValid = allObs.filter(ee.Filter.lt('visnirAlbedo', 1));
var chartAllObs =
  ui.Chart.feature.groups(allObsValid, 'system:time_start', 'visnirAlbedo', 'SATELLITE')
      .setChartType('ScatterChart')
      // .setSeriesNames(['TM', 'ETM+', 'OLI', 'S2'])
      .setOptions({
        title: 'All Observations',
        colors: ['f8766d', '00ba38', '619cff', '8934eb'],
        hAxis: {title: 'Date'},
        vAxis: {title: 'visnirAlbedo', viewWindow: {min: 0, max: 1}},
        pointSize: 6,
        dataOpacity: 0.5
      });
print(chartAllObs);

var chartAllObsTrend = ui.Chart.image.series({
  imageCollection: multiSat,
  region: aoi,
  reducer: ee.Reducer.median(),
  scale:30,
  xProperty:'system:time_start'
}).setChartType('ScatterChart')
  .setOptions({
    title: 'All Observations with Trendline',
    hAxis: {title: 'Date'},
    vAxis: {title: 'visnirAlbedo', viewWindow: {min: 0, max: 1}},
    pointSize: 6,
    dataOpacity: 0.5,
    trendlines: {0:{color:'black'}}
  });
print(chartAllObsTrend);

/*
Make a new chart for the original dataset. 
*/
// Define function to prepare OLI images.
function prepOliOri(img) {
  var orig = img;
  img = renameOli(img);
  img = maskL8sr(img);
  img = imRangeFilter(img);
  img = addVisnirAlbedo(img);
  return ee.Image(img.copyProperties(orig, orig.propertyNames()).set('SATELLITE', 'LANDSAT_8'));
}
// Define function to prepare ETM+ images.
function prepEtmOri(img) {
  var orig = img;
  img = renameEtm(img);
  img = maskL457sr(img);
  img = imRangeFilter(img);
  img = addVisnirAlbedo(img);
  return ee.Image(img.copyProperties(orig, orig.propertyNames()).set('SATELLITE', 'LANDSAT_7'));
}
// Define function to prepare TM images.
function prepTmOri(img) {
  var orig = img;
  img = renameEtm(img);
  img = maskL457sr(img);
  img = imRangeFilter(img);
  img = addVisnirAlbedo(img);
  return ee.Image(img.copyProperties(orig, orig.propertyNames()).set('SATELLITE', 'LANDSAT_4/5'));
}
// Define function to prepare S2 images.
function prepS2Ori(img) {
  var orig = img;
  img = renameS2(img);
  img = maskS2sr(img);
  img = imRangeFilter(img);
  img = addVisnirAlbedo(img);
  return ee.Image(img.copyProperties(orig, orig.propertyNames()).set('SATELLITE', 'SENTINEL_2'));
}

var oliColOri = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2') 
              .filter(colFilter) 
              .map(prepOliOri)
              .select(['visnirAlbedo']); //# .select(['totalAlbedo']) or  .select(['visnirAlbedo'])
var etmColOri = ee.ImageCollection('LANDSAT/LE07/C02/T1_L2') 
            .filter(colFilter) 
            .filter(ee.Filter.calendarRange(1999, 2020, 'year')) // filter out L7 imagaes acquired after 2020 due to orbit drift
            .map(prepEtmOri)
            .select(['visnirAlbedo']); // # .select(['totalAlbedo']) or  .select(['visnirAlbedo'])
var tmColOri = ee.ImageCollection('LANDSAT/LT05/C02/T1_L2') 
            .filter(colFilter) 
            .map(prepTmOri)
            .select(['visnirAlbedo']); //# .select(['totalAlbedo']) or  .select(['visnirAlbedo'])
var tm4ColOri = ee.ImageCollection('LANDSAT/LT04/C02/T1_L2') 
            .filter(colFilter) 
            .map(prepTmOri)
            .select(['visnirAlbedo']); //# .select(['totalAlbedo']) or  .select(['visnirAlbedo'])
var s2ColOri = ee.ImageCollection('COPERNICUS/S2_SR') 
            .filter(s2colFilter) 
            .map(prepS2Ori)
            .select(['visnirAlbedo']); //# .select(['totalAlbedo']) or  .select(['visnirAlbedo'])

var landsatColOri = oliColOri.merge(etmColOri).merge(tmColOri).merge(tm4ColOri);
var multiSatOri = landsatColOri.merge(s2ColOri).sort('system:time_start', true); // Sort chronologically in descending order.
  

var allObsOri = multiSatOri.map(function(img) {
  var obs = img.reduceRegion(
      {geometry: aoi, 
      reducer: ee.Reducer.median(), 
      scale: 30});
  return img.set('visnirAlbedo', obs.get('visnirAlbedo'));
});

var allObsOriValid = allObsOri.filter(ee.Filter.lt('visnirAlbedo', 1));
var chartAllObsOri =
  ui.Chart.feature.groups(allObsOriValid, 'system:time_start', 'visnirAlbedo', 'SATELLITE')
      .setChartType('ScatterChart')
      // .setSeriesNames(['TM', 'ETM+', 'OLI', 'S2'])
      .setOptions({
        title: 'All Observations Original',
        colors: ['f8766d', '00ba38', '619cff', '8934eb'],
        hAxis: {title: 'Date'},
        vAxis: {title: 'visnirAlbedo', viewWindow: {min: 0, max: 1}},
        pointSize: 6,
        dataOpacity: 0.5
      });
print(chartAllObsOri);

var chartAllObsOriTrend = ui.Chart.image.series({
  imageCollection: multiSatOri,
  region: aoi,
  reducer: ee.Reducer.median(),
  scale:30,
  xProperty:'system:time_start'
}).setChartType('ScatterChart')
  // .setSeriesNames('visnirAlbedo')
  .setOptions({
    title: 'All Observations Original with Trendline',
    hAxis: {title: 'Date'},
    vAxis: {title: 'visnirAlbedo', viewWindow: {min: 0, max: 1}},
    pointSize: 6,
    dataOpacity: 0.5,
    trendlines: {0:{color:'black'}}
  });
print(chartAllObsOriTrend);