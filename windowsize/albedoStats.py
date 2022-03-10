# %%
import pandas as pd
import numpy as np
# import matplotlib.pyplot as plt
from scipy import stats
import seaborn as sns

# %%
listCSV = [
    "promice/promice vs satellite10m.csv",
    "promice/promice vs satellite20m.csv",
    "promice/promice vs satellite30m.csv",
    "promice/promice vs satellite60m.csv",
    "promice/promice vs satellite90m.csv",
    "promice/promice vs satellite150m.csv"
]

# %%
for i in listCSV:
    df = pd.read_csv(i).dropna()
    stat, p = stats.levene(df["Albedo_theta<70d"], df["visnirAlbedo"])
    print("%s test result is:" % i)
    print(stat)
    print(p)


# %%
albedo10m = pd.read_csv(listCSV[0]).dropna()
albedo20m = pd.read_csv(listCSV[1]).dropna()
albedo30m = pd.read_csv(listCSV[2]).dropna()
albedo60m = pd.read_csv(listCSV[3]).dropna()
albedo90m = pd.read_csv(listCSV[4]).dropna()
albedo150m = pd.read_csv(listCSV[5]).dropna()

#%%
stat, p = stats.levene(albedo60m.visnirAlbedo, albedo150m.visnirAlbedo)

# stat, p = stats.levene(albedo10m.visnirAlbedo, albedo20m.visnirAlbedo, albedo30m.visnirAlbedo,
#                        albedo60m.visnirAlbedo, albedo90m.visnirAlbedo, albedo150m.visnirAlbedo)
p

#%%


#%%
# albedomatrix = np.full([5139, len(listCSV)], np.nan)

# i=0
# for csvfile in listCSV:
#     df = pd.read_csv(csvfile).dropna
#     print(len(df.visnirAlbedo))
#     # albedomatrix[0:len(df.visnirAlbedo), i] = df.visnirAlbedo
#     i += 1
# %%
# stat, p = stats.bartlett(albedomatrix[:,0], albedomatrix[:,1], albedomatrix[:,2], 
#                          albedomatrix[:,3], albedomatrix[:,4], albedomatrix[:,5])
# stat, p = stats.bartlett(albedomatrix[:,1], albedomatrix[:,2], 
#                          albedomatrix[:,3], albedomatrix[:,4])

# stat, p = stats.levene(albedomatrix[:,0], albedomatrix[:,1], albedomatrix[:,2], 
#                        albedomatrix[:,3], albedomatrix[:,4], albedomatrix[:,5])          
# 
p               
# %%
# Generate a large random dataset
from string import ascii_letters
rs = np.random.RandomState(33)
d = pd.DataFrame(data=rs.normal(size=(100, 26)),
                 columns=list(ascii_letters[26:]))

# Compute the correlation matrix
corr = d.corr()
# %%
