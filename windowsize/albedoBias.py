# %%
import pandas as pd
import os
import glob
# import matplotlib.pyplot as plt
from scipy import stats
import seaborn as sns
from sklearn.metrics import mean_squared_error


# %%

# '''
# obtain the albedo and promice station data
# '''

# df = pd.read_csv('/data/shunan/github/Remote-Sensing-of-Albedo/script/promice/promice.csv')
# df['Longitude'] = df['Longitude'] * -1

# folderpath = "/data/shunan/github/Remote-Sensing-of-Albedo/windowsize/promice/multiSat150m"

# searchCriteria = "*.csv"
# globInput = os.path.join(folderpath, searchCriteria)
# csvPath = glob.glob(globInput)
# csvList = os.listdir(folderpath)

# #%%
# # hourly
# for i in range(len(csvList)):
#     # promice data
#     stationName = os.path.splitext(csvList[i])[0].replace("-", "*")
#     index = df.index[df.Station == stationName][0]
#     url = df.urlhourly[index]
#     dfs = pd.read_table(url, sep=r'\s{1,}', engine='python')

#     dfs = dfs[['Albedo_theta<70d', 'Year', 'MonthOfYear','DayOfMonth', 'HourOfDay(UTC)', 'CloudCover']]
#     dfs['datetime'] = pd.to_datetime(dict(year=dfs.Year, month=dfs.MonthOfYear, day = dfs.DayOfMonth, hour = dfs['HourOfDay(UTC)']))
#     # cloud cover less than 50% and albedo must be valid value
#     dfs = dfs[(dfs['Albedo_theta<70d'] > 0) & (dfs['Albedo_theta<70d'] < 1) & (dfs['CloudCover'] < 0.5)] 
#     dfs['Station'] = stationName

#     # satellite data
#     dfr = pd.read_csv(csvPath[i])
#     # dfr.datetime = pd.to_datetime(dfr.datetime).dt.date # keep only ymd
#     dfr.datetime = pd.to_datetime(dfr.datetime)
#     # join by datetime
#     dfmerge = pd.merge_asof(dfr.sort_values('datetime'), dfs.dropna().sort_values('datetime'), on='datetime',allow_exact_matches=False, tolerance=pd.Timedelta(hours=1),direction='nearest' )
#     # dfmerge = pd.merge_asof(dfr.sort_values('datetime'), dfs, on='datetime', tolerance=pd.Timedelta(hours=1) )
#     if i==0:
#         dfmerge.to_csv('/data/shunan/github/Remote-Sensing-of-Albedo/windowsize/promice/promice vs satellite150m.csv', mode='w', index=False)
#     else:
#         dfmerge.to_csv('/data/shunan/github/Remote-Sensing-of-Albedo/windowsize/promice/promice vs satellite150m.csv', mode='a', index=False, header=False)
# %% 
#  Plot
# 
# 
# # %% different scales

df = pd.read_csv('/data/shunan/github/Remote-Sensing-of-Albedo/windowsize/promice/promice vs satellite150m.csv').dropna()
slope, intercept, r_value, p_value, std_err = stats.linregress(df.visnirAlbedo, df["Albedo_theta<70d"])
df['bias'] = df["visnirAlbedo"] - df["Albedo_theta<70d"]
df.datetime = pd.to_datetime(df.datetime)
df['doy'] = df['datetime'].dt.dayofyear

#%% different scale plots
sns.set_theme(style="darkgrid", font="Arial", font_scale=2)
g = sns.jointplot(x="visnirAlbedo", y="Albedo_theta<70d", data=df, kind="hist", 
                  height=8, xlim=(0,1), ylim=(0,1))
g.ax_joint.axline((0, 0), (1, 1), linewidth=1, color='k', linestyle='--')                       
g.plot_joint(sns.regplot, color='r', scatter=False)
g.set_axis_labels(xlabel="visnir albedo", ylabel="PROMICE albedo")
g.savefig("/data/shunan/github/Remote-Sensing-of-Albedo/windowsize/promice/albedo150m.png",
            dpi=300, bbox_inches="tight")
print('ALL: \ny={0:.4f}x+{1:.4f}\nr_value:{2:.2f} \np:{3:.3f} \nstd_err:{4:.4f}'
      .format(slope,intercept,r_value,p_value, std_err))
