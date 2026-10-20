// Drawing a game from its game_data JSON with D3: the port of draw_game in
// src/football_graphs/plot.py, by play number, with above it each team's score,
// and below it each play's down, in the offense's color, over a bar hanging down
// for the clock time it took, colored by what stopped the clock.

const WIDTH = 1250, HEIGHT = 612;
const MARGIN = {right: 34, left: 52};    // and web/style.css indents to MARGIN.left
// the panels, top to bottom, in pixels, with the game graph's legend between the
// first two and the downs between the last two
const SCORE = {top: 44, bottom: 134};
const GAME = {top: 158, bottom: 486};
const DOWNS = 500;
const CLOCK = {top: 512, bottom: 592, most: 60};    // and the clock panel's bottom in seconds

// dash pattern for the play that starts at each point, as in plot.py's STYLES
const SOLID = null, DOTTED = '1.5 2.5', DASHED = '6 3', DASHDOT = '8 3 1.5 3';
const STYLES = {run: SOLID, qb_kneel: SOLID, pass: DOTTED, qb_spike: DOTTED,
                kickoff: DASHED, punt: DASHED, field_goal: DASHED, extra_point: DASHED,
                no_play: DASHDOT};

// the markers for plays, and the game graph's legend: the markers, then the line styles
const SYMBOLS = {kickoff: d3.symbol(d3.symbolStar, 110),
                 first_down: d3.symbol(d3.symbolCircle, 36),
                 play: d3.symbol(d3.symbolCircle, 6)};
const LEGEND = [{label: 'kickoff', symbol: SYMBOLS.kickoff},
                {label: '1st down', symbol: SYMBOLS.first_down},
                {label: 'run', dash: SOLID}, {label: 'pass', dash: DOTTED},
                {label: 'kick', dash: DASHED}, {label: 'penalty', dash: DASHDOT}];

// what stopped the clock after each play, in groups of like reasons with like
// colors, as the legend shows them: game_data's reasons, with the kicks and
// turnovers together as changes of possession, and the two-minute warning with
// the end of the quarter
const STOPS = [
  [{label: 'clock kept running', color: '#c2c0ba', stops: ['running']},
   {label: 'change of possession', color: '#7a7871', stops: ['kick', 'turnover']}],
  [{label: 'incomplete pass', color: '#1c5cab', stops: ['incomplete']},
   {label: 'out of bounds', color: '#6da7ec', stops: ['out_of_bounds']}],
  [{label: 'timeout', color: '#d95926', stops: ['timeout']},
   {label: 'two-minute warning or end of quarter', color: '#e87ba4',
    stops: ['two_minute_warning', 'quarter_end']},
   {label: 'penalty', color: '#eda100', stops: ['penalty']}],
  [{label: 'score', color: '#199e70', stops: ['score']}],
];
const STOP = Object.fromEntries(STOPS.flat().flatMap(item => item.stops.map(stop => [stop, item])));

const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
                'August', 'September', 'October', 'November', 'December'];

