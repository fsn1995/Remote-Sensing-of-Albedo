/*
This part of script would pair the Sentinel 2 and Landsat 8 images and export to Google Drive. 
It was inspired by Justin Braaten's GEE tutorial:
https://developers.google.com/earth-engine/tutorials/community/landsat-etm-to-oli-harmonization
The batch export was done via the tools developed by Rodrigo E. Principe :
https://github.com/fitoprincipe/geetools-code-editor/wiki

Shunan Feng (shunan.feng@envs.au.dk)
*/

// Note:
// The batch export tool can take a long time as the dataset is much denser compared to Landsat 7 vs Landsat 8.
// It might be better to export band by band.
// // Function to get and rename bands of interest from OLI.
// function renameOli(img) {
//   return img.select(
//     ['SR_B2',  'SR_B3',   'SR_B4', 'SR_B5', 'SR_B6',   'SR_B7',   'QA_PIXEL', 'QA_RADSAT'],
//     ['BlueL8', 'GreenL8', 'RedL8', 'NIRL8', 'SWIR1L8', 'SWIR2L8', 'QA_PIXEL', 'QA_RADSAT']);
// }
// // Function to get and rename bands of interest from Sentinel 2.
// function renameS2(img) {
//   return img.select(
//     ['B2',     'B3',      'B4',    'B8',    'B11',     'B12',     'QA60', 'SCL'],
//     ['BlueS2', 'GreenS2', 'RedS2', 'NIRS2', 'SWIR1S2', 'SWIR2S2', 'QA60', 'SCL']
//   );
// }

// Function to get and rename bands of interest from OLI.
function renameOli(img) {
  return img.select(
    ['SR_B7',  'QA_PIXEL', 'QA_RADSAT'],
    ['SWIR2L8', 'QA_PIXEL', 'QA_RADSAT']);
}

function renameS2(img) {
  return img.select(
    ['B12',     'QA60', 'SCL'],
    ['SWIR2S2', 'QA60', 'SCL']
  );
}

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
  var opticalBands = image.select('SWIR2L8').multiply(0.0000275).add(-0.2);
  // var opticalBands = image.select('SR_B.').multiply(0.0000275).add(-0.2);
  // var thermalBands = image.select('ST_B.*').multiply(0.00341802).add(149.0);

  // Replace the original bands with the scaled ones and apply the masks.
  return image.addBands(opticalBands, null, true)
      // .addBands(thermalBands, null, true)
      .updateMask(qaMask)
      .updateMask(saturationMask);
}


/**
 * Function to mask clouds using the Sentinel-2 QA band
 * @param {ee.Image} image Sentinel-2 image
 * @return {ee.Image} cloud masked Sentinel-2 image
 */
