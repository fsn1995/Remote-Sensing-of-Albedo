# %%
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
sns.set_theme(style="darkgrid")

# %% [markdown]
# ## Parlung Glacier

# %%
df = pd.read_excel("H:\insituAWS\parlung_tibet_2016.xlsx")
df.head()

# %%

df["datetime"] = pd.to_datetime(df.date) + pd.DateOffset(hours=-8)
df["albedoRaw"] = df.sout / df.sin

index = (df.sin > 0) & (df.sout > 0) & (df.albedoRaw < 1) 
df = df[index]

# %%
df["albedo"] = df.albedoRaw.rolling(5, center=True).mean()

# %%
fig, ax = plt.subplots(figsize=(10,5))
sns.lineplot(data=df, x="datetime", y="albedoRaw", label="Raw")
sns.lineplot(data=df, x="datetime", y="albedo", label="albedo")

# %%
df = df[["datetime", "albedo", "albedoRaw"]] 
df["region"] = "High Mountain Asia"
df["site"] = "Parlung Glacier No. 4"
df.to_csv("awsAlbedo.csv", mode="w", index=False)

# %% [markdown]
# ## Haig Glacier

# %%
df = pd.read_excel("H:\insituAWS\HaigAWS_daily_2002_2015_gapfilled.xlsx", skiprows=6)
df.head()

# %%

df["datetime"] = pd.to_datetime(df['Year'] * 1000 + df['Day'], format='%Y%j')
df["albedoRaw"] = df.albedo
df = df[df["       flag"] == 1] 
# %%
fig, ax = plt.subplots(figsize=(10,5))
sns.lineplot(data=df, x="datetime", y="albedoRaw", label="Raw")
sns.lineplot(data=df, x="datetime", y="albedo", label="albedo")

# %%
df = df[["datetime", "albedo", "albedoRaw"]] 
df["region"] = "North America"
df["site"] = "Haig Glacier"
df.to_csv("awsAlbedo.csv", mode="a", index=False, header=False)




# %% [markdown]
# # %% Djankuat AWS1
df = pd.read_csv("H:\insituAWS\Djankuat_AWS1_hourly.tab", skiprows=20, delimiter="\t")
df.rename(columns={
    "Date/Time": "datetime",
    "SWD [W/m**2]": "SWD",
    "SWU [W/m**2]": "SWU"
},
inplace = True)
df.head()
# %%
df["datetime"] = pd.to_datetime(df.datetime) + pd.DateOffset(hours=-4)
df["albedoRaw"] = df.SWU / df.SWD

index = (df.SWU > 0) & (df.SWD > 0) & (df.albedoRaw < 1) 
df = df[index]
df["albedo"] = df.albedoRaw.rolling(5, center=True).mean()

# %%
fig, ax = plt.subplots(figsize=(10,5))
sns.lineplot(data=df, x="datetime", y="albedoRaw", label="Raw")
sns.lineplot(data=df, x="datetime", y="albedo", label="albedo")
# %%
df = df[["datetime", "albedo", "albedoRaw"]] 
df["region"] = "North Caucasus"
df["site"] = "Djankuat AWS1"
df.to_csv("awsAlbedo.csv", mode="a", index=False, header=False)

# %% [markdown]
# %% Djankuat AWS2
df = pd.read_csv("H:\insituAWS\Djankuat_AWS2_hourly.tab", skiprows=20, delimiter="\t")
df.rename(columns={
    "Date/Time": "datetime",
    "SWD [W/m**2]": "SWD",
    "SWU [W/m**2]": "SWU"
},
inplace = True)
df.head()
# %%
df["datetime"] = pd.to_datetime(df.datetime) + pd.DateOffset(hours=-4)
df["albedoRaw"] = df.SWU / df.SWD

index = (df.SWU > 0) & (df.SWD > 0) & (df.albedoRaw < 1) 
df = df[index]
df["albedo"] = df.albedoRaw.rolling(5, center=True).mean()


# %%
fig, ax = plt.subplots(figsize=(10,5))
sns.lineplot(data=df, x="datetime", y="albedoRaw", label="Raw")
sns.lineplot(data=df, x="datetime", y="albedo", label="albedo")
# %%
df = df[["datetime", "albedo", "albedoRaw"]] 
df["region"] = "North Caucasus"
df["site"] = "Djankuat AWS2"
df.to_csv("awsAlbedo.csv", mode="a", index=False, header=False)

# %% [markdown]
# %% Kwadacha Glacier 

# %%
df = pd.read_excel("H:\insituAWS\Kwadacha_GlacierAWS_2008_2011.xlsx", 
                    skiprows=[0,1,2,3,4,5,6,7,8,9,11])               
df.rename(
    columns={
        "Unnamed: 0": "datetime",
        "  QS_in": "SWI",
        "  QS_out": "SWO"
    },
    inplace=True
)
# df.drop(0, inplace=True)
df["datetime"] = df["datetime"].apply(pd.to_datetime, errors='coerce') + pd.DateOffset(hours=+8)  
df[["SWI", "SWO"]] = df[["SWI", "SWO"]].apply(pd.to_numeric, errors='coerce')       
df.head()   

