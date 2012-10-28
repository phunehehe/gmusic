#!/usr/bin/env python

from collections import Counter
from gmusicapi.api import Api
import random
import re

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


def regen_playlist(api):

    # Find the correct playlists
    playlist_all = None
    playlist_neglected = None

    for playlist_name, playlist_id in api.get_all_playlist_ids(auto=False).values()[0].iteritems():

        if playlist_name == 'All':
            playlist_all = playlist_id
            if playlist_neglected:
                break

        elif playlist_name == 'Neglected':
            playlist_neglected = playlist_id
            if playlist_all:
                break

    # Put songs into a map with play counts as keys
    song_index = {}
    songs = api.get_playlist_songs(playlist_all)

    for song in songs:
        play_count = song['playCount']
        if play_count not in song_index:
            song_index[play_count] = [song]
        else:
            song_index[play_count].append(song)

    for play_count, songs in song_index.iteritems():
        print play_count, len(songs)

    # Put songs into a weighted list, songs with lower play count appears more times
    max_weight = max(song_index.iterkeys())
    haystack = []
    for play_count, songs in song_index.iteritems():
        weight = max_weight - play_count
        haystack.extend(songs * weight)

    # Take random songs from the weighted list
    needle = random.sample(haystack, 50)
    for song in needle:
        print song['playCount'], song['title']

    # And use that to update the playlist
    api.change_playlist(playlist_neglected, needle)


def main():

    api = Api()
    if not api.login(credentials.email, credentials.password):
        print "Couldn't log in :("
        return

    regen_playlist(api)
    #check_playlists(api)
    #fix_metadata(api)
    #fix_flac
    #reset_play_count(api)


if __name__ == '__main__':
    main()