print('Total RMSE is %.4f' % (mean_squared_error(df["Albedo_theta<70d"], df["visnirAlbedo"], squared=False)))
print("average bias is: %.4f" % df.bias.mean())
# %% bias plot
sns.set_theme(style="darkgrid", font="Arial", font_scale=1)
g = sns.FacetGrid(data=df, col="Station", col_wrap=4, legend_out=True)
g.map(sns.regplot, "doy", "bias")
g.add_legend()
g.refline(y=0)    

# ax = g.axes[0]
# ax.annotate('n:%.0f' % (len(df.L8.values)), xy=(0.7, 0.1),  xycoords='data',
#             horizontalalignment='left', verticalalignment='top',
#             )

g.savefig("/data/shunan/github/Remote-Sensing-of-Albedo/windowsize/promice/bias150m.png",
            dpi=600, bbox_inches="tight")
# %% ryan 2017 

df = df[(df.Station=="KAN_L") | (df.Station=="KAN_M") | (df.Station=="KAN_U") ]

# %%
sns.set_theme(style="darkgrid", font="Arial", font_scale=2)
g = sns.FacetGrid(data=df.sort_values("Station"), col="Station", col_wrap=3, 
                 legend_out=True, size=6)
g.map(sns.regplot, "doy", "bias")
g.add_legend()
g.refline(y=0)    
# %%
dfsubset = df[(df.Station=="KAN_L") | (df.Station=="KAN_M")]
# RMSE
print('Total RMSE is %.4f' % (mean_squared_error(dfsubset["Albedo_theta<70d"], dfsubset["visnirAlbedo"], squared=False)))
print("mean bias is %.4f" % dfsubset.bias.mean())
dfsubsetM = dfsubset[(dfsubset["MonthOfYear"] == 4) | (dfsubset["MonthOfYear"] == 5)]
print('April/May RMSE is %.4f' % (mean_squared_error(dfsubsetM["Albedo_theta<70d"], dfsubsetM["visnirAlbedo"], squared=False)))
print("mean bias is %.4f" % dfsubsetM.bias.mean())
dfsubsetM = dfsubset[dfsubset["MonthOfYear"] == 6]
print('June RMSE is %.4f' % (mean_squared_error(dfsubsetM["Albedo_theta<70d"], dfsubsetM["visnirAlbedo"], squared=False)))
print("mean bias is %.4f" % dfsubsetM.bias.mean())
dfsubsetM = dfsubset[dfsubset["MonthOfYear"] == 7]
print('July RMSE is %.4f' % (mean_squared_error(dfsubsetM["Albedo_theta<70d"], dfsubsetM["visnirAlbedo"], squared=False)))
print("mean bias is %.4f" % dfsubsetM.bias.mean())
dfsubsetM = dfsubset[dfsubset["MonthOfYear"] == 8]
print('August RMSE is %.4f' % (mean_squared_error(dfsubsetM["Albedo_theta<70d"], dfsubsetM["visnirAlbedo"], squared=False)))
print("mean bias is %.4f" % dfsubsetM.bias.mean())


dfsubset = df[df.Station=="KAN_L"]
# RMSE
print('KAN_L RMSE is %.4f' % (mean_squared_error(dfsubset["Albedo_theta<70d"], dfsubset["visnirAlbedo"], squared=False)))
print("mean bias is %.4f" % dfsubset.bias.mean())
dfsubsetM = dfsubset[(dfsubset["MonthOfYear"] == 4) | (dfsubset["MonthOfYear"] == 5)]
print('April/May RMSE is %.4f' % (mean_squared_error(dfsubsetM["Albedo_theta<70d"], dfsubsetM["visnirAlbedo"], squared=False)))
print("mean bias is %.4f" % dfsubsetM.bias.mean())
dfsubsetM = dfsubset[dfsubset["MonthOfYear"] == 6]
print('June RMSE is %.4f' % (mean_squared_error(dfsubsetM["Albedo_theta<70d"], dfsubsetM["visnirAlbedo"], squared=False)))
print("mean bias is %.4f" % dfsubsetM.bias.mean())
dfsubsetM = dfsubset[dfsubset["MonthOfYear"] == 7]
print('July RMSE is %.4f' % (mean_squared_error(dfsubsetM["Albedo_theta<70d"], dfsubsetM["visnirAlbedo"], squared=False)))
print("mean bias is %.4f" % dfsubsetM.bias.mean())
dfsubsetM = dfsubset[dfsubset["MonthOfYear"] == 8]
print('August RMSE is %.4f' % (mean_squared_error(dfsubsetM["Albedo_theta<70d"], dfsubsetM["visnirAlbedo"], squared=False)))
print("mean bias is %.4f" % dfsubsetM.bias.mean())



