// prepare mask
var greenlandmask = ee.Image('OSU/GIMP/2000_ICE_OCEAN_MASK')
                      .select('ice_mask').eq(1); //'ice_mask', 'ocean_mask'
var ktransect = ee.Geometry.LineString(
    [[-50.1, 67.083333], [-48, 67.083333]]
); 


/*
prepare harmonized satellite data
*/

// Function to get and rename bands of interest from OLI.
function renameOli(img) {
  return img.select(
    ['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'QA_PIXEL', 'QA_RADSAT'], // 'QA_PIXEL', 'QA_RADSAT'
    ['Blue',  'Green', 'Red',   'NIR',   'QA_PIXEL', 'QA_RADSAT']);//'QA_PIXEL', 'QA_RADSAT';
}
// Function to get and rename bands of interest from ETM+, TM.
function renameEtm(img) {
  return img.select(
    ['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'QA_PIXEL', 'QA_RADSAT'], //#,   'QA_PIXEL', 'QA_RADSAT'
    ['Blue',  'Green', 'Red',   'NIR',   'QA_PIXEL', 'QA_RADSAT']); // #, 'QA_PIXEL', 'QA_RADSAT'
}
// Function to get and rename bands of interest from Sentinel 2.
function renameS2(img) {
  return img.select(
    ['B2',   'B3',    'B4',  'B8',  'QA60', 'SCL'],
    ['Blue', 'Green', 'Red', 'NIR', 'QA60', 'SCL']
    //['B2',     'B3',      'B4',    'B8',    'B11',     'B12',     'QA60', 'SCL'],
    //['BlueS2', 'GreenS2', 'RedS2', 'NIRS2', 'SWIR1S2', 'SWIR2S2', 'QA60', 'SCL']
  );
}

/* RMA transformation */
var rmaCoefficients = {
  itcpsL7: ee.Image.constant([-0.0084, -0.0065, 0.0022, -0.0768]),
  slopesL7: ee.Image.constant([1.1017, 1.0840, 1.0610, 1.2100]),
  itcpsS2: ee.Image.constant([0.0210, 0.0167, 0.0155, -0.0693]),
  slopesS2: ee.Image.constant([1.0849, 1.0590, 1.0759, 1.1583])
}; // #rma

function oli2oli(img) {
  return img.select(['Blue', 'Green', 'Red', 'NIR'])
            .toFloat();
}

function etm2oli(img) {
  return img.select(['Blue', 'Green', 'Red', 'NIR'])
    .multiply(rmaCoefficients.slopesL7)
    .add(rmaCoefficients.itcpsL7)
    .toFloat();
}
function s22oli(img) {
  return img.select(['Blue', 'Green', 'Red', 'NIR'])
    .multiply(rmaCoefficients.slopesS2)
    .add(rmaCoefficients.itcpsS2)
    .toFloat();
}

function imRangeFilter(image) {
  var maskMax = image.lte(1);
  var maskMin = image.gt(0);
  return image.updateMask(maskMax).updateMask(maskMin);
}

function aoiMask(image) {
  return image.updateMask(greenlandmask);
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
  return image.select(['Blue', 'Green', 'Red', 'NIR']).multiply(0.0000275).add(-0.2)
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
  return image.select(['Blue', 'Green', 'Red', 'NIR']).multiply(0.0000275).add(-0.2)
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

// narrow to broadband conversion
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


/* get harmonized image collection */

// Define function to prepare OLI images.
function prepOli(img) {
  var orig = img;
  img = renameOli(img);
  img = maskL8sr(img);
  img = oli2oli(img);
  //img = addTotalAlbedo(img);
  img = imRangeFilter(img);
  img = addVisnirAlbedo(img);
  return ee.Image(img.copyProperties(orig, orig.propertyNames()));
}
// Define function to prepare ETM+/TM images.
function prepEtm(img) {
  var orig = img;
  img = renameEtm(img);
  img = maskL457sr(img);
  img = etm2oli(img);
  //img = addTotalAlbedo(img);
  img = imRangeFilter(img);
  img = addVisnirAlbedo(img);
  return ee.Image(img.copyProperties(orig, orig.propertyNames()));
}
// Define function to prepare S2 images.
function prepS2(img) {
  var orig = img;
  img = renameS2(img);
  img = maskS2sr(img);
  img = s22oli(img);
  // img = addTotalAlbedo(img)
  img = imRangeFilter(img);
  img = addVisnirAlbedo(img);
  return ee.Image(img.copyProperties(orig, orig.propertyNames()).set('SATELLITE', 'SENTINEL_2'));
}


var date_start = ee.Date.fromYMD(1984, 1, 1),
    date_end = ee.Date(Date.now()),
    now = Date.now();
// ref: https://gist.github.com/jscarto/6cc7f547bb7d5d9acda51e5c15256b01
var blue_fluorite = ["#291b32", "#2a1b34", "#2b1b34", "#2d1c36", "#2f1c38", "#301c39", "#301d3a", "#321d3b", "#331d3d", "#351d3f", "#351e40", "#371e41", "#381e43", "#3a1e45", "#3b1f45", "#3c1f46", "#3e1f48", "#3f1f4a", "#401f4c", "#42204d", "#43204e", "#44204f", "#462051", "#472052", "#482054", "#4a2056", "#4a2157", "#4c2158", "#4e215a", "#4f215b", "#50215d", "#52215e", "#532160", "#552162", "#552263", "#562264", "#582265", "#592267", "#5b2268", "#5c226b", "#5e226c", "#5f226e", "#60226f", "#622271", "#632272", "#642274", "#662276", "#672277", "#692278", "#6a227a", "#6c227b", "#6e227d", "#6e237e", "#6f247f", "#702480", "#712581", "#722681", "#732683", "#742783", "#752884", "#762985", "#772987", "#792a87", "#792b88", "#7a2c89", "#7b2c8a", "#7c2d8a", "#7d2d8c", "#7e2e8d", "#7f2f8d", "#80308e", "#813190", "#823191", "#833292", "#843292", "#863393", "#863494", "#873595", "#893596", "#8a3697", "#8b3798", "#8b3899", "#8c389a", "#8e399b", "#8e3a9c", "#8f3b9c", "#8f3d9d", "#8f3e9e", "#903f9e", "#90419e", "#90439f", "#9044a0", "#9046a0", "#9047a1", "#9049a1", "#914aa2", "#914ca2", "#914ca3", "#914ea3", "#9150a4", "#9151a5", "#9153a5", "#9154a6", "#9156a6", "#9157a7", "#9258a7", "#9259a8", "#925aa8", "#925ba9", "#925da9", "#925faa", "#9260ab", "#9260ab", "#9263ac", "#9264ac", "#9265ad", "#9266ae", "#9268ae", "#9269ae", "#926aaf", "#926bb0", "#926cb0", "#926eb1", "#926fb1", "#9270b2", "#9271b2", "#9273b3", "#9274b3", "#9275b4", "#9277b5", "#9277b5", "#9278b6", "#927ab6", "#927bb7", "#927cb7", "#927eb8", "#927fb8", "#9280b9", "#9281ba", "#9282ba", "#9284bb", "#9285bb", "#9285bc", "#9187bc", "#9188bd", "#918abd", "#918bbe", "#918cbf", "#918dbf", "#918ec0", "#918fc0", "#9191c1", "#9092c2", "#9094c2", "#9094c2", "#9095c3", "#9096c3", "#8f99c4", "#8f9ac5", "#8f9ac5", "#8f9bc6", "#8f9cc6", "#8f9dc7", "#8e9fc8", "#8ea0c8", "#8ea2c9", "#8ea3c9", "#8da5ca", "#8da5ca", "#8da6cb", "#8da7cb", "#8ca9cc", "#8caacc", "#8caccd", "#8bacce", "#8badce", "#8baecf", "#8ab0d0", "#8ab2d0", "#8ab2d1", "#8ab4d1", "#89b4d1", "#89b5d2", "#89b7d2", "#88b8d3", "#88bad4", "#87bad4", "#87bbd5", "#86bdd6", "#86bed6", "#86c0d7", "#85c0d7", "#85c1d8", "#84c3d8", "#84c4d9", "#83c5d9", "#83c6da", "#82c8da", "#82c8db", "#81cadc", "#81cbdc", "#80ccdd", "#81cddd", "#84cfdd", "#85cfdd", "#87d0dd", "#8ad0de", "#8dd1de", "#8fd2de", "#90d2de", "#92d4de", "#95d5de", "#97d5de", "#98d6de", "#9bd7de", "#9dd7df", "#a0d8df", "#a1d9df", "#a2dadf", "#a5dadf", "#a7dbdf", "#aadcdf", "#abdddf", "#acdde0", "#afdfe0", "#b1dfe0", "#b3e0e0", "#b4e1e0", "#b7e2e0", "#bae2e1", "#bae3e1", "#bee3e2", "#c0e4e3", "#c1e5e3", "#c4e6e3", "#c6e6e4", "#c8e7e4", "#cbe7e5", "#cde8e5", "#cee9e6", "#d2e9e7", "#d3eae7", "#d5eae7", "#d8ebe8", "#d9ece8", "#dcece9", "#deedea", "#dfeeea", "#e2eeea", "#e5efeb", "#e6f0eb", "#e9f0ec", "#ebf1ed", "#ecf2ed", "#eff3ee", "#f1f3ee"];
var vis = {min: 0, max: 1, palette: blue_fluorite};


var l8img = prepOli(ee.Image('LANDSAT/LC08/C02/T1_L2/LC08_007013_20200721')).updateMask(greenlandmask);
var s2img = prepS2(ee.Image('COPERNICUS/S2_SR/20200721T144921_20200721T144924_T22WEV')).updateMask(greenlandmask);

// Compute standard deviation (SD) as texture of the NDVI.
var l8texture = l8img.select('visnirAlbedo').reduceNeighborhood({
    reducer: ee.Reducer.stdDev(),
    kernel: ee.Kernel.square(3), //default units in pixels
  });

// Compute standard deviation (SD) as texture of the NDVI.
var s2texture = s2img.select('visnirAlbedo').reduceNeighborhood({
  reducer: ee.Reducer.stdDev(),
  kernel: ee.Kernel.square(9), //default units in pixels
});  
var poi = ee.Geometry.Point(-48.8355, 67.067);

Map.addLayer(l8img.select('visnirAlbedo'), vis, 'l8albedo');
Map.addLayer(s2img.select('visnirAlbedo'), vis, 's2albedo');
// Map.addLayer(l8texture, {min: 0, max: 0.3}, 'SD of l8albedo');
// Map.addLayer(s2texture, {min: 0, max: 0.3}, 'SD of s2albedo');
Map.addLayer(poi, {}, 'kamm');
Map.addLayer(ktransect, {}, 'k-transect');

// Export the image, specifying the CRS, transform, and region.
Export.image.toDrive({
  image: l8img.select('visnirAlbedo'),
  description: 'l8img',
  // crs: projection.crs,
  // crsTransform: projection.transform,
  // region: geometry
});


// Export the image, specifying the CRS, transform, and region.
Export.image.toDrive({
  image: s2img.select('visnirAlbedo'),
  description: 's2img',
  // crs: projection.crs,
  // crsTransform: projection.transform,
  // region: geometry
});