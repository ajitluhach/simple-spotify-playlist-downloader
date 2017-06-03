#!/usr/bin/env/ python3

import webbrowser
import argparse
import http.client
import http.server
import re
import json
import codecs
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


class SpotifyAPI():

        # Requires an OAuth token.
        def __init__(self, auth):
                self._auth = auth

        @staticmethod
        def authorize(client_id, scope):
                webbrowser.open('https://accounts.spotify.com/authorize?'
                                + urllib.parse.urlencode({
                                        'response_type': 'token',
                                        'client_id': client_id,
                                        'scope': scope,
                                        'redirect_uri':
                                        'http://127.0.0.1:43019/redirect'
                                }))

                # Start a simple, local HTTP server to listen for the authorization token... (i.e. a hack).
                server = SpotifyAPI._AuthorizationServer('127.0.0.1', '43019')
                try:
                        while True:
                                server.handle_request()
                except SpotifyAPI._Authorization as auth:
                        return SpotifyAPI(auth.access_token)

        class _AuthorizationServer(http.server.HTTPServer):
            """To get the authorization token from the url, khichdi c bnegi yhaaan"""
            def __init__(self, host, port):
                        http.server.HTTPServer.__init__(self, (host, port), SpotifyAPI._AuthorizationHandler)
                        # calling the authorization handler of the api with last argument, first is the location of the server, redirect uri

                # Disable the default error handling.
            def handle_error(self, request, client_address):
                        raise

        class _AuthorizationHandler(http.server.BaseHTTPRequestHandler):
                def do_GET(self):
                    """The Spotify API has redirected here, but access_token
                    is hidden in the URL fragment. Read it using JavaScript
                    and send it to /token as an actual query string...
                    """
                    if self.path.startswith('/redirect'):
                                self.send_response(200)
                                self.send_header('Content-Type', 'text/html')
                                self.end_headers()
                                # Replacing the \redirect with token content, in current location, using this script
                                self.wfile.write(b'<script>location.replace("token?" + location.hash.slice(1))</script>')

                    # Read access_token and use an exception to kill the server listening..
                    elif self.path.startswith('/token?'):
                            self.send_response(200)
                            self.send_header('Content-Type', 'text/html')
                            self.end_headers()
                            self.wfile.write(b'<script>close()</script>Thanks! You may now close this window.')
                            raise SpotifyAPI._Authorization(
                                    re.search('access_token=([^&]*)', self.path).group(1))

                    else:
                                self.send_error(404)

                # Disable the default logging.
                def log_message(self, format, *args):
                        pass

        class _Authorization(Exception):
            """Initializes the access token after raising the exception"""
            def __init__(self, access_token):
                    self.access_token = access_token


def log(str):
        sys.stdout.buffer.write('[{}] {}\n'.format(time.strftime('%I:%M:%S'), str).encode(sys.stdout.encoding, errors='replace'))
        sys.stdout.flush()


def main():
        # Parse arguments.
        parser = argparse.ArgumentParser(description='Exports your Spotify \
                                    playlists. By default, opens a \
                                    browser window to authorize the \
                                    Spotify Web API, but you can also manually\
                                    specify an OAuth token with\
                                    the --token option.')
        parser.add_argument('--token', metavar='OAUTH_TOKEN', help='use a Spotify OAuth token (requires the '
                                                   + '`playlist-read-private` permission)')
        parser.add_argument('--format', default='csv', choices=['json', 'csv'], help='output format (default: csv)')
        parser.add_argument('file', help='output filename', nargs='?')
        args = parser.parse_args()

        # If they didn't give a filename, then just prompt them. (They probably just double-clicked.)
        while not args.file:
                args.file = input('Enter a file name (e.g. playlists.txt): ')

        # Log into the Spotify API.
        if args.token:
                spotify = SpotifyAPI(args.token)
        else:
                spotify = SpotifyAPI.authorize(client_id='2d7eef1f8e014d60a92e94e164a7f11a', scope='playlist-read-private')

        # Showing who is logged in
        me = spotify.get('me')
        log('Logged in as {display_name} ({id})'.format(**me))


