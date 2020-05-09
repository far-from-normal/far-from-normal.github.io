from scrape_roto import *
from pathlib import Path
import seaborn as sns
import datetime

pd.options.display.float_format = '${:,.2f}'.format

def make_clickable(val):
    return '<a href="{}">{}</a>'.format(val,val)

def hover(hover_color="#ffff99"):
    return dict(selector="tr:hover",
                props=[("background-color", "%s" % hover_color)])

# %% |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
base_url = "https://www.baseball-reference.com/sim/leagues/MLB/2020-"
url_pitcher = base_url + "pitching.shtml" 
url_batter = base_url + "batting.shtml"

# %% Raw data pull
p_data = get_data(url_pitcher)
b_data = get_data(url_batter)
# b_data = b_data[(b_data["player"]!="Will Smith") & (b_data["team_ID"]!="ATL")]
# b_data = b_data[~((b_data["player"]=="Will Smith") & (b_data["team_ID"]=="ATL"))]
b_data = b_data[~((b_data["player"].isin(["Will Smith"])) & (b_data["team_ID"].isin(["ATL"])))]


# %% augment data witha few stats
p_data = pitcher_stats_augment(p_data)
b_data = batter_stats_augment(b_data)

# %% get team-players
df_teams = pd.read_excel("Fantasy_TeamList_032820.xlsx")
df_teams = process_teams(df_teams)

# %% team pitchers / batters
df_p = assign_players_to_teams(
    p_data, 
    df_teams, 
    'Arms'
    )
df_b = assign_players_to_teams(
    b_data,
    df_teams,
    'Bats'
    )



df_p_output = df_p[["Team_Name", "player", 'IP', 'R', 'HR', 'SO', 'whip', 'SV']]
df_p_output.columns = ["Team_Name", "player", 'IP', 'RA', 'HRA', 'SO', 'WHIP', 'SV']

df_b_output = get_nsb(df_b)
df_b_output = df_b_output[["Team_Name", "player", 'PA', 'R', 'HR', 'onbase_perc', 'slugging_perc', 'NSB']]
df_b_output.columns = ["Team_Name", "player", 'PA', 'R', 'HR', 'OBP', 'SLG', 'NSB']

df_p_output.to_csv(
    'pitcher_by_team.csv', 
    index=False, 
    float_format='%.3f'
    )
df_b_output.to_csv(
    'batter_by_team.csv', 
    index=False, 
    float_format='%.3f'
    )

# %%

roto_stats = get_roto_stats(df_p, df_b)

type_dict = {
    'Rank': np.int32,
    'PA': np.int32,
    'R': np.int32,
    'HR': np.int32,
    'OBP': np.float16,
    'SLG': np.float16,
    'NSB': np.int32,
    'IP': np.float16,
    'RA': np.int32,
    'HRA': np.int32,
    'SO': np.int32,
    'WHIP': np.float16,
    'SV': np.int32,
    'R_pts': np.float16,
    'HR_pts': np.float16,
    'OBP_pts': np.float16,
    'SLG_pts': np.float16,
    'NSB_pts': np.float16,
    'RA_pts': np.float16,
    'HRA_pts': np.float16,
    'SO_pts': np.float16,
    'WHIP_pts': np.float16,
    'SV_pts': np.float16,
    'Total_pts': np.float16,
}

format_dict = {
    'Rank': "{:d}",
    'PA': "{:d}",
    'R': "{:d}",
    'HR': "{:d}",
    'OBP': "{:.3f}",
    'SLG': "{:.3f}",
    'NSB': "{:d}",
    'IP': "{:.1f}",
    'RA': "{:d}",
    'HRA': "{:d}",
    'SO': "{:d}",
    'WHIP': "{:.3f}",
    'SV': "{:d}",
    'R_pts': "{:.1f}",
    'HR_pts': "{:.1f}",
    'OBP_pts': "{:.1f}",
    'SLG_pts': "{:.1f}",
    'NSB_pts': "{:.1f}",
    'RA_pts': "{:.1f}",
    'HRA_pts': "{:.1f}",
    'SO_pts': "{:.1f}",
    'WHIP_pts': "{:.1f}",
    'SV_pts': "{:.1f}",
    'Total_pts': "{:.1f}",
}

for k, v in type_dict.items():
    roto_stats[k] = roto_stats[k].astype(v)

# %% Header
footer_dict = {
    "OOTP Sim Data": "https://www.sports-reference.com/blog/2020/03/baseball-reference-simulating-2020-season-with-out-of-the-park-baseball-21/",
    "Batting": "https://www.baseball-reference.com/sim/leagues/MLB/2020-batting.shtml",
    "Pitching": "https://www.baseball-reference.com/sim/leagues/MLB/2020-pitching.shtml",
    "About this Roto": "https://github.com/far-from-normal/far-from-normal.github.io"
}
footer = pd.DataFrame.from_dict(footer_dict, orient='index')
footer.columns = ['Source']

styles_footer = [
    hover(),
    dict(selector="caption", props=[("caption-side", "top"),
                                    ("font-size", "10pt"),
                                    ('font-family', 'Helvetica')]
                                    ),
    dict(selector="th", props=[("font-size", "8pt"),
                                ('font-family', 'Helvetica')]
                                ),
]
styled_footer = footer.style.set_table_styles(styles_footer) \
    .format(make_clickable) \
    .set_properties(**{'font-size': '8pt', 'font-family': 'Helvetica'}) \
    .set_caption("About This Simulation") \
    .set_table_attributes("style='display:inline'")

# %% Table
mydate = datetime.datetime.now()
year = mydate.strftime("%Y")
month = mydate.strftime("%B")
day = mydate.strftime("%d")
time = mydate.strftime("%H:%M")
date_str = month + " " + day + ", " + year + ", " + time + " EST"

cmap = cmap=sns.diverging_palette(5, 250, as_cmap=True)
styles = [
    hover(),
    dict(selector="caption", props=[("caption-side", "top"),
                                    ("font-size", "12pt"),
                                    ('font-family', 'Helvetica')]
                                    ),
    dict(selector="th", props=[("font-size", "10pt"),
                                ('font-family', 'Helvetica')]
                                ),
]

styled_table = roto_stats.style.set_table_styles(styles) \
    .hide_index() \
    .format(format_dict) \
    .background_gradient(cmap) \
    .set_properties(**{'font-size': '10pt', 'font-family': 'Helvetica'}) \
    .set_caption("The Mac-3-Pitch Bush League: last updated " + date_str) \
    .set_table_attributes("style='display:inline'")

# %% Write
html_table = styled_table.render()
html_footer = styled_footer.render()

with open("index.html", "w+") as file:
    file.write(html_table)
    file.write(html_footer)
