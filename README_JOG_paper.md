# Remote Sensing of Albedo on Greenland Ice Sheet with Google Earth Engine

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6257894.svg)](https://doi.org/10.5281/zenodo.6257894)
[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2Ffsn1995%2FRemote-Sensing-of-Albedo&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)](https://hits.seeyoufarm.com)

This is a github repo for remote sensing of ice/snow albedo using Google Earth Engine.
The manuscript is currently under review. 

A web application ([<b>Albedo Inspector</b>](https://fsn1995.users.earthengine.app/view/albedoinspector)) accompaniment to this repository is available. This web app allows users to extract time series of albedo and load the albedo maps freely in-browser.

## Background

This repository relates to the harmonization of Landsat and Sentinel-2 data and the development of a new narrowband to broadband conversion algorithm, both optimized to perform well across the Greenland Ice Sheet's melting zone - an area where previous data products have underperformed. The target area is the western coast of the Greenland Ice Sheet where a dark stripe forms each year due to the growth of algae on the ice surface, with as yet unquantified impacts on global sea level rise. The tools in this repository allow for long time-series of the albedo in this zone to be generated so that new insights into its spatio-temporal dynamics can be extracted.


## Data Harmonization Tutorial
- script\harmonizationTutorial.js

Here is a simple tutorial that demonstrates the importance of harmonizing Landsat 4-7 and Sentinel 2 to Landsat 8 time series of datasets.
It will display the charts of the harmonized satellite albedo (All Observations) and original albedo (All Observations Original).
The linear trendline will be plotted on a separate chart. 

<img src="media\harmonization.png" alt="harmonization" height=800/>

## How to use 

### Data Processing 

We will harmonize the Landsat Level 2 Collection 2 Tier 1 surface reflectance and Sentinel-2 MSI: MultiSpectral Instrument, Level-2A products and calculate the broadband albedo. 

#### Paired pixels
- script\L7ToL8.js
- script\S2ToL8.js

The first step is to obtain the paired pixels for Landsat 7 vs Landsat 8 and Sentinel 2 vs Landsat 8 respectively.
Simply copy paste all lines of code into earth engine code editor: [https://code.earthengine.google.com/](https://code.earthengine.google.com/).
Paired images would be batch exported to Google Drive using the batch tools developed by Rodrigo E. Principe: https://github.com/fitoprincipe/geetools-code-editor/wiki. 

#### Band to band regression
- script\regressionCompareL7L8.ipynb
- script\regressionCompareS2L8.ipynb

Two jupyter notebooks are available for the band to band regression. In this step we read the geotiff files from previous steps and convert the pixel values to vaex dataframe.
Both Ordinary Least Square (OLS) Regression Model and Reduced Major Axis Regression (RMA) Model.
RMA was calculated using the python package from https://github.com/OceanOptics/pylr2.

*Optionally*:
- script\tif2hdf5.py 
- script\regressionEvaluation.ipynb 

It would accelerate the processing by converting tif files to vaex dataframe in hdf5 format. The optional script and notebook here might be a good example. 

#### Narrow to broadband converstion
- script\promicegee.ipynb

This notebook first displays the location of PROMICE AWSs and calculated the annual velocity based on the GPS record.
Then it will extract the satellite pixel values and MODIS albedo prodcut at each AWS site.
Results will be saved in csv files under the promice folder. 
```python
pointValue = multiSat.getRegion(aoi, 90).getInfo() # The number (e.g. 90 here) is the window size (scale) in meters
```
The number is the window size when extracting pixel values. 

- script\Promice vs satellite.ipynb

Narrow to Broadband Conversion formula converts the surface reflectance to broadband albedo. We will run multiple linear regression models with different combination of bands. Reference albedo will also be calculated.

- script\Promice vs satellite modis.ipynb

This notebook evaluates the MODIS albedo product by comparing with PROMICE AWS albedo. 

### Analysis and Mapping
#### Albedo Dynamics
- script\darkzonePoint.ipynb
- script\darkzone.ipynb

Jupyter notebooks that investigate the albedo dynamics in the dark zone at both point and spatial scale. 

#### Albedo Mapping with QGIS
- QGIS\albedoQGIS.py

This part of script is to compare the spatial resolution of harmonized Landsat and Sentinel 2
albedo and MODIS albedo product.
Users will need QGIS and the qgis-earthengine-plugin: https://gee-community.github.io/qgis-earthengine-plugin/

Once QGIS and the earthengine-plugin are installed, users can open the python script and run in the python editor of QGIS.
You can change the time range here:
```python
#%% define date and area of interest
date_start = ee.Date.fromYMD(2015, 7, 15)
date_end = ee.Date.fromYMD(2015, 8, 15)
```

<p align="left">
  <img src="media\qgis_pybutton.png" alt="qgis_button" height=60/>
  <img src="media\qgis_editor.png" alt="qgis_editor" height=60/>
</p>

Then user could make a publication ready map by QGIS. 
Congrats! 


## Directory Structure

This project is organized into three main directories. `geemap` contains the javascript code for our web application. `QGIS` contains materials relating to our GIS work using QGIS. `script` contains jupyter notebooks, python and javascript scripts and related datasets for users to replicate our work. `media` is a repository for images and html for rendering our web app. 

```
├── geeapp
│   └── albedoInspectorAPP.js
├── LICENSE
├── media
│   ├── geeapp.png
│   ├── qgis_editor.png
│   ├── qgis_pybutton.png
│   ├── satelliteMission.html
│   └── satelliteSpectra.html
├── QGIS
│   ├── albedocolorbar.svg
│   ├── albedoMap.qgz
│   ├── albedoQGIS.py
│   └── colorbar_horizontal.svg
├── README.md
└── script
    ├── darkzone.ipynb
    ├── darkzonePoint.ipynb
    ├── geopyfsn.py
    ├── harmonizationTutorial.js
    ├── L7ToL8.js
    ├── promice
    │   ├── promice.csv
    │   └── promice.xlsx
    ├── promicegee.ipynb
    ├── Promice vs satellite.ipynb
    ├── Promice vs satellite modis.ipynb
    ├── pylr2
    │   └── regress2.py
    ├── regressionCompareL7L8.ipynb
    ├── regressionCompareS2L8.ipynb
    ├── regressionEvaluation.ipynb
    ├── S2TOL8.js
    └── tif2hdf5.py

```

## Permissions
Please cite Feng et al (in review) if this code or any downstream version of it is used to support a publication.
