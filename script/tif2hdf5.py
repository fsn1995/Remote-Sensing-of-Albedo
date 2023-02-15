'''
This script converts the geotiff files of paired images to vaex dataframe saved in hdf5 format. 

Shunan Feng (shunan.feng@envs.au.dk)
'''
# %%
import vaex as vx
from geopyfsn import getBandNoFilter

# %% [markdown]
# # landsat 7 vs landsat 8

# %%
bluePath = r"/data/shunan/data/harmonize_data/201305_08landsat/blue"
greenPath = r"/data/shunan/data/harmonize_data/201305_08landsat/green"
redPath = r"/data/shunan/data/harmonize_data/201305_08landsat/red"
nirPath = r"/data/shunan/data/harmonize_data/201305_08landsat/nir"
swir1Path = r"/data/shunan/data/harmonize_data/201305_08landsat/swir1"
swir2Path = r"/data/shunan/data/harmonize_data/201305_08landsat/swir2"


# %%
L8, L7 = getBandNoFilter(bluePath)
some_dict = {'L8blue': L8, 'L7blue': L7}
blue = vx.from_arrays(**some_dict)
blue.export_hdf5(r'/data/shunan/data/harmonize_data/201305_08landsat/blue.hdf5', progress=True)
del L8, L7, blue


# %%
L8, L7 = getBandNoFilter(greenPath)
some_dict = {'L8green': L8, 'L7green': L7}
green = vx.from_arrays(**some_dict)
green.export_hdf5(r'/data/shunan/data/harmonize_data/201305_08landsat/green.hdf5', progress=True)
del L8, L7, green


# %%
L8, L7 = getBandNoFilter(redPath)
some_dict = {'L8red': L8, 'L7red': L7}
red = vx.from_arrays(**some_dict)
red.export_hdf5(r'/data/shunan/data/harmonize_data/201305_08landsat/red.hdf5', progress=True)
del L8, L7, red


# %%
L8, L7 = getBandNoFilter(nirPath)
some_dict = {'L8nir': L8, 'L7nir': L7}
nir = vx.from_arrays(**some_dict)
nir.export_hdf5(r'/data/shunan/data/harmonize_data/201305_08landsat/nir.hdf5', progress=True)
del L8, L7, nir


# %%
L8, L7 = getBandNoFilter(swir1Path)
some_dict = {'L8swir1': L8, 'L7swir1': L7}
swir1 = vx.from_arrays(**some_dict)
swir1.export_hdf5(r'/data/shunan/data/harmonize_data/201305_08landsat/swir1.hdf5', progress=True)
del L8, L7, swir1


# %%
L8, L7 = getBandNoFilter(swir2Path)
some_dict = {'L8swir2': L8, 'L7swir2': L7}
swir2 = vx.from_arrays(**some_dict)
swir2.export(r'/data/shunan/data/harmonize_data/201305_08landsat/swir2.hdf5', progress=True)
del L8, L7, swir2

# %% [markdown]
# # sentinel 2 vs landsat 8

# %%

bluePath = r"/data/shunan/data/harmonize_data/202005_08sentinel/blue"
greenPath = r"/data/shunan/data/harmonize_data/202005_08sentinel/green"
redPath = r"/data/shunan/data/harmonize_data/202005_08sentinel/red"
nirPath = r"/data/shunan/data/harmonize_data/202005_08sentinel/nir"
swir1Path = r"/data/shunan/data/harmonize_data/202005_08sentinel/swir1"
swir2Path = r"/data/shunan/data/harmonize_data/202005_08sentinel/swir2"


# %%
L8, S2 = getBandNoFilter(bluePath)
some_dict = {'L8blue': L8, 'S2blue': S2}
blue = vx.from_arrays(**some_dict)
blue.export_hdf5(r'/data/shunan/data/harmonize_data/202005_08sentinel/blue.hdf5', progress=True)
del L8, S2, blue


# %%
L8, S2 = getBandNoFilter(greenPath)
some_dict = {'L8green': L8, 'S2green': S2}
green = vx.from_arrays(**some_dict)
green.export_hdf5(r'/data/shunan/data/harmonize_data/202005_08sentinel/green.hdf5', progress=True)
del L8, S2, green


