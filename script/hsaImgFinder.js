/*
This script is used to find harmonized satellite images for a given area of interest (AOI) and time period.
The AOI is defined by a bounding box (BBox).
Users can also export harmonized satellite image and the harmonized satellite albedo (HSA) to their Google Drive.

NOTE: You will need to change the land mask if you are looking for images outside Greenland.
NOTE: You will need to change the CRS before exporting your images.

Shunan Feng
shunan.feng@envs.au.dk
*/

/**
 * Intial parameters
 */
// define your AOI here
var aoi = ee.Geometry.BBox(-50.40709020668755, 66.93869655503401,	-49.2562723355938, 67.241807971802); //west, south, east, north
// define your time period here
var date_start = ee.Date.fromYMD(2023, 8, 14);
var date_end = ee.Date.fromYMD(2023, 8, 16);


var greenlandmask = ee.Image('OSU/GIMP/2000_ICE_OCEAN_MASK')
                      .select('ice_mask').eq(1); //'ice_mask', 'ocean_mask'

// Display AOI on the map.
Map.centerObject(aoi, 10);
Map.addLayer(aoi, {color: 'f8766d'}, 'AOI');
// Map.setOptions('HYBRID');


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
    ['B2',   'B3',    'B4',  'B8',  'B11',   'B12',   'QA60', 'SCL', QA_BAND],
    ['Blue', 'Green', 'Red', 'NIR', 'SWIR1', 'SWIR2', 'QA60', 'SCL', QA_BAND]
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
 * archived after updating to Cloud Score+
 */
// function maskS2sr(image) {
//   var qa = image.select('QA60');

//   // Bits 10 and 11 are clouds and cirrus, respectively.
//   var cloudBitMask = 1 << 10;
//   var cirrusBitMask = 1 << 11;
//   // 1 is saturated or defective pixel
//   var not_saturated = image.select('SCL').neq(1);
//   // Both flags should be set to zero, indicating clear conditions.
//   var mask = qa.bitwiseAnd(cloudBitMask).eq(0)
//       .and(qa.bitwiseAnd(cirrusBitMask).eq(0));

//   // return image.updateMask(mask).updateMask(not_saturated);
//   return image.updateMask(mask).updateMask(not_saturated).divide(10000);
// }

/**
 * Function to mask clouds using the Cloud Score+
 */
// Cloud Score+ image collection. Note Cloud Score+ is produced from Sentinel-2
// Level 1C data and can be applied to either L1C or L2A collections.
var csPlus = ee.ImageCollection('GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED');

// Use 'cs' or 'cs_cdf', depending on your use case; see docs for guidance.
var QA_BAND = 'cs'; // I find'cs' is better than 'cs_cdf' because it is more robust but may mask out more clear pixels though

// The threshold for masking; values between 0.50 and 0.65 generally work well.
// Higher values will remove thin clouds, haze & cirrus shadows.
var CLEAR_THRESHOLD = 0.65;

