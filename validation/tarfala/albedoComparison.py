# %%
import pandas as pd
import os
import glob
import matplotlib.pyplot as plt
import seaborn as sns

# %%
awsPath = 'AblationAWS\summer'
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

# %%



