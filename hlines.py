import pandas as pd 
import seaborn as sns
import datetime

# df = pd.DataFrame(
#     {
#         "day": ['1', '1', '1', '2', '2', '2', '2', '3', '3'],
#         "sleep_start": [1.2, 6.6, 15.9,  2.1, 7.5, 14.8, 20.9, 3.4, 17.9],
#         "sleep_end": [3.1, 8.9, 20.7,  6.1, 9.4, 19.0, 23.8, 5.5, 19.3],
#     }
# )

# print(df.head(20))

df = pd.read_csv("Isla_sleep.csv")
df = df[['Time', 'Duration(minutes)']]
df.columns = ['start_time', 'dur_mins']

df['start_time'] = pd.to_datetime(df['start_time'], infer_datetime_format=True) 
df['dur_mins'] = pd.to_timedelta(df['dur_mins'], 'm')
df['end_time'] = df['start_time'] + df['dur_mins']
df = df.sort_values(by=['start_time'])

print(df.head(5))
print(df.dtypes)