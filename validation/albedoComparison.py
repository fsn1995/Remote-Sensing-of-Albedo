# %%
from scipy import stats
import pandas as pd
import numpy as np
# import os
# import glob
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme(style="darkgrid")
# %%
df= pd.read_csv("awsAlbedo.csv")
sitename = "Haig Glacier"
df["datetime"] = pd.to_datetime(df.datetime)
df['month'] = df["datetime"].dt.month
index = (df['month'] < 10) & (df['month'] > 4) # north of Tropic of Cancer
# index = (df['month'] < 4) & (df['month'] > 10) # south of Tropic of Capricorn
df = df[index]

dfaws = df[df.site == sitename]
dfalbedo = pd.read_csv("satAlbedo\Haig Glacier.csv")
dfalbedo["datetime"] = pd.to_datetime(dfalbedo.datetime)

# %%
dfmerge = pd.merge_asof(
    dfalbedo.sort_values('datetime'),
    dfaws.sort_values('datetime'),
    on='datetime',
    allow_exact_matches=False,
    tolerance=pd.Timedelta(hours=1),
    direction='nearest'
).dropna()
# dfmerge.to_csv('albedomergeHMA.csv', mode="w", index=False, header=True)
# dfmerge.to_csv('albedomergeHMA.csv', mode="a", index=False, header=False)

# %%
# dfmerge = pd.read_csv("albedomergeHMA.csv")
slope, intercept, r_value, p_value, std_err = stats.linregress(dfmerge.visnirAlbedo.values, dfmerge.albedo.values)
print('OLS: \ny={0:.4f}x+{1:.4f}\nOLS_r:{2:.2f}, p:{3:.3f}'.format(slope,intercept,r_value,p_value))
# slope, intercept, r_value, p_value, std_err = stats.linregress(dfmerge.visnirAlbedo.values, dfmerge.albedoRaw.values)
# print('OLS: \ny={0:.4f}x+{1:.4f}\nOLS_r:{2:.2f}, p:{3:.3f}'.format(slope,intercept,r_value,p_value))

def nse(simulations, evaluation):
    """Nash-Sutcliffe Efficiency (NSE) as per `Nash and Sutcliffe, 1970
    <https://doi.org/10.1016/0022-1694(70)90255-6>`_.
    :Calculation Details:
        .. math::
           E_{\\text{NSE}} = 1 - \\frac{\\sum_{i=1}^{N}[e_{i}-s_{i}]^2}
           {\\sum_{i=1}^{N}[e_{i}-\\mu(e)]^2}
        where *N* is the length of the *simulations* and *evaluation*
        periods, *e* is the *evaluation* series, *s* is (one of) the
        *simulations* series, and *μ* is the arithmetic mean.
    https://github.com/ThibHlln/hydroeval/tree/v0.1.0
    Thibault Hallouin, 2021. hydroeval: an evaluator for streamflow time series in Python. https://doi.org/10.5281/zenodo.4709652        
    """
    nse_ = 1 - (
            np.sum((evaluation - simulations) ** 2, axis=0, dtype=np.float64)
            / np.sum((evaluation - np.mean(evaluation)) ** 2, dtype=np.float64)
    )

    return nse_

def ioa(simulations, evaluation):
    """Index of agreement
    
    """
    ioa_ = 1 - (
            np.sum((evaluation - simulations) ** 2, axis=0, dtype=np.float64)
            / np.sum(
                  (np.abs(simulations - np.mean(evaluation)) + np.abs(evaluation - np.mean(evaluation))) ** 2,
            dtype=np.float64)
    )

    return ioa_

def nse_modified(simulations, evaluation, j):
    """Nash-Sutcliffe Efficiency (NSE) Modified
    10.5194/adgeo-5-89-2005
    """
    nse_modified_ = 1 - (
            np.sum(
                  (np.abs(evaluation - simulations)) ** j , axis=0, dtype=np.float64
            )
            / np.sum(
                  (np.abs(evaluation - np.mean(evaluation))) ** j , dtype=np.float64
            )
    )

    return nse_modified_


nsecoefficient = nse(dfmerge["visnirAlbedo"].values, dfmerge["albedo"].values)  
nsecoefficientLog = nse(np.log(dfmerge["visnirAlbedo"].values), np.log(dfmerge["albedo"].values))

ioad = ioa(dfmerge["visnirAlbedo"].values, dfmerge["albedo"].values)  
nsem = nse_modified(dfmerge["visnirAlbedo"].values, dfmerge["albedo"].values, 1)  

print("nse coefficient is %.4f" % nsecoefficient)
print("nse coefficient (log) is %.4f" % nsecoefficientLog)
print("index of agreement is %.4f" % ioad)
print("nse modified is %.4f" % nsem)


# %%
fig, ax = plt.subplots(figsize=(5,5))
# plt.sca(ax1)

plt.xlim(0, 1)
plt.ylim(0, 1)

sns.set_theme(style="darkgrid", font="Arial", font_scale=1)
sns.regplot(data=dfmerge, x='visnirAlbedo', y='albedo')
ax.set(ylabel='AWS albedo')
ax.set_aspect('equal', 'box')

# %% alternative figure
# df = pd.read_excel("albedomerge.xlsx")
sns.set_theme(style="darkgrid", font="Arial", font_scale=2)
g = sns.jointplot(x="visnirAlbedo", y="albedo", data=dfmerge, kind="reg", 
                  height=8, xlim=(0,1), ylim=(0,1)) #, cbar=True, vmin=0, vmax=55
g.ax_joint.axline((0, 0), (1, 1), linewidth=1, color='k', linestyle='--')                       
# g.plot_joint(sns.regplot, color='r', scatter=False)
g.set_axis_labels(xlabel="visnir albedo", ylabel="AWS albedo")

# ref https://stackoverflow.com/a/60849048/13318759
# get the current positions of the joint ax and the ax for the marginal x
# pos_joint_ax = g.ax_joint.get_position()
# pos_marg_x_ax = g.ax_marg_x.get_position()
# # reposition the joint ax so it has the same width as the marginal x ax
# g.ax_joint.set_position([pos_joint_ax.x0, pos_joint_ax.y0, pos_marg_x_ax.width, pos_joint_ax.height])
# # reposition the colorbar using new x positions and y positions of the joint ax
# g.fig.axes[-1].set_position([.96, pos_joint_ax.y0, .07, pos_joint_ax.height])

g.savefig(r"C:\Users\au686295\Documents\GitHub\PhD\Remote-Sensing-of-Albedo\validation\print\HMA.png",
            dpi=300, bbox_inches="tight")
# g.savefig(r"C:\Users\au686295\Documents\GitHub\PhD\Remote-Sensing-of-Albedo\validation\print\Storglaciären.pdf",
#             dpi=300, bbox_inches="tight")

# %%
