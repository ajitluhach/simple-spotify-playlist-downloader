import csv
import argparse
import os
import eyed3
import urllib.request
import youtube_dl
import urllib
from progressbar import ProgressBar


def get_all_songs(file, tag=5, skip=0):
    """Takes the csv file as input and returns the list of songs in the files,
    list of dictionaries
    Args:
      file : Name of csv file
      tag: dimension of album art (default = 300x300, row number 5 in the file)
      skip: number of songs to skip (default=0)
    each song has a name, artist, and a image_url
    """
    songs = []
    with open(file, "r") as csvfile:
        reader = csv.reader(csvfile)
        # Ignore the headers
        next(reader)
        if skip:
            for _ in range(skip):
                next(reader)
        for row in reader:
            songs.append(
                    {"name": row[0].strip(),
                        "artist": row[1].strip(),
                        "album": row[2].strip(),
                        "art": row[tag-1]})
    return songs


def get_art(url, image_name):
    image_name = image_name[:-3] + "jpg"
    urllib.request.urlretrieve(url, image_name)
    return image_name


def add_metadata_to_song(song_name, song_data):
    audiofile = eyed3.load(song_name)
    audiofile.tag.title = song_data['name']
    audiofile.tag.artist = song_data['artist']
    audiofile.tag.album = song_data['album']
    imagename = get_art(song_data['art'], song_name)
    imagedata = open(imagename, "rb").read()
    audiofile.tag.images.set(3, imagedata, "image/jpeg", u"This image is same\
                             as the spotify album art for this song")
    os.remove(imagename)
    audiofile.tag.save()


class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def download_songs(songs, folder):
    def custom_hook(d):
            """Hook to intercept flow of data from youtube-dl and output\
                    custom messages"""
            if d['status'] == 'downloading':
                    download_progress_bar = ProgressBar(maxval=100).start()
                    download_percentage = float(d['downloaded_bytes']
                                                / float(d['total_bytes']) * 100)
                    download_progress_bar.update(download_percentage)
            if d['status'] == 'finished':
                    print('\x1b[1A\x1b[2K')
                    filename = d['filename']
                    filename = os.path.basename(filename)
                    print("\x1b[1A[\033[93mConverting\033[00m]\
                            {}".format(filename))
    # Youtubedl options
    opts = {
          'format': 'bestaudio/best',
          'forcefilename': True,
          'postprocessors': [{
              'key': 'FFmpegExtractAudio',
              'preferredcodec': 'mp3',
              'preferredquality': '256',
          }],
          'progress_hooks': [custom_hook],
          'logger': MyLogger(),
      }
    for song in songs:
        probable_filename = folder + '/' + song['name'] + ' - ' +\
            song['artist'] + '.mp3'
        if os.path.isfile(probable_filename):
            # The file may already be there, so skip
            print('[\033[93mSkipping\033[00m] {} by {}'.format
                  (song['name'], song['artist']))
            continue
        # Name of the current song
        opts['outtmpl'] = folder + '/' + song['name'] + ' - ' + song['artist']\
            + '.%(ext)s'
        url = ' '.join([song['name'], song['artist'], 'audio', 'youtube'])
        url = 'gvsearch1:' + url
        print('[\033[91mFetching\033[00m] {}'.format(probable_filename))
        with youtube_dl.YoutubeDL(opts) as ydl:
            ydl.download([url])
        if os.path.isfile(probable_filename):
            add_metadata_to_song(probable_filename, song)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--folder", help="Keep the files in the\
                        folder specified")
    parser.add_argument('-c', '--create', help="try to create folder\
            if doesn't exist",
                        action="store_true")
    parser.add_argument("-s", "--size", help="Dimension of the Album art 4 is\
            600x600 (not supported by some or all smartphone, I'm not sure)\
            and 5 is 300x300 \n\
            Note that 300x300 is for all smartphone compatible,",
                        choices=[4, 5], type=int, default=5)
    parser.add_argument('--skip', help="number of songs to skip from\
            the start of csv", type=int)
    parser.add_argument('csv', help="provide the name of the csv file\
            to download music from")
    args = parser.parse_args()

    if os.path.isfile(args.csv):
        csvfile = args.csv
    else:
        print("No such file exists")
        exit()
    if args.folder:
        if os.path.isdir(args.folder):
            folder = os.path.abspath(args.folder)
        elif args.create:
            try:
                os.mkdir(args.folder)
                folder = os.path.abspath(args.folder)
                print("Creating folder '{}'".format(folder))
            except Exception:
                print("Error creating folder")
                raise
        else:
            print("No such folder, Exiting....")
            exit()
        print("Storing Files In.....: ", folder)
    songs = get_all_songs(csvfile, args.size, args.skip)
    download_songs(songs, folder)


if __name__ == '__main__':
    main()
