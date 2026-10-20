"""Serve the game page locally the way nginx does on the site: the page from
web/ at /football/, and the built game files at /football/games/, where a
request for X.json gets X.json.gz with Content-Encoding: gzip, and
/football/games/ lists the seasons as nginx's autoindex_format json does.

    .venv/bin/python scripts/serve.py [--port 8000] [--games games]
"""

import argparse
import functools
import http.server
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, games, **kwargs):
        self.games = games
        super().__init__(*args, directory=str(ROOT / 'web'), **kwargs)

    def do_GET(self):
        path = self.path.split('?', 1)[0]
        if path == '/football/games/':    # as nginx's autoindex_format json lists them
            listing = [{'name': dir.name, 'type': 'directory'}
                       for dir in sorted(self.games.iterdir()) if dir.is_dir()]
            body = json.dumps(listing).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path.startswith('/football/games/') and path.endswith('.json'):
            file = self.games / (path.removeprefix('/football/games/') + '.gz')
            if not file.is_file():
                return self.send_error(404)
            body = file.read_bytes()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Encoding', 'gzip')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path == '/football':
            self.send_response(301)
            self.send_header('Location', '/football/')
            self.end_headers()
        elif path.startswith('/football/'):
            self.path = self.path.removeprefix('/football')
            super().do_GET()
        else:
            self.send_error(404)


def main():
    parser = argparse.ArgumentParser(description='Serve the game page locally.')
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--games', default=str(ROOT / 'games'), help='the built game files')
    args = parser.parse_args()
    handler = functools.partial(Handler, games=Path(args.games))
    print(f'http://127.0.0.1:{args.port}/football/')
    http.server.ThreadingHTTPServer(('127.0.0.1', args.port), handler).serve_forever()


if __name__ == '__main__':
    main()
