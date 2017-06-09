# A Simple Spotify Playlist Downloader

This is command line utility uses youtube-dl to downloader music from your saved playlists on spotify, with proper album art and metadata.
"You can login to your spotify account using Facebook Login or your username.
"Permissions Required : playlist-read-private
Only Python3 Support
(Didn't create it for python2 support)

## Features

* Adds metadata to downloaded songs
* Download Progress
* Adds Album Art
* Skip already downloaded songs
* Give the number of songs to skip

## TODO

* Download only the songs of higher popularity, instead of downloading the complete playlist.
* (thinking......)

## Installation

1. First you'll have to make a csv backup of your playlist using the following repo
        'git clone https://github.com/ajitluhach/spotify-playlist-to-csv.git'
2. Clone the repo using these commands
        `git clone https://github.com/ajitluhach/simple-spotify-playlist-downloader.git`
        `cd simple-spotify-playlist-downloader`
3. Install the dependecies from the requirements.txt, run this in terminal
        `python3 -m pip install requierments.txt`

## Usage

1. Create a CSV Backup of playlists that you want to download from the script in STEP 1 of Installation
2. Provide the playlists as input to the file `download_mp3_from_csv.py`, run this for options
        `python3 download_mp3_from_csv.py -h`
Example:
        `python3 download_mp3_from_csv.py playlist.csv -f downloadfolder -c -s 4`

        `-s 4` is for size of album art 600x600, check help for details


## License

This script is slightly modified version of one created by Ashish Madeti, Under MIT License.
