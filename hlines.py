import pandas as pd 
import seaborn as sns

df = pd.DataFrame(
    {
        "day": ['1', '1', '1', '2', '2', '2', '2', '3', '3'],
        "sleep_start": [1.2, 6.6, 15.9,  2.1, 7.5, 14.8, 20.9, 3.4, 17.9],
        "sleep_end": [3.1, 8.9, 20.7,  6.1, 9.4, 19.0, 23.8, 5.5, 19.3],
    }
)

print(df.head(20))