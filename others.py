#!/usr/bin/env python

from collections import Counter
from gmusicapi import Mobileclient
import json

import credentials


def check_playlists(api):

    playlists = api.get_all_user_playlist_contents()
    songs = api.get_all_songs()

    def get_songs_from_playlist(playlist_name):
        playlist = next(p for p in playlists if p['name'] == playlist_name)
        return playlist['tracks']

    for playlist in playlists:
        print 'Looking for duplicates in %s' % playlist['name']
        counter = Counter((track['trackId'] for track in playlist['tracks']))
        for track_id in counter:
            if counter[track_id] > 1:
                song = next(s for s in songs if s['id'] == track_id)
                print song['title']

    print 'Looking for uncategoried songs'
    all_songs = [track['id'] for track in get_songs_from_playlist('All')]
    programming_songs = [track['id'] for track in get_songs_from_playlist('Programming')]
    non_programming_songs = [track['id'] for track in get_songs_from_playlist('NonProgramming')]
    for song in songs:
        if (song['id'] not in all_songs and
            song['id'] not in programming_songs and
            song['id'] not in non_programming_songs):
           print song['title']

    print 'Looking for miscategorized songs'
    print set.intersection(*map(set, [all_songs, programming_songs, non_programming_songs]))

    print 'Looking for something weird'
    song_ids = [song['id'] for song in songs]
    all_songs = get_songs_from_playlist('All')
    programming_songs = get_songs_from_playlist('Programming')
    non_programming_songs = get_songs_from_playlist('NonProgramming')
    for playlist in [all_songs, programming_songs, non_programming_songs]:
        for track in playlist:
            if track['trackId'] not in song_ids:
                print json.dumps(track)

    if len(songs) != (len(all_songs) + len(programming_songs) + len(non_programming_songs)):
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
        name_without_flac = name.replace('.flac', '')
        song['name'] = name_without_flac
    api.change_song_metadata(songs)


def reset_play_count(api):
    for playlist_name, playlist_id in api.get_all_playlist_ids(auto=False).values()[0].iteritems():
        if playlist_name in ('All', 'Programming'):
            songs = api.get_playlist_songs(playlist_id)
            for song in songs:
                song['playCount'] = 0
            api.change_song_metadata(songs)


def main():

    api = Mobileclient()
    if not api.login(credentials.email, credentials.password):
        print "Couldn't log in :("
        return

    #check_playlists(api)
    #fix_metadata(api)
    #fix_flac(api)
    reset_play_count(api)


if __name__ == '__main__':
    main()
