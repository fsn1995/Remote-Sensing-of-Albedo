/*
This is the script of the earth engine app: Albedo Inspector.
It was developed to visualize the albedo product derived from the long time series of 
harmonized Landsat and Sentinel 2 data.

Users can interactively extract time series of albedo from point of interest and load the 
mosaic of natural color composite satellite image and the derived albedo. 
It's also possible to export and download a small subset of the albedo image. 

The app is inspired by:
https://google.earthengine.app/view/ocean.
https://gis.stackexchange.com/questions/344680/exporting-image-from-app-side-using-google-earth-engine by Justin Braaten
https://developers.google.com/earth-engine/tutorials/community/landsat-etm-to-oli-harmonization by Justin Braaten 
Shunna Feng (shunan.feng@envs.au.dk)
*/


/*
 * Map layer configuration
 */

// get aoi
var greenlandmask = ee.Image('OSU/GIMP/2000_ICE_OCEAN_MASK')
                      .select('ice_mask').eq(1); //'ice_mask', 'ocean_mask'
var aoi = /* color: #ffc82d */ee.Geometry.Polygon(
  [[[-36.29516924635421, 83.70737243835941],
    [-51.85180987135421, 82.75597137647488],
    [-61.43188799635421, 81.99879137488564],
    [-74.08813799635422, 78.10103528196419],
    [-70.13305987135422, 75.65372336709613],
    [-61.08032549635421, 75.71891096312955],
    [-52.20337237135421, 60.9795530382023],
    [-43.41430987135421, 58.59235996703347],
    [-38.49243487135421, 64.70478286561182],
    [-19.771731746354217, 69.72271161037442],
    [-15.728762996354217, 76.0828635948066],
    [-15.904544246354217, 79.45091003031243],
    [-10.015872371354217, 81.62328742628017],
    [-26.627200496354217, 83.43179828852398],
    [-31.636966121354217, 83.7553561747887]]]); // whole greenland



var arcticDEM = ee.Image('UMN/PGC/ArcticDEM/V3/2m_mosaic');


var elevationVis = {
  min: 0.0,
  max: 3000.0,
  palette: ['0d13d8', '60e1ff', 'ffffff'],
};    
var arcticDEMgreenland = arcticDEM.visualize(elevationVis).updateMask(greenlandmask);
var demLayer = ui.Map.Layer(arcticDEMgreenland).setName('arctic dem');


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


// Create the main map and add arctic dem as base map.
var mapPanel = ui.Map();
mapPanel.setOptions('HYBRID').setControlVisibility(true);
var layers = mapPanel.layers();
layers.add(demLayer, 'arctic dem');

// /*
// MODIS Albedo as gif, disabled by default
// */
// var modisCol = ee.ImageCollection('MODIS/006/MOD10A1')
//   .filterDate(ee.Date(Date.now()).advance(-7, 'day'), ee.Date(Date.now()).advance(0, 'day'))
//   .select('Snow_Albedo_Daily_Tile')
//   .map(function(img){
//     return img.updateMask(greenlandmask);
//   });

// // Define arguments for animation function parameters.
// var gifParams = {
//   dimensions: 768,
//   region: aoi,
//   framesPerSecond: 1,
//   crs: 'EPSG:3857',
//   min: 0,
//   max: 100,
//   palette: blue_fluorite
// };

// var gifAnimation = ui.Thumbnail({
//   image: modisCol,
//   params: gifParams,
//   style: {
//     position: 'bottom-right',
//     width: '200px',
//     height: '250px'
//   }
// });

// var gifPanel = ui.Panel({
//   widgets: [
//     ui.Label('MOD10A1.006 Snow_Albedo_Daily_Tile\nin the past week.',
//     {whiteSpace: 'pre'}),
//     gifAnimation
//   ],
//   style: {position: 'bottom-right'},
//   layout: null,
//   });
// mapPanel.add(gifPanel);

/*
 * Panel setup
 */

// Create a panel to hold title, intro text, chart and legend components.
var inspectorPanel = ui.Panel({style: {width: '30%'}});

// Create an intro panel with labels.
var intro = ui.Panel([
  ui.Label({
    value: 'Albedo - Time Series Inspector',
    style: {fontSize: '20px', fontWeight: 'bold'}
  }),
  ui.Label('Click a location to see its time series of albedo.')
]);
inspectorPanel.add(intro);

// Create panels to hold lon/lat values.
var lon = ui.Label();
var lat = ui.Label();
inspectorPanel.add(ui.Panel([lon, lat], ui.Panel.Layout.flow('horizontal')));

