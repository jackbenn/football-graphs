"""Downloading and loading the nflverse play-by-play, and the columns the plots need."""

import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

BASE_URL = 'https://github.com/nflverse/nflverse-data/releases/download'

# the play-by-play's text columns, among those the package reads; read in
# chunks, a column whose first chunks are empty is otherwise taken for numbers
TEXT_COLUMNS = {'game_id', 'season_type', 'game_date', 'home_team', 'away_team', 'posteam',
                'defteam', 'play_type', 'td_team', 'field_goal_result', 'extra_point_result',
                'two_point_conv_result', 'desc', 'timeout_team'}


def download(year, data_dir='data', refresh=False):
    """Download one season of play-by-play, and the table of teams, into data_dir.
    Delete a file, or pass refresh, to fetch a fresh copy."""
    Path(data_dir).mkdir(exist_ok=True)
    for url in [f'{BASE_URL}/pbp/play_by_play_{year}.csv.gz',
                f'{BASE_URL}/teams/teams_colors_logos.csv']:
        path = Path(data_dir) / url.rsplit('/', 1)[1]
        if path.exists() and not refresh:
            print(f'{path} already exists')
        else:
            urllib.request.urlretrieve(url, path)
            print(f'downloaded {path}')


def load_season(year, data_dir='data', columns=None):
    """One season's play-by-play: every column, or only the columns given. Reading
    every column peaks near 500 MB; the few that game_data needs, read in chunks
    as low_memory does, peak near 130 MB"""
    path = Path(data_dir) / f'play_by_play_{year}.csv.gz'
    if columns is None:
        return pd.read_csv(path, low_memory=False)
    return pd.read_csv(path, usecols=columns,
                       dtype={column: 'str' for column in columns if column in TEXT_COLUMNS})


def load_teams(data_dir='data'):
    """The table of teams, with their names and colors, indexed by abbreviation"""
    return pd.read_csv(Path(data_dir) / 'teams_colors_logos.csv').set_index('team_abbr')


def add_time_column(df):
    """Add column Time: seconds into the game. Quarters are 15 minutes, and so are
    overtime periods in the playoffs, but regular-season overtime has been 10
    minutes since 2017; a period that starts with 10:00 or less left is taken as
    a 10-minute one."""
    longest = df.groupby(['game_id', 'qtr']).quarter_seconds_remaining.transform('max')
    length = np.where((df.qtr > 4) & (longest <= 10*60), 10*60, 15*60)
    df['Time'] = (df.qtr-1)*60*15 + length - df.quarter_seconds_remaining


def add_yards_column(df):
    """Add column Position: yards from the end zone the home team defends, so
    the home team always drives from 0 (the bottom of the plot) toward 100 and
    the away team the other way"""
    df['Position'] = df.yardline_100.where(df.defteam == df.home_team, 100 - df.yardline_100)