# %%

# df["datetime"] = pd.to_datetime(df.date)
df["albedoRaw"] = df.SWO / df.SWI

index = (df.SWO > 0) & (df.SWI > 0) & (df.albedoRaw < 1) 
df = df[index]
df["albedo"] = df.albedoRaw.rolling(5, center=True).mean()


# %%
fig, ax = plt.subplots(figsize=(10,5))
sns.lineplot(data=df, x="datetime", y="albedoRaw", label="Raw")
sns.lineplot(data=df, x="datetime", y="albedo", label="albedo")

# %%
df = df[["datetime", "albedo", "albedoRaw"]] 
df["region"] = "North America"
df["site"] = "Kwadacha Glacier"
df.to_csv("awsAlbedo.csv", mode="a", index=False, header=False)

# %% [markdown]
# %% Shallap glacier
df = pd.read_csv("H:\insituAWS\Shallap_data.csv", skiprows=1, delimiter=";")
df.rename(
    columns={
        "rawdate": "datetime",
        "swin": "SWI",
        "swout": "SWO"
    },
    inplace=True
)

df.head()
# %%
df["datetime"] = pd.to_datetime(df.datetime) + pd.DateOffset(hours=+5)  
df["albedoRaw"] = df.SWO / df.SWI

index = (df.SWI > 0) & (df.SWO > 0) & (df.albedoRaw < 1) 
df = df[index]
df["albedo"] = df.albedoRaw.rolling(5, center=True).mean()
sns.lineplot(data=df, x="datetime", y="tilt__y") 
# maybe exclude data when tilt is too much?

# %%
fig, ax = plt.subplots(figsize=(10,5))
sns.lineplot(data=df, x="datetime", y="albedoRaw", label="Raw")
sns.lineplot(data=df, x="datetime", y="albedo", label="albedo")

# %%
df = df[["datetime", "albedo", "albedoRaw"]] 
df["region"] = "South America"
df["site"] = "Shallap glacier"
df.to_csv("awsAlbedo.csv", mode="a", index=False, header=False)

# %% [markdown]
# %% Artesonraju glacier
df = pd.read_csv("H:\insituAWS\Artesonraju glacier.csv", skiprows=1, delimiter=";")
df.rename(
    columns={
        "rawdate": "datetime",
        "swin": "SWI",
        "swout": "SWO"
    },
    inplace=True
)

df.head()
# %%
df["datetime"] = pd.to_datetime(df.datetime) + pd.DateOffset(hours=+5)  
df["albedoRaw"] = df.SWO / df.SWI

index = (df.SWI > 0) & (df.SWO > 0) & (df.albedoRaw < 1) 
df = df[index]
df["albedo"] = df.albedoRaw.rolling(5, center=True).mean()
sns.lineplot(data=df, x="datetime", y="tilt__x") 
sns.lineplot(data=df, x="datetime", y="tilt__y") 
# maybe exclude data when tilt is too much?

# %%
fig, ax = plt.subplots(figsize=(10,5))
sns.lineplot(data=df, x="datetime", y="albedoRaw", label="Raw")
sns.lineplot(data=df, x="datetime", y="albedo", label="albedo")

# %%
df = df[["datetime", "albedo", "albedoRaw"]] 
df["region"] = "South America"
df["site"] = "Artesonraju glacier"
df.to_csv("awsAlbedo.csv", mode="a", index=False, header=False)


# %% [markdown]
# %% Yala glacier
df = pd.read_csv("H:\insituAWS\AWSYalaGlacier.csv")
df.rename(
    columns={
        "DATE": "datetime",
        "KINC": "SWI",
        "KOUT": "SWO"
    },
    inplace=True
)

df.head()
# %%
df["datetime"] = pd.to_datetime(df['datetime'] + ' ' + df['TIME']) + pd.DateOffset(hours=-5)  
df["albedoRaw"] = df.SWO / df.SWI

index = (df.SWI > 0) & (df.SWO > 0) & (df.albedoRaw < 1) 
df = df[index]
df["albedo"] = df.albedoRaw.rolling(5, center=True).mean()


# %%
fig, ax = plt.subplots(figsize=(10,5))
sns.lineplot(data=df, x="datetime", y="albedoRaw", label="Raw")
sns.lineplot(data=df, x="datetime", y="albedo", label="albedo")

# %%
df = df[["datetime", "albedo", "albedoRaw"]] 
df["region"] = "High Mountain Asia"
df["site"] = "Yala glacier"
df.to_csv("awsAlbedo.csv", mode="a", index=False, header=False)



# %% [markdown]
# ## McCall Glacier

# %%
df = pd.read_excel("H:\insituAWS\JJMC_2004-2014_Cleaned_191007.xlsx", 
                    sheet_name="JJMC_Table1_Cleaned", skiprows=2)