export function drawGame(svg, game) {
  const {home, away, teams} = game;
  const target = {[home]: 100, [away]: 0};    // the end zone each team drives toward
  // a play's room either side of the first and last, so their markers clear the frame
  const x = d3.scaleLinear([-1, game.plays.length + 2], [MARGIN.left, WIDTH - MARGIN.right]);
  const y = d3.scaleLinear([-10, 110], [GAME.bottom, GAME.top]);

  svg = d3.select(svg);
  svg.selectAll('*').remove();
  svg.attr('viewBox', `0 0 ${WIDTH} ${HEIGHT}`).attr('class', 'game');

  // yard lines, darker at the goal lines and midfield, and quarter lines, which
  // stop at the goal lines to leave the end zones to the score labels
  svg.append('g').selectAll('line')
    .data(d3.range(0, 101, 10))
    .join('line')
    .attr('x1', x.range()[0]).attr('x2', x.range()[1])
    .attr('y1', y).attr('y2', y)
    .attr('stroke', d => d % 50 === 0 ? '#999' : '#ddd').attr('shape-rendering', 'crispEdges');
  // quarters start between the last play of one and the first of the next
  svg.append('g').selectAll('line')
    .data(game.quarters.filter(q => q.quarter > 1))
    .join('line')
    .attr('x1', q => x(q.play)).attr('x2', q => x(q.play))
    .attr('y1', y(0)).attr('y2', y(100))
    .attr('stroke', 'black').attr('stroke-width', q => q.quarter === 3 ? 1.5 : 1);

  svg.append('g').selectAll('line')
    .data(game.segments)
    .join('line')
    .attr('x1', s => x(s.play[0])).attr('x2', s => x(s.play[1]))
    .attr('y1', s => y(s.y[0])).attr('y2', s => y(s.y[1]))
    .attr('stroke', s => s.color).attr('stroke-width', 1)
    .attr('stroke-dasharray', s => STYLES[s.play_type] ?? SOLID);

  svg.append('g').selectAll('path')
    .data(game.plays)
    .join('path')
    .attr('d', p => SYMBOLS[p.kind]())
    .attr('transform', p => `translate(${x(p.play)},${y(p.y)})`)
    .attr('fill', p => p.color);

  svg.append('g').selectAll('text')
    .data(game.labels)
    .join('text')
    // the same distance into either end zone
    .attr('x', l => x(l.play)).attr('y', l => target[l.team] === 100 ? y(100) - 9 : y(0) + 9)
    .attr('fill', l => teams[l.team].color).attr('class', 'score')
    .attr('text-anchor', 'middle').attr('dominant-baseline', 'central')
    .text(l => l.score);

  // each team's name in the end zone it defends
  svg.append('g').selectAll('text')
    .data([[home, -5], [away, 105]])
    .join('text')
    .attr('x', x.range()[0] + 5).attr('y', ([, yards]) => y(yards))
    .attr('dominant-baseline', 'central')
    .attr('fill', ([team]) => teams[team].color).attr('class', 'team')
    .text(([team]) => teams[team].nick);

  // yards up both sides, with no ticks at the backs of the end zones; the
  // quarters are along the bottom of the clock panel
  bothSides(svg, x, axis => axis(y)
    .tickSizeOuter(0)
    .tickValues(d3.range(0, 101, 10))
    .tickFormat(d => 50 - Math.abs(d - 50)));
  axisTitle(svg, x, GAME, 'ball position');
  svg.append('rect')
    .attr('x', x.range()[0]).attr('y', y.range()[1])
    .attr('width', x.range()[1] - x.range()[0]).attr('height', y.range()[0] - y.range()[1])
    .attr('fill', 'none').attr('stroke', 'black').attr('stroke-width', 0.8);

  const [year, month, day] = game.date.split('-').map(Number);
  svg.append('text')
    .attr('x', (x.range()[0] + x.range()[1]) / 2).attr('y', 23)
    .attr('text-anchor', 'middle').attr('class', 'title')
    .text(`${teams[away].name} at ${teams[home].name}, ${MONTHS[month - 1]} ${day}, ${year}`);

  const legend = svg.append('g')
    .attr('transform', `translate(${x.range()[1]},${GAME.top - 12})`)
    .selectAll('g')
    .data(LEGEND.slice().reverse())
    .join('g');
  let right = 0;
  legend.each(function ({label, symbol, dash}) {
    const item = d3.select(this);
    const text = item.append('text').attr('class', 'legend').attr('text-anchor', 'end')
      .attr('dominant-baseline', 'central').attr('x', right).text(label);
    const width = text.node().getComputedTextLength();
    if (symbol) {
      item.append('path').attr('d', symbol())
        .attr('transform', `translate(${right - width - 14},0)`);
      right -= width + 38;
    } else {
      item.append('line')
        .attr('x1', right - width - 30).attr('x2', right - width - 6)
        .attr('stroke', 'black').attr('stroke-width', 1).attr('stroke-dasharray', dash);
      right -= width + 46;
    }
  });

  drawScore(svg, game, x);
  drawClock(svg, game, x);
}

// each team's score, a step after each play that scores, so that a touchdown and
// its extra point are two steps; the quarters marked as below, but not labeled
function drawScore(svg, game, x) {
  const {home, away, teams} = game;
  const most = d3.max([home, away], team => game.final_score[team]);
  const y = d3.scaleLinear([0, Math.max(most, 7)], [SCORE.bottom, SCORE.top]).nice(3);

  svg.append('g').selectAll('line')
    .data(y.ticks(3).filter(d => d > 0))
    .join('line')
    .attr('x1', x.range()[0]).attr('x2', x.range()[1])
    .attr('y1', y).attr('y2', y)
    .attr('stroke', '#ddd').attr('shape-rendering', 'crispEdges');
  svg.append('g').selectAll('line')
    .data(game.quarters.filter(q => q.quarter > 1))
    .join('line')
    .attr('x1', q => x(q.play)).attr('x2', q => x(q.play))
    .attr('y1', SCORE.bottom).attr('y2', SCORE.top)
    .attr('stroke', 'black').attr('stroke-width', q => q.quarter === 3 ? 1.5 : 1);

  // from 0-0 at the left edge to the final score at the right
  const line = d3.line(([play]) => x(play), ([, score]) => y(score)).curve(d3.curveStepAfter);
  svg.append('g').selectAll('path')
    .data([home, away])
    .join('path')
    .attr('d', team => line([[x.domain()[0], 0],
                             ...game.plays.map(p => [p.play, p.score[team]]),
                             [x.domain()[1], game.final_score[team]]]))
    .attr('fill', 'none').attr('stroke', team => teams[team].color).attr('stroke-width', 2);

  bothSides(svg, x, axis => axis(y).tickSizeOuter(0).ticks(3));
  axisTitle(svg, x, SCORE, 'score');
  svg.append('rect')
    .attr('x', x.range()[0]).attr('y', SCORE.top)
    .attr('width', x.range()[1] - x.range()[0]).attr('height', SCORE.bottom - SCORE.top)
    .attr('fill', 'none').attr('stroke', 'black').attr('stroke-width', 0.8);
}

