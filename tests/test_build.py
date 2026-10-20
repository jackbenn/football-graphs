import datetime
import gzip
import json

import pytest

from football_graphs import build

from conftest import DATA_DIR


def read(path):
    return json.load(gzip.open(path))


@pytest.mark.parametrize('date, season', [('2026-09-10', 2026), ('2027-02-14', 2026),
                                          ('2027-06-01', 2026), ('2026-08-31', 2025)])
def test_current_season(date, season):
    assert build.current_season(datetime.date.fromisoformat(date)) == season


def test_fails_on_a_wrong_score(monkeypatch, capsys):
    monkeypatch.setattr(build, 'build', lambda *args: [('2018_01_ATL_PHI', {'PHI': 17}, {'PHI': 18})])
    assert build.main(['2018']) == 1
    assert '2018_01_ATL_PHI' in capsys.readouterr().err


@pytest.mark.slow
def test_build_2018(teams, tmp_path):
    if not (DATA_DIR / 'play_by_play_2018.csv.gz').exists():
        pytest.skip('no downloaded 2018 play-by-play in data/')
    assert build.build(2018, DATA_DIR, tmp_path) == []
    season_dir = tmp_path / '2018'
    index = read(season_dir / 'index.json.gz')
    assert len(index['games']) == 267
    assert len(index['teams']) == 32
    files = {path.name for path in season_dir.iterdir()} - {'index.json.gz'}
    assert files == {f"{game['game_id']}.json.gz" for game in index['games']}
    weeks = {}
    for game in index['games']:
        weeks[game['week']] = weeks.get(game['week'], 0) + 1
    assert list(weeks) == [str(week) for week in range(1, 18)] + ['WC', 'DIV', 'CONF', 'SB']
    assert sum(weeks[str(week)] for week in range(1, 18)) == 256
    assert [weeks[round] for round in ['WC', 'DIV', 'CONF', 'SB']] == [4, 4, 2, 1]
    assert index['games'][-1]['game_id'] == '2018_21_NE_LA'
    game = read(season_dir / '2018_01_ATL_PHI.json.gz')
    assert game['final_score'] == {'PHI': 18, 'ATL': 12}
