"""Hand-built games for the scoring edge cases; these need no downloaded data."""

import json

import numpy as np
import pandas as pd

from football_graphs.data import add_time_column, add_yards_column
from football_graphs.game import game_data

HOME, AWAY = 'HOM', 'AWY'
TEAMS = pd.DataFrame({'team_name': ['Hometown Hosts', 'Away City Visitors'],
                      'team_nick': ['Hosts', 'Visitors'],
                      'team_color': ['#0b3d91', '#c8102e'],
                      'team_color2': np.nan, 'team_color3': np.nan, 'team_color4': np.nan},
                     index=pd.Index([HOME, AWAY], name='team_abbr'))
COLORS = {HOME: '#0b3d91', AWAY: '#c8102e'}


def other(team):
    return AWAY if team == HOME else HOME


def kickoff(kicking, yardline_100=35, **columns):
    """A kickoff from the kicking team's own 35; posteam is the receiving team"""
    return dict(play_type='kickoff', posteam=other(kicking), defteam=kicking,
                yardline_100=yardline_100, **columns)


def snap(play_type, offense, yardline_100, down=1, **columns):
    return dict(play_type=play_type, posteam=offense, defteam=other(offense),
                yardline_100=yardline_100, down=down, **columns)


def game(*plays):
    """game_data for the plays given, each a dict of its columns that differ from
    a play that scores nothing, thirty seconds apart"""
    ordinary = dict(game_id='2018_01_AWY_HOM', home_team=HOME, away_team=AWAY,
                    game_date='2018-09-09', qtr=1, down=np.nan, ydstogo=10, touchdown=0,
                    td_team=np.nan, field_goal_result=np.nan, extra_point_result=np.nan,
                    two_point_conv_result=np.nan, safety=0, posteam_score=0,
                    posteam_score_post=0, defensive_two_point_conv=0, desc='a play',
                    timeout=0, timeout_team=np.nan)
    df = pd.DataFrame([{**ordinary, 'quarter_seconds_remaining': 900 - 30*i, **play}
                       for i, play in enumerate(plays)])
    add_time_column(df)
    add_yards_column(df)
    data = game_data(df, TEAMS)
    json.dumps(data, allow_nan=False)
    return data


def labels(data):
    return [(label['play'], label['team'], label['score']) for label in data['labels']]


def segment_from(data, play):
    return next(segment for segment in data['segments'] if segment['play'][0] == play)


def test_defensive_touchdown():
    """An interception returned for a touchdown scores for the defense, and the
    line runs, in the offense's color, into the end zone the defense attacks"""
    data = game(kickoff(HOME),
                snap('run', AWAY, 75),
                snap('pass', AWAY, 70, down=2, touchdown=1, td_team=HOME),
                snap('extra_point', HOME, 15, down=np.nan, extra_point_result='good'),
                kickoff(HOME))
    assert data['final_score'] == {HOME: 7, AWAY: 0}
    assert labels(data) == [(3, HOME, 7)]
    interception = segment_from(data, 3)
    assert interception['y'][1] == 100
    assert interception['color'] == COLORS[AWAY]
    assert segment_from(data, 4)['y'][1] == 100


def test_punt_return_safety():
    """A returner tackled in his own end zone gives the kicking team the safety;
    on a punt the kicking team is posteam"""
    data = game(kickoff(HOME),
                snap('run', AWAY, 75),
                snap('punt', AWAY, 80, down=4, safety=1, posteam_score=0, posteam_score_post=2),
                kickoff(HOME, yardline_100=20))    # the free kick after a safety
    assert data['final_score'] == {HOME: 0, AWAY: 2}
    assert labels(data) == [(3, AWAY, 2)]
    assert segment_from(data, 3)['y'][1] == 0


def test_safety_on_offense():
    """A ball carrier tackled in his own end zone gives the defense the safety"""
    data = game(kickoff(AWAY),
                snap('run', HOME, 95, safety=1, posteam_score=0, posteam_score_post=0),
                kickoff(HOME, yardline_100=20))
    assert data['final_score'] == {HOME: 0, AWAY: 2}
    assert labels(data) == [(2, AWAY, 2)]
    assert segment_from(data, 2)['y'][1] == 0


def test_defensive_two_point_return():
    """A two-point try returned by the defense scores it two, with its own label,
    and leaves the touchdown's label at six"""
    data = game(kickoff(HOME),
                snap('pass', AWAY, 10, touchdown=1, td_team=AWAY),
                snap('pass', AWAY, 2, down=np.nan, two_point_conv_result='failure',
                     defensive_two_point_conv=1),
                kickoff(AWAY))
    assert data['final_score'] == {HOME: 2, AWAY: 6}
    assert labels(data) == [(2, AWAY, 6), (3, HOME, 2)]
    assert segment_from(data, 3)['y'][1] == 100


def test_first_play_not_a_kickoff():
    """As in 2018102500: the opening kickoff is called back by a penalty, so the
    first play is a no_play, with the receiving team as posteam, and the kickoff
    after it starts a new line"""
    data = game(dict(kickoff(HOME), play_type='no_play'),
                kickoff(HOME, yardline_100=40),
                snap('pass', AWAY, 75))
    assert [play['play'] for play in data['plays']] == [1, 2, 3]
    assert [segment['play'] for segment in data['segments']] == [[2, 3]]
    assert data['quarters'] == [{'quarter': 1, 'play': 0, 'time': 0}]
    assert data['final_score'] == {HOME: 0, AWAY: 0}


def test_plays():
    """Each play's details, and the score after it: a touchdown is 6, and the
    extra point makes it 7 on the next play"""
    data = game(kickoff(HOME),
                snap('pass', AWAY, 10, desc='a touchdown pass', touchdown=1, td_team=AWAY),
                snap('extra_point', AWAY, 15, down=np.nan, extra_point_result='good'))
    touchdown = data['plays'][1]
    assert touchdown['offense'] == AWAY and touchdown['play_type'] == 'pass'
    assert (touchdown['quarter'], touchdown['clock']) == (1, 870)
    assert (touchdown['down'], touchdown['distance']) == (1, 10)
    assert touchdown['desc'] == 'a touchdown pass'
    assert [play['score'] for play in data['plays']] == [{HOME: 0, AWAY: 0}, {HOME: 0, AWAY: 6},
                                                        {HOME: 0, AWAY: 7}]
    assert data['plays'][0]['down'] is None and data['plays'][0]['distance'] is None


def test_timeouts():
    """A timeout goes with the play before it, whether it is its own row or is
    recorded on that play, as a lost challenge is"""
    timeout = dict(play_type='no_play', posteam=np.nan, defteam=np.nan, yardline_100=np.nan,
                   timeout=1, timeout_team=HOME)
    data = game(kickoff(HOME),
                snap('run', AWAY, 75),
                timeout,
                snap('pass', AWAY, 70, down=2, timeout=1, timeout_team=HOME))
    assert [play['timeouts'] for play in data['plays']] == [[], [HOME], [HOME]]


def test_overtime_clock():
    """Regular-season overtime is 10 minutes, playoff overtime 15; either way the
    game clock carries on from the end of the fourth quarter"""
    for length in (600, 900):
        data = game(kickoff(HOME, qtr=4, quarter_seconds_remaining=10),
                    kickoff(AWAY, qtr=5, quarter_seconds_remaining=length),
                    snap('run', HOME, 75, qtr=5, quarter_seconds_remaining=length - 5))
        assert [play['time'] for play in data['plays']] == [3590, 3600, 3605]