function maskS2clouds(image) {
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


// Define function to prepare OLI images.
function prepOli(img) {
  var orig = img;
  img = renameOli(img);
  img = maskL8sr(img);
  // img = addNDSIoli(img);
  return ee.Image(img.copyProperties(orig, orig.propertyNames()));
}


// Define function to prepare S2 images.
function prepS2(img) {
  var orig = img;
  img = renameS2(img);
  img = maskS2clouds(img);
  // img = addNDSI(img);
  return ee.Image(img.copyProperties(orig, orig.propertyNames()).set('SATELLITE', 'SENTINEL_2'));
}

var greenlandmask = ee.Image('OSU/GIMP/2000_ICE_OCEAN_MASK')
                      .select('ice_mask').eq(1); //'ice_mask', 'ocean_mask'
// var greenlandmask = ee.Image('OSU/GIMP/2000_ICE_OCEAN_MASK')
//                       .select('ocean_mask').eq(1); //'ice_mask', 'ocean_mask'

// var aoi = /* color: #0b4a8b */ee.Geometry.Polygon(
//         [[[-61.63041559528885, 76.18619438808824],
//           [-51.78666559528885, 60.06734599422235],
//           [-42.73393122028885, 59.49227511780627],
//           [-38.33939997028885, 65.03717957749697],
//           [-33.94486872028885, 66.198035394237],
//           [-19.882368720288856, 69.99225298677781],
//           [-16.015181220288856, 75.88931492254663]]]);// south greenland
// var aoi = /* color: #ffc82d */ee.Geometry.Polygon(
//   [[[-36.29516924635421, 83.70737243835941],
//     [-51.85180987135421, 82.75597137647488],
//     [-61.43188799635421, 81.99879137488564],
//     [-74.08813799635422, 78.10103528196419],
//     [-70.13305987135422, 75.65372336709613],
//     [-61.08032549635421, 75.71891096312955],
//     [-52.20337237135421, 60.9795530382023],
//     [-43.41430987135421, 58.59235996703347],
//     [-38.49243487135421, 64.70478286561182],
//     [-19.771731746354217, 69.72271161037442],
//     [-15.728762996354217, 76.0828635948066],
//     [-15.904544246354217, 79.45091003031243],
//     [-10.015872371354217, 81.62328742628017],
//     [-26.627200496354217, 83.43179828852398],
//     [-31.636966121354217, 83.7553561747887]]]); // whole greenland

var aoi = /* color: #d63000 */ee.Geometry.Polygon(
        [[[-75.35327725640606, 78.15797707936824],
          [-58.137306661848434, 69.59945512283268],
          [-51.82415036596651, 59.897134149764156],
          [-42.233465551083604, 59.260337764670496],
          [-61.95501079278244, 79.65995314962508]]]);   // western greenland

// Display AOI on the map.
Map.centerObject(aoi, 4);
Map.addLayer(aoi, {color: 'f8766d'}, 'AOI');
Map.setOptions('HYBRID');

// var date_start = ee.Image(s2col.first()).date().format('yyyy-MM-dd'),
//     date_end = ee.Date(Date.now()).format('yyyy-MM-dd'),
//     now = Date.now();
var year_start = 2020; // 2013-04-11T00:00:00 - Present
var year_end = 2020;

// var month_start = 5;

// var month_end = 12;

var date_start = ee.Date.fromYMD(2020, 5, 1);
// var date_end = date_start.advance(1,'month');
var date_end = ee.Date.fromYMD(2020, 5, 15);




var colFilter = ee.Filter.and(
  ee.Filter.bounds(aoi),
  ee.Filter.date(date_start, date_end),
  // ee.Filter.calendarRange(moi, moi, 'month'),
  ee.Filter.lt('CLOUD_COVER', 50)
);

var s2colFilter =  ee.Filter.and(
  ee.Filter.bounds(aoi),
  ee.Filter.date(date_start, date_end),
  // ee.Filter.calendarRange(moi, moi, 'month'),
  ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 50)
);


// var oliCol = ee.ImageCollection("LANDSAT/LC08/C01/T1_TOA")
var oliCol = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2") 
             .filter(colFilter)
             .map(prepOli);

var s2Col = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
            .filter(s2colFilter)
            .map(prepS2);

// var landsatCol = oliCol.merge(etmCol).merge(tmCol);
// var multiSat = landsatCol.merge(s2Col);
// print(landsatCol)


// Difference in days between start and finish
var diff = date_end.difference(date_start, 'day');

// Make a list of all dates
var dayNum = 1; // steps of day number
var range = ee.List.sequence(0, diff.subtract(1), dayNum).map(function(day){return date_start.advance(day,'day')});

// Function for iteration over the range of dates

var day_mosaicsL8 = function(date, newlist) {
  // Cast
  date = ee.Date(date)
  newlist = ee.List(newlist)

  // Filter collection between date and the next day
  var filtered = oliCol.filterDate(date, date.advance(dayNum,'day'));

  // Make the mosaic
  var image = ee.Image(
      filtered.median().copyProperties(filtered.first()))
      .set({date: date.format('yyyy-MM-dd')})
      .set('system:time_start', filtered.first().get('system:time_start'));
  // Add the mosaic to a list only if the collection has images
  return ee.List(ee.Algorithms.If(filtered.size(), newlist.add(image), newlist));
};
var l8dayCol = ee.ImageCollection(ee.List(range.iterate(day_mosaicsL8, ee.List([]))));
// print(l7dayCol, 'l7dayCol');
// print(l8dayCol, 'l8dayCol');
var day_mosaicsS2 = function(date, newlist) {
  // Cast
  date = ee.Date(date)
  newlist = ee.List(newlist)

  // Filter collection between date and the next day
  var filtered = s2Col.filterDate(date, date.advance(dayNum,'day'));

  // Make the mosaic
  var image = ee.Image(
      filtered.median().copyProperties(filtered.first()))
      .set({date: date.format('yyyy-MM-dd')})
      .set('system:time_start', filtered.first().get('system:time_start'));
  // Add the mosaic to a list only if the collection has images
  return ee.List(ee.Algorithms.If(filtered.size(), newlist.add(image), newlist));
};
var s2dayCol = ee.ImageCollection(ee.List(range.iterate(day_mosaicsS2, ee.List([]))));


