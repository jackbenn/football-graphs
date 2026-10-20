"""Building the files the game page serves: one JSON file per game, and an index
of the season's games, gzipped for nginx's gzip_static.

    python -m football_graphs.build 2018 [--data-dir data] [--out games] [--refresh]
"""

import argparse
import datetime
import gzip
import json
import sys
from pathlib import Path

from .data import add_time_column, add_yards_column, download, load_season, load_teams
from .game import COLUMNS, game_data

# the columns the index needs, besides those game_data reads
INDEX_COLUMNS = ['game_id', 'play_id', 'season_type', 'week', 'home_score', 'away_score']


def current_season(today=None):
    """The season under way, or the last one: a season runs from September to February"""
    today = today or datetime.date.today()
    return today.year if today.month >= 9 else today.year - 1


def write_json(path, data):
    """Write data as gzipped JSON, with no timestamp, so the same data gives the same bytes"""
    with open(path, 'wb') as f, gzip.GzipFile(fileobj=f, mode='wb', mtime=0) as gz:
        gz.write(json.dumps(data, separators=(',', ':')).encode())


def build(season, data_dir='data', out='games', refresh=False):
    """Write out/season/<game_id>.json.gz for every game of the season, and
    out/season/index.json.gz listing them. Return the games whose final score
    doesn't match the data's, as (game_id, ours, theirs)."""
    download(season, data_dir, refresh=refresh)
    plays, teams = load_season(season, data_dir, COLUMNS + INDEX_COLUMNS), load_teams(data_dir)
    season_dir = Path(out) / str(season)
    season_dir.mkdir(parents=True, exist_ok=True)

    games, wrong = [], []
    for game_id, df in plays.groupby('game_id', sort=False):
        df = df.sort_values('play_id').reset_index(drop=True)
        add_time_column(df)
        add_yards_column(df)
        game = game_data(df, teams)
        home, away = game['home'], game['away']
        final = {home: int(df.home_score.iloc[0]), away: int(df.away_score.iloc[0])}
        if game['final_score'] != final:
            wrong.append((game_id, game['final_score'], final))
        write_json(season_dir / f'{game_id}.json.gz', game)
        games.append({'game_id': game_id, 'season_type': df.season_type.iloc[0],
                      'week': int(df.week.iloc[0]), 'date': game['date'],
                      'home': home, 'away': away, 'home_score': final[home], 'away_score': final[away]})

    games.sort(key=lambda game: (game['date'], game['game_id']))
    playing = sorted({game['home'] for game in games} | {game['away'] for game in games})
    write_json(season_dir / 'index.json.gz', {
        'season': season,
        'teams': {team: {'name': teams.team_name[team], 'nick': teams.team_nick[team]}
                  for team in playing},
        'games': games,
    })
    return wrong


def main(argv=None):
    parser = argparse.ArgumentParser(description='Build the game files for a season.')
    parser.add_argument('season', type=int, nargs='?', default=current_season(),
                        help='the season, by the year it starts; the current one by default')
    parser.add_argument('--data-dir', default='data', help='where the downloaded data goes')
    parser.add_argument('--out', default='games', help='where the game files go')
    parser.add_argument('--refresh', action='store_true',
                        help='download the data again even if it is already there')
    args = parser.parse_args(argv)
    wrong = build(args.season, args.data_dir, args.out, args.refresh)
    for game_id, ours, theirs in wrong:
        print(f'{game_id}: final score {ours}, but the data says {theirs}', file=sys.stderr)
    return 1 if wrong else 0


if __name__ == '__main__':
    sys.exit(main())
