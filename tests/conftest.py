from pathlib import Path

import pytest

from football_graphs.data import load_teams

DATA_DIR = Path(__file__).parent.parent / 'data'


@pytest.fixture(scope='session')
def teams():
    """The downloaded table of teams, or a skip if there isn't one"""
    if not (DATA_DIR / 'teams_colors_logos.csv').exists():
        pytest.skip('no downloaded teams table in data/')
    return load_teams(DATA_DIR)
