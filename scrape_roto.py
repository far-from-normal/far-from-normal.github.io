# import re
from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd
import numpy as np

def get_data(url):
    # get data
    soup = BeautifulSoup(urlopen(url), features="html.parser")
    raw = soup.find_all("td")
    data = []
    tag = []
    for row in raw:
        data.append(row.get_text())
        tag.append(row.get('data-stat'))

    # stuff into super long data frame
    long = pd.DataFrame(
        data=np.array([data, tag]).T,
        columns=['data', 'tag']
    )

    # reshape / pivot
    long['idx'] = 0
    idx = 0
    for index, row in long.iterrows():
        if row['tag'] == 'player':
            idx += 1
        long.at[index, 'idx'] = idx
    long = long.pivot_table(
        index='idx', 
        columns='tag', 
        values='data',
        aggfunc='first',
        fill_value=None
    )
    long.reset_index(inplace=True)
    # long.drop(columns=['idx', 'team_ID'], inplace=True)
    long.drop(columns=['idx'], inplace=True)

    # move players col to front
    cols = list(long)
    cols.insert(0, cols.pop(cols.index('player')))
    long = long.loc[:, cols]

    cols_string = ["player", "team_ID"]
    cols_numeric = [c for c in cols if c not in cols_string]

    # long[cols[1:]] = long[cols[1:]].apply(pd.to_numeric, errors='coerce', axis=1)
    long[cols_numeric] = long[cols_numeric].apply(pd.to_numeric, errors='coerce', axis=1)
    long['player'] = long['player'].str.strip()
    long[['player']] = long[['player']] \
        .apply(lambda x: x.str.normalize('NFKD') \
        .str.encode('ascii', errors='ignore') \
        .str.decode('utf-8')
        .str.lower())

    return long

def get_singles(df):
    df['1B'] = df['H'] - (df['2B'] + df['3B'] + df['HR'])
    return df
def get_nsb(df):
    df['NSB'] = df['SB'] - df['CS']
    return df
def get_obp(df):
    df['OBP'] = (df['H'] + df['BB'] + df['HBP']) / (df['PA'])
    # df['OBP'] = (df['H'] + df['BB'] + df['HBP']) / (df['AB'] + df['BB'] + df['HBP'] + df['SF'])
    return df
def get_slg(df):
    df['SLG'] = (df['1B'] + 2*df['2B'] + 3*df['3B'] + 4*df['HR']) / df['AB']
    return df
def get_whip(df):
    df['WHIP'] = (df['H'] + df['BB']) / df['IP']
    return df
def get_svh(df):
    df['SVH'] = df['SV'] + df['Hold']
    return df
def get_forward_ip(df):
    df['IP'] = \
        df['IP'].astype(str).str.split('.').str[0].astype(float) + \
        (1./3.)*df['IP'].astype(str).str.split('.').str[1].astype(float)
    return df

def get_backward_ip(df):
    df['IP'] = \
        df['IP'].astype(str).str.split('.').str[0].astype(float) + \
        0.3*('0.' + df['IP'].astype(str).str.split('.').str[1]).astype(float)
    return df

def batter_stats_augment(df):
    # R, HR, OPB, SLG, NSB
    df = get_singles(df)
    df = get_nsb(df)
    return df

def pitcher_stats_augment(df):
    # R, HR, WHIP, SO, SVH
    df = get_forward_ip(df)
    # df = get_whip(df)
    return df

def team_pitcher_stats(df):
    # R, HR, SO, WHIP, SV, Hold
    cols = [
        "Team_Name",
        'IP',
        'R',
        'HR',
        'SO',
        'H',
        'BB',
        'SV',
        'Hold'
    ]
    df = df[cols]
    df = df.groupby(["Team_Name"]).sum()
    df.reset_index(inplace=True)
    df = get_whip(df)
    df = get_svh(df)
    df = df[["Team_Name", 'IP', 'R', 'HR', 'SO', 'WHIP', 'SVH']]
    df.columns = ["Team_Name", 'IP', 'RA', 'HRA', 'SO', 'WHIP', 'SVH']
    return df

def team_batter_stats(df):
    # R, HR, OPB, SLG, NSB
    cols = [
        "Team_Name",
        'PA',
        'AB',
        'BB',
        'HBP',
        'SF',
        'R',
        'H',
        '1B',
        '2B',
        '3B',
        'HR',
        'NSB'
    ]
    df = df[cols]
    df = df.groupby(["Team_Name"]).sum()
    df.reset_index(inplace=True)
    df = get_obp(df)
    df = get_slg(df)
    df = df[["Team_Name", 'PA', 'R', 'HR', 'OBP', 'SLG', 'NSB']]
    return df


def assign_players_to_teams(
    data,
    teams,
    player_type
):

    teams = teams[teams['Type'] == player_type.lower()]
    df = teams.merge(
        data,
        how='left',
        # how='inner',
        on=['player']
        )
    return df

def combine_team_stats(b, p):
    roto_stats = b.merge(
        p,
        how='inner',
        on=['Team_Name']
        )
    return roto_stats

def process_teams(df):
    df = pd.melt(df , id_vars=['Type'])
    df.columns = ['Type', 'Team_Name', 'player']
    cols = df.select_dtypes(include=[np.object]).columns
    df[cols] = df[cols] \
        .apply(lambda x: x.str.normalize('NFKD') \
        .str.encode('ascii', errors='ignore') \
        .str.decode('utf-8')
        .str.lower())

    df['player'] = df['player'] \
        .str.replace(r"\(.*\)", "") \
        .str.strip()
    df = df \
        .apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    return df

def get_roto_stats(df_p, df_b):

    teams_p = team_pitcher_stats(df_p)
    teams_b = team_batter_stats(df_b)

    roto_stats = combine_team_stats(
        teams_b, 
        teams_p)

    roto_stats = get_backward_ip(roto_stats)

    pts_cat = {
        'R': True,
        'HR': True,
        'OBP': True,
        'SLG': True,
        'NSB': True,
        'RA': False,	
        'HRA': False,	
        'SO': True,
        'WHIP': False,
        'SVH': True,
    }

    exclude_rank = ['PA', 'IP']

    for col in roto_stats.columns[1:]:
        if col not in exclude_rank:
            pts_col = col + '_pts'
            order = pts_cat[col]
            roto_stats[pts_col] = roto_stats[col].rank(
                method='average', 
                ascending=order) #.astype(np.int32)

    roto_stats['Total_pts'] = roto_stats.loc[:, 'R_pts':'SVH_pts'].sum(axis = 1)
    roto_stats['Rank'] = roto_stats['Total_pts'].rank(
        method='average', 
        ascending=False) #.astype(np.int32)

    cols = list(roto_stats)
    cols.insert(1, cols.pop(cols.index('Rank')))
    roto_stats = roto_stats.loc[:, cols]
    roto_stats.sort_values(
        by=['Rank'], 
        ascending=True, 
        inplace=True
        )

    return roto_stats