import pandas as pd 
import seaborn as sns
import datetime
import matplotlib.pyplot as plt

df = pd.read_csv("Isla_sleep.csv")
df = df[['Time', 'Duration(minutes)']]
df.columns = ['start_time', 'dur_mins']

df['start_time'] = pd.to_datetime(df['start_time'], infer_datetime_format=True) 
df['dur_mins'] = pd.to_timedelta(df['dur_mins'], 'min')
df['end_time'] = df['start_time'] + df['dur_mins']
df = df.sort_values(by=['start_time'])
df['key'] = 0
df = df[['start_time', 'end_time', 'key']]

dr = pd.date_range(start='03/31/2020', end=pd.datetime.now().date(), freq='1min')
dr = pd.DataFrame({'time_int': dr})
dr['key'] = 0
dr = dr[['time_int', 'key']]


dfr = df.merge(dr, on='key', how='outer')
dfr.loc[(dfr['time_int'] >= dfr['start_time']) & (dfr['time_int'] <= dfr['end_time']), 'sleep_bool'] = 1
dfr = dfr[['time_int', 'sleep_bool']]
dfr = dfr.groupby(['time_int']).max()
dfr = dfr.fillna(0)

print(dfr.head(25))


# dfr.set_index(pd.to_datetime(dfr['time_int']), inplace=True)
# dfr.reset_index(inplace=True)

dfr.index = pd.MultiIndex.from_arrays([dfr.index.date, dfr.index.time], names=['Date','Time'])

print(dfr.head(25))

hm = dfr.reset_index().pivot(columns='Time', index='Date', values='sleep_bool')

print(hm)

fig, ax = plt.subplots(figsize=(15,10))
sns.heatmap(hm, cmap="YlGnBu", cbar=False)
ax.tick_params(left=False, bottom=False)
ax.set_xticks([])
ax.set_yticks([])
plt.savefig('sleep_map.png', dpi=300)