df.head()

# %%
# df["datetime"] = pd.to_datetime(df['year'] * 1000 + df['day'], format='%Y%j')
index = df.time > 2359
df.time[index] = 0000
df["datetime"] = pd.to_datetime(df['year'] * 10000000 + df['day'] * 10000 + df['time'],
                                format='%Y%j%H%M')+ pd.DateOffset(hours=9)

#%%
df["albedoRaw"] = df.Albedo

index = (df.Albedo > 0) & (df.Albedo < 1) 
df = df[index]

# %%
df["albedo"] = df.albedoRaw.rolling(5, center=True).mean()

# %%
fig, ax = plt.subplots(figsize=(10,5))
sns.lineplot(data=df, x="datetime", y="albedoRaw", label="Raw")
sns.lineplot(data=df, x="datetime", y="albedo", label="albedo")

# %%
df = df[["datetime", "albedo", "albedoRaw"]] 
df["region"] = "North America"
df["site"] = "McCall Glacier"
df.to_csv("awsAlbedo.csv", mode="a", index=False, header=False)

# %% [markdown]
# ## Qaanaaq ice cap

# %%
df = pd.read_csv("H:\insituAWS\SIGMA_AWS_SiteB_2012-2020_Lv1_3.csv", 
                  usecols=['date', 'albedo', 'daily_integrated_albedo', 'solz_slope'])
df.head()

# %%
# df["datetime"] = pd.to_datetime(df['year'] * 1000 + df['day'], format='%Y%j')
df["datetime"] = pd.to_datetime(df.date)

#%%
df["albedoRaw"] = df.albedo
df["albedo"] = df['daily_integrated_albedo']
index = (df.albedo > 0) & (df.albedo < 1) 
df = df[index]
index = (df.albedoRaw > 0) & (df.albedoRaw < 1) 
df = df[index]
index = df['solz_slope'] <= 76
df = df[index]
# %%
# df["albedo"] = df.albedoRaw.rolling(5, center=True).mean()
# sns.scatterplot(data=df, x="albedo", y="albedoRaw")

# %%
fig, ax = plt.subplots(figsize=(10,5))
# sns.lineplot(data=df, x="datetime", y="albedoRaw", label="Raw")
sns.lineplot(data=df, x="datetime", y="albedo", label="albedo")

# %%
df = df[["datetime", "albedo", "albedoRaw"]] 
df["region"] = "Greenland"
df["site"] = "Qaanaaq ice cap"
df.to_csv("awsAlbedo.csv", mode="a", index=False, header=False)

# %% [markdown]
# ## Hintereisferner

# %% 
df = pd.read_csv(r"C:\Users\au686295\Downloads\acinn_data_Hintereisferner_RAW_05881cef\data.csv", 
                  skiprows=1,
                  usecols=['rawdate', 'swi_avg', 'swo_avg'],
                  delimiter=";")
df.head()

# %%
# df["datetime"] = pd.to_datetime(df['year'] * 1000 + df['day'], format='%Y%j')
df["datetime"] = pd.to_datetime(df.rawdate) + pd.DateOffset(hours=+1)

#%%
df["albedoRaw"] = df.swo_avg / df.swi_avg
index = (df.albedoRaw > 0) & (df.albedoRaw < 1) 
df = df[index]

# %%
df["albedo"] = df.albedoRaw.rolling(5, center=True).mean()
sns.scatterplot(data=df, x="albedo", y="albedoRaw")

# %%
fig, ax = plt.subplots(figsize=(10,5))
# sns.lineplot(data=df, x="datetime", y="albedoRaw", label="Raw")
sns.lineplot(data=df, x="datetime", y="albedo", label="albedo")

# %%
df = df[["datetime", "albedo", "albedoRaw"]] 
df["region"] = "Alps"
df["site"] = "Hintereisferner"
df.to_csv("awsAlbedo.csv", mode="a", index=False, header=False)

# %% [markdown]
# ## Glacier de la Plaine Morte 

df = pd.read_excel("H:\insituAWS\PlaineMorte_Meteo_20142017.xlsx")
df.head()

# %%

df["datetime"] = pd.to_datetime(df.TIMESTAMP) + pd.DateOffset(hours=-1)
df["albedoRaw"] = df.Albedo

index = (df.albedoRaw > 0) & (df.albedoRaw < 1) 
df = df[index]

# %%
df["albedo"] = df.albedoRaw.rolling(5, center=True).mean()

# %%
fig, ax = plt.subplots(figsize=(10,5))
sns.lineplot(data=df, x="datetime", y="albedoRaw", label="Raw")
sns.lineplot(data=df, x="datetime", y="albedo", label="albedo")

# %%
df = df[["datetime", "albedo", "albedoRaw"]] 
df["region"] = "Alps"
df["site"] = "Glacier de la Plaine Morte"
df.to_csv("awsAlbedo.csv", mode="a", index=False, header=False)

# %%
