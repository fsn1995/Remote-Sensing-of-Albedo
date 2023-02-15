# %%
import pandas as pd
import os
import glob
import matplotlib.pyplot as plt
import seaborn as sns

# %%
awsPath = r'C:\Users\au686295\Desktop\Tarfala\meteorological\AblationAWS\summer'
searchCriteria = "*.csv"

globInput = os.path.join(awsPath, searchCriteria)
awsCSVpath = glob.glob(globInput)
awsList = os.listdir(awsPath)

# %%
for i in range(len(awsList)):
    dfaws = pd.read_csv(awsCSVpath[i])
    dfaws["datetime"] = pd.to_datetime(dfaws["TIMESTAMP"])

    if i==0:
        dfaws.to_csv('ablationAWS.csv', mode='w', index=False)
    else:
        dfaws.to_csv('ablationAWS.csv', mode='a', index=False, header=False)


# %%
dfaws = pd.read_csv("ablationAWS.csv")
dfaws["albedo"] = dfaws.SWrefl_avg / dfaws.SW_avg
dfaws["datetime"] = pd.to_datetime(dfaws["datetime"])
dfaws = dfaws[["datetime", "albedo"]].dropna()
dfalbedo = pd.read_csv(r"AblationAWS\sat\30malbedo.csv")
dfalbedo["datetime"] = pd.to_datetime(dfalbedo["datetime"])

# %%
dfmerge = pd.merge_asof(
    dfalbedo.sort_values('datetime'),
    dfaws[dfaws.albedo<1].sort_values('datetime'),
    on='datetime',
    allow_exact_matches=False,
    tolerance=pd.Timedelta(hours=1),
    direction='nearest'
).dropna()
# dfmerge.to_excel('albedomerge.xlsx')

# %%
fig, ax = plt.subplots(figsize=(5,5))
# plt.sca(ax1)

plt.xlim(0, 1)
plt.ylim(0, 1)

sns.set_theme(style="darkgrid", font="Arial", font_scale=1)
sns.regplot(data=dfmerge, x='visnirAlbedo', y='albedo')
ax.set(ylabel='storglaciaren aws albedo')
ax.set_aspect('equal', 'box')

# %% alternative figure
df = pd.read_excel("albedomerge.xlsx")
sns.set_theme(style="darkgrid", font="Arial", font_scale=2)
g = sns.jointplot(x="visnirAlbedo", y="albedo", data=df, kind="reg", 
                  height=8, xlim=(0,1), ylim=(0,1)) #, cbar=True, vmin=0, vmax=55
g.ax_joint.axline((0, 0), (1, 1), linewidth=1, color='k', linestyle='--')                       
# g.plot_joint(sns.regplot, color='r', scatter=False)
g.set_axis_labels(xlabel="visnir albedo", ylabel="Storglaciären albedo")

# ref https://stackoverflow.com/a/60849048/13318759
# get the current positions of the joint ax and the ax for the marginal x
# pos_joint_ax = g.ax_joint.get_position()
# pos_marg_x_ax = g.ax_marg_x.get_position()
# # reposition the joint ax so it has the same width as the marginal x ax
# g.ax_joint.set_position([pos_joint_ax.x0, pos_joint_ax.y0, pos_marg_x_ax.width, pos_joint_ax.height])
# # reposition the colorbar using new x positions and y positions of the joint ax
# g.fig.axes[-1].set_position([.96, pos_joint_ax.y0, .07, pos_joint_ax.height])

g.savefig(r"C:\Users\au686295\Documents\GitHub\PhD\Remote-Sensing-of-Albedo\validation\print\Storglaciären.png",
            dpi=300, bbox_inches="tight")
g.savefig(r"C:\Users\au686295\Documents\GitHub\PhD\Remote-Sensing-of-Albedo\validation\print\Storglaciären.pdf",
            dpi=300, bbox_inches="tight")

# %%