dfsubset = df[df.Station=="KAN_M"]
# RMSE
print('KAN_M RMSE is %.4f' % (mean_squared_error(dfsubset["Albedo_theta<70d"], dfsubset["visnirAlbedo"], squared=False)))
print("mean bias is %.4f" % dfsubset.bias.mean())
dfsubsetM = dfsubset[(dfsubset["MonthOfYear"] == 4) | (dfsubset["MonthOfYear"] == 5)]
print('April/May RMSE is %.4f' % (mean_squared_error(dfsubsetM["Albedo_theta<70d"], dfsubsetM["visnirAlbedo"], squared=False)))
print("mean bias is %.4f" % dfsubsetM.bias.mean())
dfsubsetM = dfsubset[dfsubset["MonthOfYear"] == 6]
print('June RMSE is %.4f' % (mean_squared_error(dfsubsetM["Albedo_theta<70d"], dfsubsetM["visnirAlbedo"], squared=False)))
print("mean bias is %.4f" % dfsubsetM.bias.mean())
dfsubsetM = dfsubset[dfsubset["MonthOfYear"] == 7]
print('July RMSE is %.4f' % (mean_squared_error(dfsubsetM["Albedo_theta<70d"], dfsubsetM["visnirAlbedo"], squared=False)))
print("mean bias is %.4f" % dfsubsetM.bias.mean())
dfsubsetM = dfsubset[dfsubset["MonthOfYear"] == 8]
print('August RMSE is %.4f' % (mean_squared_error(dfsubsetM["Albedo_theta<70d"], dfsubsetM["visnirAlbedo"], squared=False)))
print("mean bias is %.4f" % dfsubsetM.bias.mean())




# %% Individual AWS
dfsubset = df[df.Station=="KAN_L"]
slope, intercept, r_value, p_value, std_err = stats.linregress(dfsubset["doy"], dfsubset["bias"])
print('KAN_L: \ny={0:.4f}x+{1:.4f}\nr_value:{2:.2f} \np:{3:.3f}'.format(slope,intercept,r_value,p_value))


dfsubset = df[df.Station=="KAN_M"]
slope, intercept, r_value, p_value, std_err = stats.linregress(dfsubset["doy"], dfsubset["bias"])
print('KAN_M: \ny={0:.4f}x+{1:.4f}\nr_value:{2:.2f} \np:{3:.3f}'.format(slope,intercept,r_value,p_value))





# %%
df = df[(df.Station=="KAN_L") | (df.Station=="KAN_M")]

sns.set_theme(style="darkgrid", font="Arial", font_scale=2)
g = sns.FacetGrid(data=df.sort_values("Station"), col="Station", col_wrap=2, 
                 legend_out=True, size=6)
g.map(sns.regplot, "doy", "bias")
g.add_legend()
g.refline(y=0)    
g.savefig("/data/shunan/github/Remote-Sensing-of-Albedo/windowsize/promice/KANbias150m.png",
            dpi=300, bbox_inches="tight")

#%%
sns.set_theme(style="darkgrid", font="Arial", font_scale=2)
g = sns.FacetGrid(data=df, col="Station", col_wrap=2, height=6)
g.map(sns.regplot, "visnirAlbedo", "bias")
g.refline(y=0)    
g.savefig("/data/shunan/github/Remote-Sensing-of-Albedo/windowsize/promice/KANbiasLinear150m.png",
            dpi=300, bbox_inches="tight")

dfsubset = df[df.Station=="KAN_L"]
slope, intercept, r_value, p_value, std_err = stats.linregress(dfsubset["visnirAlbedo"], dfsubset["bias"])
print('KAN_L: \ny={0:.4f}x+{1:.4f}\nr_value:{2:.2f} \np:{3:.3f}'.format(slope,intercept,r_value,p_value))
dfsubset = df[df.Station=="KAN_M"]
slope, intercept, r_value, p_value, std_err = stats.linregress(dfsubset["visnirAlbedo"], dfsubset["bias"])
print('KAN_M: \ny={0:.4f}x+{1:.4f}\nr_value:{2:.2f} \np:{3:.3f}'.format(slope,intercept,r_value,p_value))



# %%
sns.boxplot(data=df, x="Station", y="bias")
# %%
sns.boxplot(data=df, x="Station", y="visnirAlbedo")
# %%