// a bar for each play of the clock time it took, hanging down to at most
// CLOCK.most seconds, in the color of what stopped the clock, with the quarters
// marked as above
function drawClock(svg, game, x) {
  const y = d3.scaleLinear([0, CLOCK.most], [CLOCK.top, CLOCK.bottom]).clamp(true);
  const width = Math.max(1, x(1) - x(0) - 1.5);

  svg.append('g').selectAll('line')
    .data(y.ticks(3).filter(d => d > 0))
    .join('line')
    .attr('x1', x.range()[0]).attr('x2', x.range()[1])
    .attr('y1', y).attr('y2', y)
    .attr('stroke', '#ddd').attr('shape-rendering', 'crispEdges');
  svg.append('g').selectAll('line')
    .data(game.quarters.filter(q => q.quarter > 1))
    .join('line')
    .attr('x1', q => x(q.play)).attr('x2', q => x(q.play))
    .attr('y1', CLOCK.bottom).attr('y2', CLOCK.top)
    .attr('stroke', 'black').attr('stroke-width', q => q.quarter === 3 ? 1.5 : 1);

  // each play's down over its bar, in the offense's color; kicks and tries have none
  svg.append('g').selectAll('text')
    .data(game.plays.filter(p => p.down !== null))
    .join('text')
    .attr('x', p => x(p.play)).attr('y', DOWNS)
    .attr('text-anchor', 'middle').attr('dominant-baseline', 'central')
    .attr('fill', p => p.color).attr('class', 'down')
    .text(p => p.down);
  svg.append('text')
    .attr('x', x.range()[0] - 6).attr('y', DOWNS)
    .attr('text-anchor', 'end').attr('dominant-baseline', 'central').attr('class', 'axis-title')
    .text('down');

  const clock = seconds => `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`;
  svg.append('g').selectAll('rect')
    .data(game.plays.filter(p => p.duration !== null))
    .join('rect')
    .attr('x', p => x(p.play) - width / 2).attr('width', width)
    .attr('y', CLOCK.top).attr('height', p => y(p.duration) - CLOCK.top)
    .attr('fill', p => STOP[p.stop].color)
    .append('title')
    .text(p => `${p.quarter <= 4 ? `Q${p.quarter}` : 'OT'} ${clock(p.clock)}: ` +
               `${p.duration} seconds, ${STOP[p.stop].label}`);

  bothSides(svg, x, axis => axis(y)
    .tickSizeOuter(0)
    .ticks(3)
    .tickFormat(d => d === 0 ? '' : clock(d)));
  axisTitle(svg, x, CLOCK, 'play duration');
  // the quarters along the bottom, for both panels, the first at the frame
  const quarters = game.quarters;
  svg.append('g')
    .attr('transform', `translate(0,${CLOCK.bottom})`)
    .call(d3.axisBottom(x)
      .tickSizeOuter(0)
      .tickSize(4)
      .tickPadding(2)
      .tickValues(quarters.map(q => q.quarter === 1 ? x.domain()[0] : q.play))
      .tickFormat((_, i) => quarters[i].quarter <= 4 ? `Q${quarters[i].quarter}` : 'OT'));
  svg.append('rect')
    .attr('x', x.range()[0]).attr('y', CLOCK.top)
    .attr('width', x.range()[1] - x.range()[0]).attr('height', CLOCK.bottom - CLOCK.top)
    .attr('fill', 'none').attr('stroke', 'black').attr('stroke-width', 0.8);
}

// a y axis on both sides of a panel: make(d3.axisLeft), then make(d3.axisRight)
function bothSides(svg, x, make) {
  svg.append('g').attr('transform', `translate(${x.range()[0]},0)`).call(make(d3.axisLeft));
  svg.append('g').attr('transform', `translate(${x.range()[1]},0)`).call(make(d3.axisRight));
}

// a panel's name, up the left side, outside its axis
function axisTitle(svg, x, panel, text) {
  const middle = (panel.top + panel.bottom) / 2;
  svg.append('text')
    .attr('transform', `translate(${x.range()[0] - 40},${middle}) rotate(-90)`)
    .attr('text-anchor', 'middle').attr('dominant-baseline', 'central').attr('class', 'axis-title')
    .text(text);
}

// the legend for the clock bars, into an HTML element: what stopped the clock,
// one item to a line, in its groups
export function drawClockLegend(element) {
  const group = d3.select(element).selectAll('ul').data(STOPS).join('ul');
  const item = group.selectAll('li').data(items => items).join('li');
  item.append('span').attr('class', 'swatch').style('background', item => item.color);
  item.append('span').text(item => item.label);
}
