import itertools

from football_graphs.colors import pick_colors


def test_every_matchup_gets_a_distinct_pair(teams):
    """No pair of teams in the table, either way round, falls back to grey"""
    for home, away in itertools.permutations(teams.index, 2):
        assert pick_colors(teams, home, away)[1] != 'grey', (home, away)
