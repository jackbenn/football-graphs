"""Downloading and loading the nflverse play-by-play, and the columns the plots need."""

import urllib.request
from pathlib import Path

import pandas as pd

BASE_URL = 'https://github.com/nflverse/nflverse-data/releases/download'


def download(year, data_dir='data'):
    """Download one season of play-by-play, and the table of teams, into data_dir.
    Delete a file to fetch a fresh copy."""
    Path(data_dir).mkdir(exist_ok=True)
    for url in [f'{BASE_URL}/pbp/play_by_play_{year}.csv.gz',
                f'{BASE_URL}/teams/teams_colors_logos.csv']:
        path = Path(data_dir) / url.rsplit('/', 1)[1]
        if path.exists():
            print(f'{path} already exists')
        else:
            urllib.request.urlretrieve(url, path)
            print(f'downloaded {path}')


def load_season(year, data_dir='data'):
    """One season's play-by-play"""
    return pd.read_csv(Path(data_dir) / f'play_by_play_{year}.csv.gz', low_memory=False)


def load_teams(data_dir='data'):
    """The table of teams, with their names and colors, indexed by abbreviation"""
    return pd.read_csv(Path(data_dir) / 'teams_colors_logos.csv').set_index('team_abbr')


def add_time_column(df):
    """Add column for number of seconds into game"""
    df['Time'] = (df.qtr-1)*60*15 + 60*15 - df.quarter_seconds_remaining


def add_yards_column(df):
    """Add column Position: yards from the end zone the home team defends, so
    the home team always drives from 0 (the bottom of the plot) toward 100 and
    the away team the other way"""
    df['Position'] = df.yardline_100.where(df.defteam == df.home_team, 100 - df.yardline_100)