// Define an allowable time difference: a day in milliseconds.
// https://developers.google.com/earth-engine/guides/joins_save_all
var oneDaysMillis = 1 * 24 * 60 * 60 * 1000;
// Create a time filter to define a match as overlapping timestamps.

var timeFilter = ee.Filter.or(
  ee.Filter.maxDifference({
    difference: oneDaysMillis,
    leftField: 'system:time_start',
    rightField: 'system:time_start'
  })
//   ee.Filter.maxDifference({
//     difference: oneDaysMillis,
//     leftField: 'system:time_end',
//     rightField: 'system:time_start'
//   })
);

// Define the join.
var saveFirstJoin = ee.Join.saveFirst({
  matchKey: 'timewindow',
  ordering: 'system:time_start',
  ascending: false
});

// Apply the join.
// var landsatDayCol = saveFirstJoin.apply(l8dayCol, l7dayCol, timeFilter);
// function noiseMask(image) {
//   var mask = image.normalizedDifference(['NDSIoli', 'NDSIetm']).abs().multiply(2).subtract(1);
//   return image.updateMask(mask.lt(0));
// }

var landsatDayCol = ee.ImageCollection(saveFirstJoin.apply(l8dayCol, s2dayCol, timeFilter))
    .map(function(image) {
        return image.addBands(image.get('timewindow'))
                    .updateMask(greenlandmask.eq(1))
                    .clip(aoi);
    });

// landsatDayCol = landsatDayCol.map(noiseMask);



// landsatDayCol = landsatDayCol.map(function(image) {
//   return image.reduceResolution({
//     reducer: ee.Reducer.mean(),
//     maxPixels: 400,
//     bestEffort: true
//   })
// })
// print(landsatDayCol);

// var visPara = {
//   min: 0,
//   max: 9000,
//   band: ['RedL8', 'GreenL8', 'BlueL8']
// };
// Map.addLayer(landsatDayCol.first(), visPara);

var batch = require('users/fitoprincipe/geetools:batch');

// batch export
// batch.Download.ImageCollection.toDrive(landsatDayCol.select(['BlueL8', 'BlueS2']), 'sentinel', 
//                 {scale: 600, 
//                  region: aoi, 
//                  type: 'uint16',
//                  name: 'Blue_{system_date}'
//                 });
// batch.Download.ImageCollection.toDrive(landsatDayCol.select(['GreenL8', 'GreenS2']), 'sentinel', 
//                 {scale: 600, 
//                  region: aoi, 
//                  type: 'uint16',
//                  name: 'Green_{system_date}'
//                 });

// batch.Download.ImageCollection.toDrive(landsatDayCol.select(['RedL8', 'RedS2']), 'sentinel', 
//                 {scale: 600, 
//                  region: aoi, 
//                  type: 'uint16',
//                  name: 'Red_{system_date}'
//                 });
                
// batch.Download.ImageCollection.toDrive(landsatDayCol.select(['NIRL8', 'NIRS2']), 'sentinel', 
//                 {scale: 600, 
//                  region: aoi, 
//                  type: 'uint16',
//                  name: 'NIR_{system_date}'
//                 });
                
// batch.Download.ImageCollection.toDrive(landsatDayCol.select(['SWIR1L8', 'SWIR1S2']), 'sentinel', 
//                 {scale: 600, 
//                  region: aoi, 
//                  type: 'uint16',
//                  name: 'SWIR1_{system_date}'
//                 });
                
batch.Download.ImageCollection.toDrive(landsatDayCol.select(['SWIR2L8', 'SWIR2S2']), 'sentinel', 
                {scale: 600, 
                 region: aoi, 
                 type: 'uint16',
                 name: 'SWIR2_{system_date}'
                });
                
