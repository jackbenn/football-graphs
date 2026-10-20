"""Checks of every game of the 2018 season, using the downloaded data."""

import pytest

from football_graphs.data import add_time_column, add_yards_column, load_season
from football_graphs.game import game_data

from conftest import DATA_DIR

pytestmark = pytest.mark.slow


@pytest.fixture(scope='module')
def games(teams):
    """The 2018 games as {old_game_id: (rows, game_data)}"""
    if not (DATA_DIR / 'play_by_play_2018.csv.gz').exists():
        pytest.skip('no downloaded 2018 play-by-play in data/')
    games = {}
    for game_id, df in load_season(2018, DATA_DIR).groupby('old_game_id'):
        df = df.sort_values('play_id').reset_index(drop=True).copy()
        add_time_column(df)
        add_yards_column(df)
        games[game_id] = df, game_data(df, teams)
    return games


def test_final_scores(games):
    for game_id, (df, game) in games.items():
        real = {df.home_team.iloc[0]: df.home_score.iloc[0], df.away_team.iloc[0]: df.away_score.iloc[0]}
        assert game['final_score'] == real, game_id


def test_labels_apart(games):
    """Two scores by one team need at least a kickoff between them, so labels on
    the same side closer than two plays mean a score was counted twice"""
    for game_id, (df, game) in games.items():
        for team in (game['home'], game['away']):
            plays = [label['play'] for label in game['labels'] if label['team'] == team]
            assert all(b - a >= 2 for a, b in zip(plays, plays[1:])), (game_id, team, plays)
