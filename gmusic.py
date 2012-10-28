#!/usr/bin/env python

from collections import Counter
import re
from gmusicapi.api import Api

import credentials


def check_playlists(api):

    playlists = {}
    for playlist_name, playlist_id in api.get_all_playlist_ids(auto=False).values()[0].iteritems():
        print 'Looking for duplicates in %s' % playlist_name
        playlist_songs = [song['id'] for song in api.get_playlist_songs(playlist_id)]
        counter = Counter(playlist_songs)
        print [song for song in counter if counter[song] > 1]
        playlists[playlist_name] = playlist_songs

    print 'Looking for uncategoried songs'
    all_songs = playlists['All']
    staging_songs = playlists['Staging']
    programming_songs = playlists['Programming']
    non_programming_songs = playlists['NonProgramming']

    songs = api.get_all_songs()
    song_ids = [song['id'] for song in songs]

    weird_song_ids = [song for song in song_ids if
            song not in all_songs and
            song not in staging_songs and
            song not in programming_songs and
            song not in non_programming_songs]
    weird_songs = [song for song in songs if song['id'] in weird_song_ids]

    for song in weird_songs:
        print '%s: %s' % (song['album'], song['name'])

    if len(songs) != (len(all_songs) + len(staging_songs) + len(programming_songs) + len(non_programming_songs)):
        print 'Something is wrong'


def fix_metadata(api):

    songs = api.get_all_songs()

    for key in ['album', 'genre']:
        print 'Fixing garbage in %s' % key
        weird_songs = [song for song in songs if song[key] == '-']

        if weird_songs:
            for song in weird_songs:
                print song['name']
                song[key] = ''

            api.change_song_metadata(weird_songs)


def fix_flac(api):
    songs = api.search('.flac')['song_hits']
    for song in songs:
        name = song['name']
        print name
        if song['track'] == 0:
            song['track'] = int(name.split()[0])
        name_without_flac = name.replace('.flac', '')
        song['name'] = re.sub('[0-9]+ ', '', name_without_flac)
    api.change_song_metadata(songs)


def reset_play_count(api):
    for playlist_name, playlist_id in api.get_all_playlist_ids(auto=False).values()[0].iteritems():
        if playlist_name in ('All', 'Programming'):
            songs = api.get_playlist_songs(playlist_id)
            for song in songs:
                song['playCount'] = 0
            api.change_song_metadata(songs)


def main():

    api = Api()
    if not api.login(credentials.email, credentials.password):
        print "Couldn't log in :("
        return

    #check_playlists(api)
    #fix_metadata(api)
    #fix_flac
    #reset_play_count(api)


if __name__ == '__main__':
    main()
