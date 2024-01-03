# Remote Sensing of Ice Albedo with Google Earth Engine

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6257894.svg)](https://doi.org/10.5281/zenodo.6257894)
[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2Ffsn1995%2FRemote-Sensing-of-Albedo&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)](https://hits.seeyoufarm.com)

This is a github repo for remote sensing of ice/snow albedo using Google Earth Engine.
It is part of two studies:
1. Feng, S., Cook, J. M., Anesio, A. M., Benning, L. G., & Tranter, M. (2023). Long time series (1984–2020) of albedo variations on the Greenland ice sheet from harmonized Landsat and Sentinel 2 imagery. Journal of Glaciology, 69(277), 1225–1240. [https://doi.org/10.1017/jog.2023.11](https://doi.org/10.1017/jog.2023.11).
2. Feng, S., Cook, J. M., Onuma, Y., Naegeli, K., Tan, W., Anesio, A. M., Benning, L. G., & Tranter, M. (2023). Remote sensing of ice albedo using harmonized Landsat and Sentinel 2 datasets: validation. International Journal of Remote Sensing, 00(00), 1–29. [https://doi.org/10.1080/01431161.2023.2291000](https://doi.org/10.1080/01431161.2023.2291000).

Paper 1 focuses on the development of data harmonization and narrow to broad band conversion algorithm optimized for the ablation zone in the Greenland Ice Sheet. The harmonized satellite albedo (HSA) is further validated globally using AWS albedo measurements in paper 2. It also provides a complete workflow of validating remote sensing derived product with groundtruth measurements. 

A web application ([<b>Albedo Inspector</b>](https://fsn1995.users.earthengine.app/view/albedoinspector)) accompaniment to this repository is available. This web app allows users to extract time series of albedo and load the albedo maps freely in-browser.

## Background

This repository relates to the harmonization of Landsat and Sentinel-2 data and the development of a new narrowband to broadband conversion algorithm, both optimized to perform well across the Greenland Ice Sheet's melting zone - an area where previous data products have underperformed. The target area is the western coast of the Greenland Ice Sheet where a dark stripe forms each year due to the growth of algae on the ice surface, with as yet unquantified impacts on global sea level rise. The tools in this repository allow for long time-series of the albedo in this zone to be generated so that new insights into its spatio-temporal dynamics can be extracted.


## Data Harmonization Tutorial
- [script/harmonizationTutorial.js](script/harmonizationTutorial.js)

Here is a simple tutorial that demonstrates the importance of harmonizing Landsat 4-7, 9 and Sentinel 2 to Landsat 8 time series of datasets.
It will display the charts of the harmonized satellite albedo (All Observations) and original albedo (All Observations Original).
The linear trendline will be plotted on a separate chart. 
It can be used to determine whether data harmonziation is necessary or not, and to extract the time series of albedo at a specific location.

-[script/hsaImgFinder.js](script/hsaImgFinder.js)

This is a simple tutorial that demonstrates how to find the harmonized satellite albedo image for a specific date and location.
It will display the rgb and albedo image. It supports exporting the image to Google Drive as well.

<img src="media\harmonization.png" alt="harmonization" height=800/>

## How to use 

### Data Processing 

We will harmonize the Landsat Level 2 Collection 2 Tier 1 surface reflectance and Sentinel-2 MSI: MultiSpectral Instrument, Level-2A products and calculate the broadband albedo. 

#### Paired pixels
- [script/L7ToL8.js](script/L7ToL8.js)
- [script/S2ToL8.js](script/S2ToL8.js)
- [script/L9ToL8.js](script/L9ToL8.js)

The first step is to obtain the paired pixels for Landsat 7 vs Landsat 8, Landsat 9 vs Landsat 8, and Sentinel 2 vs Landsat 8 respectively.
Simply copy paste all lines of code into earth engine code editor: [https://code.earthengine.google.com/](https://code.earthengine.google.com/).
Paired images would be batch exported to Google Drive using the batch tools developed by Rodrigo E. Principe: https://github.com/fitoprincipe/geetools-code-editor/wiki. 

#### Band to band regression
- [script/regressionCompareL7L8.ipynb](script/regressionCompareL7L8.ipynb)
- [script/regressionCompareS2L8.ipynb](script/regressionCompareS2L8.ipynb)
- [script/regressionCompareL9L8.ipynb](script/regressionCompareL9L8.ipynb)

Two jupyter notebooks are available for the band to band regression. In this step we read the geotiff files from previous steps and convert the pixel values to vaex dataframe.
Both Ordinary Least Square (OLS) Regression Model and Reduced Major Axis Regression (RMA) Model.
RMA was calculated using the python package from https://github.com/OceanOptics/pylr2.

*Optionally*:
- [script/tif2hdf5.py](script/tif2hdf5.py)
- [script/regressionEvaluation.ipynb](script/regressionEvaluation.ipynb)

It would accelerate the processing by converting tif files to vaex dataframe in hdf5 format. The optional script and notebook here might be a good example. 

#### Narrow to broadband converstion
- [script/promicegee.ipynb](script/promicegee.ipynb)

This notebook first displays the location of PROMICE AWSs and calculated the annual velocity based on the GPS record.
Then it will extract the satellite pixel values and MODIS albedo prodcut at each AWS site.
Results will be saved in csv files under the promice folder. 
```python
pointValue = multiSat.getRegion(aoi, 90).getInfo() # The number (e.g. 90 here) is the window size (scale) in meters
```
The number is the window size when extracting pixel values. 

- [script/Promice vs satellite.ipynb](script/Promice%20vs%20satellite.ipynb)

Narrow to Broadband Conversion formula converts the surface reflectance to broadband albedo. We will run multiple linear regression models with different combination of bands. Reference albedo will also be calculated.

- [script/Promice vs satellite modis.ipynb](script/Promice%20vs%20satellite%20modis.ipynb)

This notebook evaluates the MODIS albedo product by comparing with PROMICE AWS albedo. 

### Spatial Window Size

The albedo images are exported by [windowsize/ktransectImage.js](windowsize/ktransectImage.js) and used for GLCM analysis [windowsize/glcm](windowsize/glcm).
The optimal spaital window size is done by following scripts:
- [windowsize/promiceAlbedo.py](windowsize/promiceAlbedo.py)
- [windowsize/albedoStats.py](windowsize/albedoStats.py) 
- [windowsize/albedoBias.py](windowsize/albedoBias.py), where different statistical measures are defined. 

### Validation with global AWS

The validation of albedo consists of 3 steps: 1) extraction of harmonized satellite albedo [validation/extractPoint.py](validation/extractPoint.py); 2) preparation of AWS data [validation/awsDataViewer.py](validation/awsDataViewer.py); and 3) validation [validation/albedoComparison.py](validation/albedoComparison.py).
Statistical measures such as the Nash-Sutcliffe Efficiency (NSE) and its modified forms, Index of agreement are all avaialble here. 

### Analysis and Mapping
#### Albedo Dynamics
- [script/darkzonePoint.ipynb](script/darkzonePoint.ipynb)
- [script/darkzone.ipynb](script/darkzone.ipynb)

Jupyter notebooks that investigate the albedo dynamics in the dark zone at both point and spatial scale. 

#### Albedo Mapping with QGIS
- [QGIS/albedoQGIS.py](QGIS/albedoQGIS.py)

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

## Citation
### Publication
```
@article{HSAJOGpaper2023,
   author = {Shunan Feng and Joseph Mitchell Cook and Alexandre Magno Anesio and Liane G. Benning and Martyn Tranter},
   doi = {10.1017/jog.2023.11},
   issn = {0022-1430},
   journal = {Journal of Glaciology},
   month = {3},
   pages = {1-16},
   title = {Long time series (1984–2020) of albedo variations on the Greenland ice sheet from harmonized Landsat and Sentinel 2 imagery},
   year = {2023},
}
```
Paper 2 is currently under review and will be updated once it's available. 
### Harmonized Satellite Albedo Product
Note: The doi number is provided by zenodo to cite all versions and will always resolve to the latest one. However, it may be different from the doi number in the publication as those were citing a specific version. 
```
@generic{hsajog,
   author = {Shunan Feng and Joseph M Cook},
   doi = {10.5281/zenodo.7642574},
   month = {2},
   publisher = {Zenodo},
   title = {Remote-Sensing-of-Albedo: Development of harmonized satellite albedo},
   url = {https://doi.org/10.5281/zenodo.7642574},
   year = {2023},
}

```

## Directory Structure

This project is organized into three main directories. `geemap` contains the javascript code for our web application. `QGIS` contains materials relating to our GIS work using QGIS. `script` contains jupyter notebooks, python and javascript scripts and related datasets for users to replicate our work. `windowsize` and `validation` are scripts for determining the optimal window size and validation with global AWS data. `media` is a repository for images and html for rendering our web app. 

```
|   LICENSE
|   README.md
|
+---geeapp
|       albedoInspectorAPP.js
|
+---media
|       allobs.svg
|       allobsori.svg
|       allobsoritrend.svg
|       geeapp.png
|       geeappdownload.png
|       harmonization.pdf
|       harmonization.png
|       qgis_editor.png
|       qgis_pybutton.png
|
+---QGIS
|       albedocolorbar.svg
|       albedoMap.qgz
|       albedoQGIS.py
|       albedoValidation.qgz
|       arcticdemQGIS.py
|       colorbar_horizontal.svg
|
+---script
|   |   bandtransform.xlsx
|   |   darkzone.ipynb
|   |   darkzonePoint.ipynb
|   |   geopyfsn.py
|   |   harmonizationTutorial.js       
|   |   hsaImgFinder.js 
|   |   L7ToL8.js
|   |   L9ToL8.js
|   |   Promice vs satellite modis.ipynb
|   |   Promice vs satellite.ipynb      
|   |   promicegee.ipynb
|   |   regressionCompareL7L8.ipynb     
|   |   regressionCompareL9L8.ipynb     
|   |   regressionCompareS2L8.ipynb     
|   |   regressionEvaluation.ipynb      
|   |   S2ToL8.js
|   |   satmission.py
|   |   tif2hdf5.py
|   |
|   +---promice
|   |       promice - qgis.csv
|   |       promice.csv
|   |       promice.xlsx
|   |
|   \---pylr2
|           regress2.py
|
+---validation
|   |   albedoComparison.py
|   |   albedomergeHMA.csv
|   |   albedomergeSA.csv
|   |   awsAlbedo.csv
|   |   awsDataViewer.py
|   |   extractPoint.py
|   |   insitu_list.csv
|   |   insitu_list.xlsx
|   |
\---windowsize
    |   albedoBias.py
    |   albedoStats.py
    |   ktransect.csv
    |   ktransect.py
    |   ktransectExtract.js
    |   ktransectFind.js
    |   ktransectImage.js
    |   ktransectplot.py
    |   ktransectQGIS.py
    |   l8panCNMF.m
    |   promiceAlbedo.py
    |   satellitedate.txt
    |   stacktif.m
    |   windowsize.xlsx
    |
    +---glcm
    |       spatialHomogeneityKAN.m
    |
   
```

