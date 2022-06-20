# %%
import pandas as pd
import seaborn as sns
import ee
import geemap
import matplotlib.pyplot as plt
import numpy as np

# %%
# %% display map
Map = geemap.Map()
Map

'''
get a profile of the k-transect
'''
# %%
latLonImg = ee.Image.pixelLonLat()
greenlandmask = ee.Image('OSU/GIMP/2000_ICE_OCEAN_MASK') \
                   .select('ice_mask').eq(1) #'ice_mask', 'ocean_mask'
arcticDEM = ee.Image('UMN/PGC/ArcticDEM/V3/2m_mosaic').addBands(latLonImg)
arcticDEMgreenland = arcticDEM.updateMask(greenlandmask)
visPara = {'min': 0,  'max': 3000.0, 'palette': ['0d13d8', '60e1ff', 'ffffff']}
Map.addLayer(arcticDEMgreenland.select('elevation'), visPara, 'arctic dem')

# %% define k transect
ktransect = ee.Geometry.LineString(
    [[-50.1, 67.083333], [-48, 67.083333]]
)
Map.addLayer(ktransect, {}, 'ktransect')
Map.center_object(ktransect, zoom=8)

# %% get the elevation profile
elevTransect = arcticDEMgreenland.reduceRegion(**{
    'reducer': ee.Reducer.toList(),
    'geometry': ktransect,
    'scale': 10,
    'tileScale': 6
})
dfdem = pd.DataFrame(elevTransect.getInfo())
# %% plot the profile
sns.set_theme()
dfdem = dfdem.sort_values("longitude")
dfdem.plot.area(x="longitude", y='elevation')



# %% ktransect albedo
df = pd.read_csv("ktransect.csv")
df.rename(columns={
    'std3': 'std30m',
    'std5': 'std50m',
    'std9': 'std90m',
    'std15': 'std150m'
}, inplace=True)
df.std30m[df.satellite=="Landsat"] = np.nan
df.std50m[df.satellite=="Landsat"] = np.nan
df["datetime"] = pd.to_datetime(df.time, unit="ms")
df["year"] = df.datetime.dt.year
df["month"] = df.datetime.dt.month
df["day"] = df.datetime.dt.day
df = df[(df.month>4) & (df.month<10) & (df.visnirAlbedo<1)]

dfnew = df.groupby(by=["year", "longitude"]).mean()
dfnew.reset_index(inplace=True)
  
sns.set_theme(font="Arial", font_scale=2)                 
fig = sns.relplot(
    data=dfnew, 
    x="longitude",
    y="visnirAlbedo",
    hue="year",
    kind="line",
    height=8,
    aspect=2,
)
figlegend = fig._legend
figlegend.set_bbox_to_anchor([0.25, 0.8])
axes = fig.axes.flatten()
for ax in axes:
    ax2 = ax.twinx()
    dfdem.plot(x="longitude", y="elevation", legend=False, ax=ax2)
    ax2.set(ylabel="elevation m.a.s.l")

fig.savefig("print/ktransectAlbedoProfile.png", dpi=300, bbox_inches="tight")
# %%
dfmelt = pd.melt(df, id_vars=["year", "month", "day"],
                 value_vars=["std30m", "std50m", "std90m", "std150m"],
                 var_name="scales",
                 value_name="stddev")


fig, ax = plt.subplots(figsize=(6, 5))                 
sns.set_theme(font="Arial", font_scale=2)                 
sns.boxplot(
    data=dfmelt, x="month", y="stddev", hue="scales",
    ax=ax
)
plt.legend(bbox_to_anchor=(1.1, 1.3), ncol=2)
fig.savefig("print/ktransectSTDbox.png", dpi=300, bbox_inches="tight")
# sns.relplot(
#     data=df, 
#     x="longitude",
#     y="visnirAlbedo",
#     col="year",
#     row="month",
#     kind="line"
# )
# %% group by month
df = pd.read_csv("ktransect.csv")
df["datetime"] = pd.to_datetime(df.time, unit="ms")
df["year"] = df.datetime.dt.year
df["month"] = df.datetime.dt.month
df["day"] = df.datetime.dt.day
df = df[(df.month>5) & (df.month<10) & (df.visnirAlbedo<1)]

dfnew = df.groupby(by=["year", "month", "longitude"]).mean()
dfnew.reset_index(inplace=True)
# %%
sns.set_theme(font="Arial", font_scale=2)
fig = sns.relplot(
    data=dfnew, 
    x="longitude",
    y="std9",
    hue="year",
    row="month",
    kind="line",
    height=8,
    aspect=2
)
figlegend = fig._legend
figlegend.set_bbox_to_anchor([0.25, 0.9])
axes = fig.axes.flatten()
for ax in axes:
    ax.set_ylim(0, 0.25)
    ax.set(ylabel="std90m")
    ax2 = ax.twinx()
    dfdem.plot(x="longitude", y="elevation", legend=False, ax=ax2)
    ax2.set(ylabel="elevation m.a.s.l")

fig.savefig("print/ktransectSTDprofile.png", dpi=300, bbox_inches="tight")
fig.savefig("print/ktransectSTDprofile.pdf", dpi=300, bbox_inches="tight")
    # # The math
    # ylim1 = ax.get_ylim()
    # len1 = ylim1[1]-ylim1[0]
    # yticks1 = ax.get_yticks()
    # rel_dist = [(y-ylim1[0])/len1 for y in yticks1]
    # ylim2 = ax2.get_ylim()
    # len2 = ylim2[1]-ylim2[0]
    # yticks2 = [ry*len2+ylim2[0] for ry in rel_dist]

    # #My best attempt
    # ax2.set_yticks(yticks2)
    # ax2.set_ylim(ylim2)  #<-- this line is needed to re-adjust the limits to the orig

# %%
