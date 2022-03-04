// This is to help find the overlapping l8 and s2 images.

// get aoi
var greenlandmask = ee.Image('OSU/GIMP/2000_ICE_OCEAN_MASK')
                      .select('ice_mask').eq(1); //'ice_mask', 'ocean_mask'

// Define a pixel coordinate image.
var latLonImg = ee.Image.pixelLonLat();                      
var arcticDEM = ee.Image('UMN/PGC/ArcticDEM/V3/2m_mosaic').addBands(latLonImg);


var elevationVis = {
  min: 0.0,
  max: 3000.0,
  palette: ['0d13d8', '60e1ff', 'ffffff'],
};    
Map.addLayer(arcticDEM.updateMask(greenlandmask), elevationVis, 'arcticDEM');

var ktransect = ee.Geometry.LineString(
    [[-50.1, 67.083333], [-47, 67.083333]]
); 
Map.addLayer(ktransect, {}, 'k-transect');
Map.centerObject(ktransect, 10);

var elevTransect = arcticDEM.reduceRegion({
    reducer:ee.Reducer.toList(),
    geometry: ktransect,
    scale:10,
    tileScale:6
});

// Get longitude and elevation value lists from the reduction dictionary.
var lon = ee.List(elevTransect.get('longitude'));
var elev = ee.List(elevTransect.get('elevation'));

// Sort the longitude and elevation values by ascending longitude.
var lonSort = lon.sort(lon);
var elevSort = elev.sort(lon);

// Define the chart and print it to the console.
var chart = ui.Chart.array.values({array: elevSort, axis: 0, xLabels: lonSort})
                .setOptions({
                  title: 'Elevation Profile Across Longitude',
                  hAxis: {
                    title: 'Longitude',
                    viewWindow: {min: -124.50, max: -122.8},
                    titleTextStyle: {italic: false, bold: true}
                  },
                  vAxis: {
                    title: 'Elevation (m)',
                    titleTextStyle: {italic: false, bold: true}
                  },
                  colors: ['1d6b99'],
                  lineSize: 5,
                  pointSize: 0,
                  legend: {position: 'none'}
                });
print(chart);
