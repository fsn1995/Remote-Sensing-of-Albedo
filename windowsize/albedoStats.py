# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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
stat, p = stats.levene(albedo20m.visnirAlbedo, albedo10m.visnirAlbedo)

# stat, p = stats.levene(albedo10m.visnirAlbedo, albedo20m.visnirAlbedo, albedo30m.visnirAlbedo,
#                        albedo60m.visnirAlbedo, albedo90m.visnirAlbedo, albedo150m.visnirAlbedo)
p

# %% make a diagonal correlation matrix plot
# https://seaborn.pydata.org/examples/many_pairwise_correlations.html

df = pd.read_excel("windowsize.xlsx", sheet_name="levene", index_col=[0])

mask = np.triu(np.ones_like(df, dtype=bool))
sns.set_theme(style="white", font="Arial", font_scale=2)
fig, ax = plt.subplots(figsize=(9,7))

cmap = sns.diverging_palette(240, 10, as_cmap=True)

# Draw the heatmap with the mask and correct aspect ratio
sns.heatmap(df, mask=mask, cmap=cmap, vmin=0, vmax=1, center=0, annot=True, annot_kws={"size": "small"},
            square=True, linewidths=.5, cbar_kws={"shrink": .8, "label": "Levene's test p-value"}, ax=ax)
fig.savefig("print/leveneHeatmap.pdf", dpi=300, bbox_inches="tight")            
# %%