# %%
L8, S2 = getBandNoFilter(redPath)
some_dict = {'L8red': L8, 'S2red': S2}
red = vx.from_arrays(**some_dict)
red.export_hdf5(r'/data/shunan/data/harmonize_data/202005_08sentinel/red.hdf5', progress=True)
del L8, S2, red


# %%
L8, S2 = getBandNoFilter(nirPath)
some_dict = {'L8nir': L8, 'S2nir': S2}
nir = vx.from_arrays(**some_dict)
nir.export_hdf5(r'/data/shunan/data/harmonize_data/202005_08sentinel/nir.hdf5', progress=True)
del L8, S2, nir


# %%
L8, S2 = getBandNoFilter(swir1Path)
some_dict = {'L8swir1': L8, 'S2swir1': S2}
swir1 = vx.from_arrays(**some_dict)
swir1.export_hdf5(r'/data/shunan/data/harmonize_data/202005_08sentinel/swir1.hdf5', progress=True)
del L8, S2, swir1


# %%
L8, S2 = getBandNoFilter(swir2Path)
some_dict = {'L8swir2': L8, 'S2swir2': S2}
swir2 = vx.from_arrays(**some_dict)
swir2.export_hdf5(r'/data/shunan/data/harmonize_data/202005_08sentinel/swir2.hdf5', progress=True)
del L8, S2, swir2


# %% [markdown]
# # landsat 9 vs landsat 8

# %%

bluePath = r"/data/shunan/data/harmonize_data/202205_08landsat/blue"
greenPath = r"/data/shunan/data/harmonize_data/202205_08landsat/green"
redPath = r"/data/shunan/data/harmonize_data/202205_08landsat/red"
nirPath = r"/data/shunan/data/harmonize_data/202205_08landsat/nir"
swir1Path = r"/data/shunan/data/harmonize_data/202205_08landsat/swir1"
swir2Path = r"/data/shunan/data/harmonize_data/202205_08landsat/swir2"


# %%
L8, L9 = getBandNoFilter(bluePath)
some_dict = {'L8blue': L8, 'L9blue': L9}
blue = vx.from_arrays(**some_dict)
blue.export_hdf5(r'/data/shunan/data/harmonize_data/202205_08landsat/blue.hdf5', progress=True)
del L8, L9, blue


# %%
L8, L9 = getBandNoFilter(greenPath)
some_dict = {'L8green': L8, 'L9green': L9}
green = vx.from_arrays(**some_dict)
green.export_hdf5(r'/data/shunan/data/harmonize_data/202205_08landsat/green.hdf5', progress=True)
del L8, L9, green


# %%
L8, L9 = getBandNoFilter(redPath)
some_dict = {'L8red': L8, 'L9red': L9}
red = vx.from_arrays(**some_dict)
red.export_hdf5(r'/data/shunan/data/harmonize_data/202205_08landsat/red.hdf5', progress=True)
del L8, L9, red


# %%
L8, L9 = getBandNoFilter(nirPath)
some_dict = {'L8nir': L8, 'L9nir': L9}
nir = vx.from_arrays(**some_dict)
nir.export_hdf5(r'/data/shunan/data/harmonize_data/202205_08landsat/nir.hdf5', progress=True)
del L8, L9, nir


# %%
L8, L9 = getBandNoFilter(swir1Path)
some_dict = {'L8swir1': L8, 'L9swir1': L9}
swir1 = vx.from_arrays(**some_dict)
swir1.export_hdf5(r'/data/shunan/data/harmonize_data/202205_08landsat/swir1.hdf5', progress=True)
del L8, L9, swir1


# %%
L8, L9 = getBandNoFilter(swir2Path)
some_dict = {'L8swir2': L8, 'L9swir2': L9}
swir2 = vx.from_arrays(**some_dict)
swir2.export_hdf5(r'/data/shunan/data/harmonize_data/202205_08landsat/swir2.hdf5', progress=True)
del L8, L9, swir2
# %%