// Add placeholders for the chart and legend.
inspectorPanel.add(ui.Label('[Chart]'));
inspectorPanel.add(ui.Label('[Legend]'));


/*
 * Chart setup
 */

// Generates a new time series chart of SST for the given coordinates.
var generateChart = function (coords) {
  // Update the lon/lat panel with values from the click event.
  lon.setValue('lon: ' + coords.lon.toFixed(4));
  lat.setValue('lat: ' + coords.lat.toFixed(4));

  // Add a dot for the point clicked on.
  var point = ee.Geometry.Point(coords.lon, coords.lat);
  var dot = ui.Map.Layer(point, {color: '000000'}, 'clicked location');
  // Add the dot as the third layer, so it shows up on top of all layers.
  mapPanel.layers().set(3, dot);


  var colFilter = ee.Filter.and(
    ee.Filter.bounds(point),
    ee.Filter.date(date_start, date_end)
    // ee.Filter.calendarRange(6, 8, 'month')
  );
  
  var s2colFilter =  ee.Filter.and(
    ee.Filter.bounds(point),
    ee.Filter.date(date_start, date_end),
    // ee.Filter.calendarRange(6, 7, 'month'),
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
              .map(prepEtm)
              .select(['visnirAlbedo']); //# .select(['totalAlbedo']) or  .select(['visnirAlbedo'])
  var tm4Col = ee.ImageCollection('LANDSAT/LT04/C02/T1_L2') 
              .filter(colFilter) 
              .map(prepEtm)
              .select(['visnirAlbedo']); //# .select(['totalAlbedo']) or  .select(['visnirAlbedo'])
  var s2Col = ee.ImageCollection('COPERNICUS/S2_SR') 
              .filter(s2colFilter) 
              .map(prepS2)
              .select(['visnirAlbedo']); //# .select(['totalAlbedo']) or  .select(['visnirAlbedo'])
  
  var landsatCol = oliCol.merge(etmCol).merge(tmCol).merge(tm4Col);
  var multiSat = landsatCol.merge(s2Col).sort('system:time_start', true).map(imRangeFilter); // Sort chronologically in descending order.
  
  // Make a chart from the time series.
  var geeChart = ui.Chart.image.series(multiSat, point, ee.Reducer.mean(), 90);

  // Customize the chart.
  geeChart.setOptions({
    title: 'Albedo: time series',
    vAxis: {title: 'Albedo'},
    hAxis: {title: 'Date'},
    series: {
      0: {
        color: 'blue',
        lineWidth: 0,
        pointsVisible: true,
        pointSize: 2,
      },
    },
    legend: {position: 'right'},
  });
  // Add the chart at a fixed position, so that new charts overwrite older ones.
  inspectorPanel.widgets().set(2, geeChart);
};


/*
 * Legend setup
 */

// Creates a color bar thumbnail image for use in legend from the given color
// palette.
function makeColorBarParams(palette) {
  return {
    bbox: [0, 0, 1, 0.1],
    dimensions: '100x10',
    format: 'png',
    min: 0,
    max: 1,
    palette: palette,
  };
}

// Create the color bar for the legend.
var colorBar = ui.Thumbnail({
  image: ee.Image.pixelLonLat().select(0),
  params: makeColorBarParams(vis.palette),
  style: {stretch: 'horizontal', margin: '0px 8px', maxHeight: '24px'},
});
var colorBarDEM = ui.Thumbnail({
  image: ee.Image.pixelLonLat().select(0),
  params: makeColorBarParams(elevationVis.palette),
  style: {stretch: 'horizontal', margin: '0px 8px', maxHeight: '24px'},
});

// Create a panel with three numbers for the legend.
var legendLabels = ui.Panel({
  widgets: [
    ui.Label(vis.min, {margin: '4px 8px'}),
    ui.Label(
        (vis.max / 2),
        {margin: '4px 8px', textAlign: 'center', stretch: 'horizontal'}),
    ui.Label(vis.max, {margin: '4px 8px'})
  ],
  layout: ui.Panel.Layout.flow('horizontal')
});
var legendLabelsDEM = ui.Panel({
  widgets: [
    ui.Label(elevationVis.min, {margin: '4px 8px'}),
    ui.Label(
        (elevationVis.max / 2),
        {margin: '4px 8px', textAlign: 'center', stretch: 'horizontal'}),
    ui.Label(elevationVis.max, {margin: '4px 8px'})
  ],
  layout: ui.Panel.Layout.flow('horizontal')
});

var legendTitle = ui.Label({
  value: 'Map Legend: albedo',
  style: {fontWeight: 'bold'}
});
var legendTitleDEM = ui.Label({
  value: 'Map Legend: ArcticDEM (m)',
  style: {fontWeight: 'bold'}
});

var legendPanel = ui.Panel([legendTitle, colorBar, legendLabels, legendTitleDEM, colorBarDEM, legendLabelsDEM]);
inspectorPanel.widgets().set(3, legendPanel);

/*
 * Map setup
 */

// Register a callback on the default map to be invoked when the map is clicked.
mapPanel.onClick(generateChart);

// Configure the map.
mapPanel.style().set('cursor', 'crosshair');


// Initialize with a test point.
var initialPoint = ee.Geometry.Point(-50.3736, 71.1445); 
mapPanel.centerObject(initialPoint, 4);


/*
 * Initialize the app
 */

// Replace the root with a SplitPanel that contains the inspector and map.
ui.root.clear();
ui.root.add(ui.SplitPanel(inspectorPanel, mapPanel));
// ui.root.add(gifPanel);

generateChart({
  lon: initialPoint.coordinates().get(0).getInfo(),
  lat: initialPoint.coordinates().get(1).getInfo()
});


var dateIntro = ui.Panel([
  ui.Label({
    value: 'Albedo Map Date Selector',
    style: {fontSize: '20px', fontWeight: 'bold'}
  }),
  ui.Label("Change date (YYYY-MM-DD) to load the n-week albedo and natural color composite mosaic. Increase the week number would include more images but may take longer time. A button to download the albedo image will appear ONLY if: maximum request size < 32 MB and maximum grid dimension < 10000.")
]);
inspectorPanel.widgets().set(4, dateIntro);

// You can even add panels to other panels
var dropdownPanel = ui.Panel({
  layout: ui.Panel.Layout.flow('horizontal'),
});
inspectorPanel.widgets().set(5, dropdownPanel);

var yearSelector = ui.Select({
  placeholder: 'please wait..',
  });
var monthSelector = ui.Select({
  placeholder: 'please wait..',
  });
var daySelector = ui.Select({
  placeholder: 'please wait..',
  });
var weekSelector = ui.Select({
  placeholder: 'please wait..',
  });
var button = ui.Button('Load');
dropdownPanel.add(yearSelector);
dropdownPanel.add(monthSelector);
dropdownPanel.add(daySelector);
dropdownPanel.add(weekSelector);
dropdownPanel.add(button);
var urlLabel = ui.Label('Download', {shown: false});
dropdownPanel.add(urlLabel);

// Let's add a dropdown with the year month day and week
var years = ee.List.sequence( date_end.get('year'), date_start.get('year'), -1),
    months = ee.List.sequence(1, 12),
    days = ee.List.sequence(1, 31),
    weeks = ee.List.sequence(0.5, 4, 0.5);

// Dropdown items need to be strings
var yearStrings = years.map(function(year){
  return ee.Number(year).format('%04d');
});
var monthStrings = months.map(function(month){
  return ee.Number(month).format('%02d');
});
var dayStrings = days.map(function(day){
  return ee.Number(day).format('%02d');
});
var weekStrings = weeks.map(function(week){
  return ee.Number(week).format('%.1f');
});

// Evaluate the results and populate the dropdown
yearStrings.evaluate(function(yearList) {
  yearSelector.items().reset(yearList);
  yearSelector.setPlaceholder('select a year');
});

monthStrings.evaluate(function(monthList) {
  monthSelector.items().reset(monthList);
  monthSelector.setPlaceholder('select a month');
});

dayStrings.evaluate(function(dayList) {
  daySelector.items().reset(dayList);
  daySelector.setPlaceholder('select a day');
});

weekStrings.evaluate(function(weekList) {
  weekSelector.items().reset(weekList);
  weekSelector.setPlaceholder('select time step (week)');
});


// Define a function that triggers when any value is changed
var loadComposite = function() {
   
    var year = yearSelector.getValue(),
        month = monthSelector.getValue(),
        day = daySelector.getValue(),
        week = weekSelector.getValue();

    var startDate = ee.Date.fromYMD(
      ee.Number.parse(year), ee.Number.parse(month), ee.Number.parse(day));
    var endDate = startDate.advance(ee.Number.parse(week), 'week');

    var colFilter = ee.Filter.and(
      ee.Filter.bounds(aoi),
      ee.Filter.date(startDate, endDate)
      // ee.Filter.calendarRange(6, 8, 'month')
    );

    var s2colFilter =  ee.Filter.and(
      ee.Filter.bounds(aoi),
      ee.Filter.date(startDate, endDate),
      // ee.Filter.calendarRange(6, 7, 'month'),
      ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 50)
    );


    var oliCol = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2') 
                .filter(colFilter) 
                .map(prepOli);
                // .select(['visnirAlbedo']); //# .select(['totalAlbedo']) or  .select(['visnirAlbedo'])
    var etmCol = ee.ImageCollection('LANDSAT/LE07/C02/T1_L2') 
                .filter(ee.Filter.calendarRange(1999, 2020, 'year')) // filter out L7 imagaes acquired after 2020 due to orbit drift
                .filter(colFilter) 
                .map(prepEtm);
                // .select(['visnirAlbedo']); // # .select(['totalAlbedo']) or  .select(['visnirAlbedo'])
    var tmCol = ee.ImageCollection('LANDSAT/LT05/C02/T1_L2') 
                .filter(colFilter) 
                .map(prepEtm);
                // .select(['visnirAlbedo']); //# .select(['totalAlbedo']) or  .select(['visnirAlbedo'])
    var tm4Col = ee.ImageCollection('LANDSAT/LT04/C02/T1_L2') 
                .filter(colFilter) 
                .map(prepEtm);
                // .select(['visnirAlbedo']); //# .select(['totalAlbedo']) or  .select(['visnirAlbedo'])
    var s2Col = ee.ImageCollection('COPERNICUS/S2_SR') 
                .filter(s2colFilter) 
                .map(prepS2);
                // .select(['visnirAlbedo']); //# .select(['totalAlbedo']) or  .select(['visnirAlbedo'])

    var landsatCol = oliCol.merge(etmCol).merge(tmCol).merge(tm4Col);
    var multiSat = landsatCol.merge(s2Col).sort('system:time_start', true).map(imRangeFilter); // Sort chronologically in descending order.


    var rgblayerName = year + '-' + month + '-' + day;
    var rgbComposite = multiSat.select(['Red', 'Green', 'Blue']).mean().visualize(
      {
        min: 0,
        max: 1,
        bands:['Red', 'Green', 'Blue']
      }
    ).updateMask(greenlandmask);
    var rgbCompositeLayer = ui.Map.Layer(rgbComposite).setName(rgblayerName);
    mapPanel.layers().set(1, rgbCompositeLayer);

    var imgDownload = multiSat.select('visnirAlbedo').mean();
    var layerName = 'Albedo ' + year + '-' + month + '-' + day;
    var imgComposite = imgDownload.visualize(vis).updateMask(greenlandmask);
    var imgCompositeLayer = ui.Map.Layer(imgComposite).setName(layerName);
    // layers.add(imgCompositeLayer, layerName);
    mapPanel.layers().set(2, imgCompositeLayer);
    // Define a function to generate a download URL of the image for the
    // viewport region. 
    function downloadImg(img) {
      var viewBounds = ee.Geometry.Rectangle(mapPanel.getBounds());
      var downloadArgs = {
        name: 'ee_albedo',
        crs: 'EPSG:3857',
        scale: 30,
        region: viewBounds.toGeoJSONString()
    };
    var url = img.getDownloadURL(downloadArgs);
    return url;
}
urlLabel.setUrl(downloadImg(imgDownload));
urlLabel.style().set({shown: true});
};
button.onClick(loadComposite);


/*
add logo , ref: https://gis.stackexchange.com/questions/331842/adding-a-logo-to-a-panel-on-an-app-in-google-earth-engine
*/
var logo = ee.Image('projects/ee-deeppurple/assets/dplogo').visualize({
  bands:  ['b1', 'b2', 'b3'],
  min: 0,
  max: 255
  });
var thumb = ui.Thumbnail({
  image: logo,
  params: {
      dimensions: '107x111',
      format: 'png'
      },
  style: {height: '107px', width: '111px',padding :'0'}
  });
var logoPanel = ui.Panel(thumb, 'flow', {width: '120px'});
inspectorPanel.widgets().set(6, logoPanel);

var logoIntro = ui.Panel([
  ui.Label("The Deep Purple project receives funding from the European Research Council (ERC) under the European Union's Horizon 2020 research and innovation programme under grant agreement No 856416. This study is currently under review."),
  ui.Label("https://www.deeppurple-ercsyg.eu/home", {}, "https://www.deeppurple-ercsyg.eu/home"),
  ui.Label("https://github.com/fsn1995/Remote-Sensing-of-Albedo", {}, "https://github.com/fsn1995/Remote-Sensing-of-Albedo")
]);
inspectorPanel.widgets().set(7, logoIntro);