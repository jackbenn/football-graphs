"""Choosing the colors for the two teams in a game."""

import numpy as np


def pick_colors(teams, home, away):
    """Choose a line color for each team from its own colors, darkened where
    needed to show on white, and distinct from each other for normal and
    red-green colorblind vision. The away team gives way first."""
    machado = {    # Machado et al. 2009, severity 1.0
        'protan': np.array([[0.152286, 1.052583, -0.204868],
                            [0.114503, 0.786281, 0.099216],
                            [-0.003882, -0.048116, 1.051998]]),
        'deutan': np.array([[0.367322, 0.860646, -0.227968],
                            [0.280085, 0.672501, 0.047413],
                            [-0.011820, 0.042940, 0.968881]]),
    }

    def linear(color):
        rgb = np.array([int(color[i:i+2], 16) for i in (1, 3, 5)]) / 255
        return np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)

    def oklab(lin):
        lms = np.cbrt(np.array([[0.4122214708, 0.5363325363, 0.0514459929],
                                [0.2119034982, 0.6806995451, 0.1073969566],
                                [0.0883024619, 0.2817188376, 0.6299787005]]) @ lin)
        return np.array([[0.2104542553, 0.7936177850, -0.0040720468],
                         [1.9779984951, -2.4285922050, 0.4505937099],
                         [0.0259040371, 0.7827717662, -0.8086757660]]) @ lms

    def difference(c1, c2, cvd=None):
        """OKLab distance x100, optionally as seen with a color vision deficiency"""
        l1, l2 = linear(c1), linear(c2)
        if cvd:
            l1, l2 = np.clip(machado[cvd] @ l1, 0, 1), np.clip(machado[cvd] @ l2, 0, 1)
        return 100 * np.linalg.norm(oklab(l1) - oklab(l2))

    def contrast(color):
        """WCAG contrast ratio against white"""
        return 1.05 / (linear(color) @ [0.2126, 0.7152, 0.0722] + 0.05)

    def usable(team):
        colors = []
        for color in teams.loc[team, ['team_color', 'team_color2', 'team_color3', 'team_color4']].dropna():
            if difference(color, '#ffffff') < 10:    # white, or nearly
                continue
            rgb = np.array([int(color[i:i+2], 16) for i in (1, 3, 5)])
            while contrast(color) < 3:               # too pale for thin lines on white
                rgb = (rgb * 0.97).astype(int)
                color = '#%02x%02x%02x' % tuple(rgb)
            if color not in colors:
                colors.append(color)
        return colors

    def distinct(c1, c2):
        return (difference(c1, c2) >= 15 and
                min(difference(c1, c2, 'protan'), difference(c1, c2, 'deutan')) >= 8)

    home_colors, away_colors = usable(home), usable(away)
    # fewest steps from the two primaries first; on a tie the away team gives way
    pairs = sorted(((h, a) for h in range(len(home_colors)) for a in range(len(away_colors))),
                   key=lambda p: (sum(p), p[0]))
    for h, a in pairs:
        if distinct(home_colors[h], away_colors[a]):
            return home_colors[h], away_colors[a]
    return home_colors[0], 'grey'    # no pair works; no current matchup gets here
