// The game page: a graph of one game, always, and below it a pageable list of
// games, most recent first, with multi-select filters for year, week and team.
// The game shown is the one in the URL (?game=<game_id>), or else the most recent.

import {drawClockLegend, drawGame} from './draw.js';

const PAGE_SIZE = 20;
const WEEKS = [...Array.from({length: 18}, (_, i) => String(i + 1)), 'WC', 'DIV', 'CONF', 'SB'];

const svg = document.getElementById('game');
const message = document.getElementById('message');
const filtersElement = document.getElementById('filters');
const listElement = document.getElementById('games');
const pagerElement = document.getElementById('pager');

let games = [];      // every game of every season, most recent first
let teams = {};      // abbreviation -> {name, nick}, the latest season's where they differ
const filters = {season: new Set(), week: new Set(), team: new Set()};
let page = 0;
let shown = null;    // the game_id of the game drawn

// every season's index, as nginx lists the season directories
const listing = await d3.json('games/');
const seasons = listing.filter(entry => entry.type === 'directory').map(entry => entry.name).sort();
for (const index of await Promise.all(seasons.map(season => d3.json(`games/${season}/index.json`)))) {
  Object.assign(teams, index.teams);
  games.push(...index.games.map(game => ({...game, season: String(index.season)})));
}
games.sort((a, b) => d3.descending(a.date, b.date) || d3.descending(a.game_id, b.game_id));

drawClockLegend(document.getElementById('clock-legend'));
buildFilters();
showList();
await showGame(new URLSearchParams(location.search).get('game') ?? games[0].game_id);

window.addEventListener('popstate', () =>
  showGame(new URLSearchParams(location.search).get('game') ?? games[0].game_id));

async function showGame(gameId) {
  try {
    drawGame(svg, await d3.json(`games/${gameId.slice(0, 4)}/${gameId}.json`));
    message.textContent = '';
  } catch {
    message.textContent = `There is no game ${gameId}.`;
    return;
  }
  shown = gameId;
  listElement.querySelectorAll('tr').forEach(row =>
    row.classList.toggle('shown', row.dataset.game === shown));
}

function choose(gameId) {
  if (gameId === shown) return;
  history.pushState(null, '', `?game=${gameId}`);
  showGame(gameId);
}

function buildFilters() {
  const options = {
    season: [...seasons].reverse().map(season => [season, season]),
    week: WEEKS.map(week => [week, /^\d/.test(week) ? `Week ${week}` : week]),
    team: Object.keys(teams).sort().map(team => [team, `${team} ${teams[team].nick}`]),
  };
  const names = {season: 'Year', week: 'Week', team: 'Team'};
  for (const [key, values] of Object.entries(options)) {
    const details = d3.select(filtersElement).append('details').attr('class', 'filter');
    const summary = details.append('summary');
    const update = () => {
      const chosen = [...filters[key]];
      summary.text(`${names[key]}: ${chosen.length === 0 ? 'all'
        : chosen.length <= 3 ? chosen.join(', ') : `${chosen.length} chosen`}`);
    };
    const box = details.append('div').attr('class', 'options');
    box.append('button').attr('type', 'button').text('Clear').on('click', () => {
      filters[key].clear();
      box.selectAll('input').property('checked', false);
      update();
      page = 0;
      showList();
    });
    const label = box.selectAll('label').data(values).join('label');
    label.append('input').attr('type', 'checkbox').attr('value', ([value]) => value)
      .on('change', function () {
        this.checked ? filters[key].add(this.value) : filters[key].delete(this.value);
        update();
        page = 0;
        showList();
      });
    label.append('span').text(([, text]) => text);
    update();
  }
  // close an open filter when another opens, or on a click elsewhere
  document.addEventListener('click', event => {
    filtersElement.querySelectorAll('details[open]').forEach(details => {
      if (!details.contains(event.target)) details.open = false;
    });
  });
}

function matches(game) {
  return (filters.season.size === 0 || filters.season.has(game.season)) &&
         (filters.week.size === 0 || filters.week.has(game.week)) &&
         (filters.team.size === 0 || filters.team.has(game.home) || filters.team.has(game.away));
}

function showList() {
  const matching = games.filter(matches);
  const pages = Math.max(1, Math.ceil(matching.length / PAGE_SIZE));
  page = Math.min(page, pages - 1);
  const rows = d3.select(listElement).selectAll('tr')
    .data(matching.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE), game => game.game_id)
    .join(enter => {
      const row = enter.append('tr').attr('data-game', game => game.game_id);
      row.append('td').attr('class', 'date').text(game => game.date);
      row.append('td').attr('class', 'week')
        .text(game => /^\d/.test(game.week) ? `Week ${game.week}` : game.week);
      row.append('td').attr('class', 'matchup').html(game => {
        const team = abbr => `<span title="${teams[abbr]?.name ?? abbr}">${abbr}</span>`;
        return `${team(game.away)} ${game.away_score} <span class="at">at</span> ` +
               `${team(game.home)} ${game.home_score}`;
      });
      return row.on('click', (_, game) => choose(game.game_id));
    })
    .classed('shown', game => game.game_id === shown)
    .order();

  const pager = d3.select(pagerElement);
  pager.selectAll('*').remove();
  if (matching.length === 0) {
    pager.append('span').text('No games match.');
    return;
  }
  pager.append('button').attr('type', 'button').text('‹ Newer')
    .property('disabled', page === 0).on('click', () => { page--; showList(); });
  pager.append('span').text(` Page ${page + 1} of ${pages}, ${matching.length} games `);
  pager.append('button').attr('type', 'button').text('Older ›')
    .property('disabled', page === pages - 1).on('click', () => { page++; showList(); });
}
