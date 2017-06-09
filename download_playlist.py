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
import csv
import os


class SpotifyAPI():

        # Requires an OAuth token.
        def __init__(self, auth):
                self._auth = auth

        def get(self, url, params={}, tries=3):
            """Get a resource from the SpotifyAPI and returns an object, e.g get(me) returns object of "me" which is an url"""

            # Construct the correct url, which is in the form e.g https://api.spotify.com/v1/me
            if not url.startswith('https://api.spotify.com/v1/'):
                url = 'https://api.spotify.com/v1/' + url
            if params:
                url += ('&' if '?' in url else '?') + urllib.parse.urlencode(params)
            # Try sending the request a specified number of times
            for _ in range(tries):
                try:
                    req = urllib.request.Request(url)
                    req.add_header('Authorization', 'Bearer ' + self._auth)
                    response = urllib.request.urlopen(req)
                    reader = codecs.getreader('utf-8')
                    return json.load(reader(response))
                except Exception as err:
                    log('Couldn\'t load the URL: {} {}'.format(url, err))
                    time.sleep(2)
                    log('Trying again')
            sys.exit(1)

        def list(self, url, params={}):
            response = self.get(url, params)
            items = response['items']
            while response['next']:
                response = self.get(response['next'])
                items += response['items']
            return items

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
                server = SpotifyAPI._AuthorizationServer('127.0.0.1', 43019)
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
        parser.add_argument('--format', default='csv', choices=['csv'], help='output format, (default: csv)')
        args = parser.parse_args()
        files = {}
        # Log into the Spotify API.
        if args.token:
                spotify = SpotifyAPI(args.token)
        else:
                spotify = SpotifyAPI.authorize(client_id='2d7eef1f8e014d60a92e94e164a7f11a', scope='playlist-read-private')

        # Showing who is logged in
        me = spotify.get('me')
        log('Logged in as {display_name} ({id})'.format(**me))

        # List all the playlists
        playlists = spotify.list('users/{user_id}/playlists'
                                 .format(user_id=me['id']), {'limit': 50})
        for playlist in playlists:
            log('Loading Playlist: {name} ({tracks[total]} songs)'
                .format(**playlist))
            playlist['tracks'] = spotify.list(playlist['tracks']
                                              ['href'], {'limit': 100})
            files[playlist['name']] = playlist['tracks']

        print()
        print("Which Playlist would You like to download enter the number of the playlists, seperated by spaces or\
                \nEnter 'all' to download all of them ")
        to_choose_from = list(files.keys())

        valid = False
        choices = []
        while not valid:
            for index, name in enumerate(to_choose_from):
                print("{} : {}".format(index, name))
            choice = input(">>>")
            if choice:
                if choice == "all":
                    choices = to_choose_from
                    valid = True
                else:
                    numeric = [int(x) for x in choice.split(" ")]
                    for num in numeric:
                        try:
                            choices.append(to_choose_from[num])
                            valid = True
                        except IndexError:
                            valid = False
                            print("Invalid choice of Playlists, Try Again!!")
                            continue
            else:
                print("You didn't provide me with any playlist,\
                        if you  wanted to exit Try ctrl + c")
                continue

        if args.format != 'csv':
            print('Invalid file type, only json and\
                    csv supported, switching to csv')
        for playlist in choices:
            file = playlist + '.csv'
            if os.path.exists(file):
                print("{} Exists, Overwriting  ".format(file))
            else:
                print(playlist)
            with open(file, 'w', encoding='utf-8') as csvfile:
                print("\tWriting To {}".format(file))
                fieldnames = ["Track", "Artist", "Album", "ImageURL6",
                              "ImageURL3"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for data in files[playlist]:
                    needed_data = {
                            "Track": data["track"]["name"],
                            "Artist": data["track"]["artists"][0]["name"],
                            "Album": data["track"]["album"]["name"],
                            "ImageURL6": data["track"]["album"]["images"]
                            [0]["url"],
                            "ImageURL3": data["track"]["album"]["images"]
                            [1]["url"]
                            }
                    writer.writerow(needed_data)


if __name__ == '__main__':
    main()
