# A Simple Spotify Playlist Downloader

This is command line utility uses youtube-dl to downloader music from your saved playlists on spotify, with proper album art and metadata.
You can login to your spotify account using Facebook Login or your username.
Permissions Required : playlist-read-private
Only Python3 Support
(Didn't create it for python2)

## Features

* Adds spotify album art url in the csv file itself, (easy download)
* Prompts User to login ones via Facebook or Username (No need to register your own application)
* Choice to save only selected playlists
* Adds metadata to downloaded songs
* Download Progress bar
* Adds Album Art in two sizes, 300x300 is default
* Skip already downloaded songs
* Give the number of songs to skip

## TODO

* Download only the songs of higher popularity, instead of downloading the complete playlist.
* (thinking......)

## Installation

* Clone the repo

    `git clone https://github.com/ajitluhach/simple-spotify-playlist-downloader.git`
    
    `cd simple-spotify-playlist-downloader`    
    
* Install the dependecies from the requirements.txt, run this in terminal

    `python3 -m pip install requierments.txt`

## Usage

* Create a CSV Backup of playlists that you want to download using `download_playlist.py`, currently only one format is supported (csv), Usage:

        `python3 download_playlist.py -h`
        
* Provide the playlists as input to the file `download_mp3_from_csv.py`, run this for detailed options

        python3 download_mp3_from_csv.py playlist.csv -f downloadfolder -c -s 4
        
* For more detailed options run: 

        `python3 download_mp3_from_csv.py -h`


## Dependencies

Depends on following three libraries
* youtube-dl
* eyed3
* progressbar33

## Credits
* Idea of creating this came from very similar project by Ashish Madeti
* (I don't know how to tag someone here)

## PS
this was just for fun