function maskS2sr(image) {
  // 1 is saturated or defective pixel
  var not_saturated = image.select('SCL').neq(1);
  return image.updateMask(image.select(QA_BAND).gte(CLEAR_THRESHOLD))
              .updateMask(not_saturated)
              .divide(10000);
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

// Define function to prepare OLI2 images.
function prepOli2(img) {
  var orig = img;
  img = renameOli(img);
  img = maskL8sr(img);
  img = oli2oli(img);
  img = imRangeFilter(img);
  img = addVisnirAlbedo(img);
  return ee.Image(img.copyProperties(orig, orig.propertyNames()).set('SATELLITE', 'LANDSAT_9'));
}
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


var colFilter = ee.Filter.and(
  ee.Filter.bounds(aoi),
  ee.Filter.date(date_start, date_end)
  // ee.Filter.calendarRange(6, 8, 'month')
);

var s2colFilter =  ee.Filter.and(
  ee.Filter.bounds(aoi),
  ee.Filter.date(date_start, date_end),
  // ee.Filter.calendarRange(6, 7, 'month'),
  // ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 50),
  ee.Filter.lt('MEAN_SOLAR_ZENITH_ANGLE', 76)
);

var oli2Col = ee.ImageCollection('LANDSAT/LC09/C02/T1_L2') 
              .filter(colFilter) 
              .map(prepOli2)
              .select(['Blue', 'Green', 'Red', 'NIR', 'SWIR1','SWIR2','visnirAlbedo']); //# .select(['totalAlbedo']) or  .select(['visnirAlbedo'])
var oliCol = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2') 
              .filter(colFilter) 
              .map(prepOli)
              .select(['Blue', 'Green', 'Red', 'NIR', 'SWIR1','SWIR2','visnirAlbedo']); //# .select(['totalAlbedo']) or  .select(['visnirAlbedo'])
var etmCol = ee.ImageCollection('LANDSAT/LE07/C02/T1_L2') 
            .filter(colFilter) 
            .filter(ee.Filter.calendarRange(1999, 2020, 'year')) // filter out L7 imagaes acquired after 2020 due to orbit drift
            .map(prepEtm)
            .select(['Blue', 'Green', 'Red', 'NIR', 'SWIR1','SWIR2','visnirAlbedo']); // # .select(['totalAlbedo']) or  .select(['visnirAlbedo'])
var tmCol = ee.ImageCollection('LANDSAT/LT05/C02/T1_L2') 
            .filter(colFilter) 
            .map(prepTm)
            .select(['Blue', 'Green', 'Red', 'NIR', 'SWIR1','SWIR2','visnirAlbedo']); //# .select(['totalAlbedo']) or  .select(['visnirAlbedo'])
var tm4Col = ee.ImageCollection('LANDSAT/LT04/C02/T1_L2') 
            .filter(colFilter) 
            .map(prepTm)
            .select(['Blue', 'Green', 'Red', 'NIR', 'SWIR1','SWIR2','visnirAlbedo']); //# .select(['totalAlbedo']) or  .select(['visnirAlbedo'])
var s2Col = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') 
            .linkCollection(csPlus, [QA_BAND])
            .filter(s2colFilter) 
            .map(prepS2)
            .select(['Blue', 'Green', 'Red', 'NIR', 'SWIR1','SWIR2','visnirAlbedo']); //# .select(['totalAlbedo']) or  .select(['visnirAlbedo'])

var landsatCol = oliCol.merge(etmCol).merge(tmCol).merge(tm4Col).merge(oli2Col);
var multiSat = landsatCol.merge(s2Col).sort('system:time_start', true); // Sort chronologically in descending order.
  
print(multiSat);
var imgHSA = multiSat.mean().clip(aoi).updateMask(greenlandmask);
var visParam = {min:0, max:1, bands:['Red', 'Green', 'Blue']};
Map.addLayer(imgHSA, visParam, 'img');
              

var palettes = require('users/gena/packages:palettes');
var blue_fluorite = palettes.misc.BlueFluorite[256];
var visHSA = {min: 0, max: 1, palette: blue_fluorite};

Map.addLayer(imgHSA.select('visnirAlbedo'), visHSA, 'albedo');

var map_id_dict =imgHSA.select('visnirAlbedo').getMap(visHSA);
print(map_id_dict);


// Export the image, specifying the CRS, transform, and region.
Export.image.toDrive({
  image: imgHSA.select(['Blue', 'Green', 'Red', 'NIR', 'SWIR1','SWIR2']),
  description: 'dp19sat20230815',
  folder:'export',
  scale:30,
  crs: 'EPSG:32622', // change your CRS here
  // crsTransform: projection.transform,
  region: aoi
});


// Export the image, specifying the CRS, transform, and region.
Export.image.toDrive({
  image: imgHSA.select('visnirAlbedo'),
  description: 'hsa20230815',
  folder:'export',
  scale:30,
  crs: 'EPSG:32622', // change your CRS here
  // crsTransform: projection.transform,
  region: aoi
});
