#!/usr/bin/env python

from gmusicapi.api import Api
import random
import unicodedata

import credentials


def regen_playlist(api, source, destination, length=50):

    # Put songs into a map with play counts as keys
    song_index = {}
    songs = api.get_playlist_songs(source)

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
    needle = random.sample(haystack, length)
    for song in needle:
        print song['playCount'], unicodedata.normalize('NFKD', song['title']).encode('ascii','ignore')

    # And use that to update the playlist
    api.change_playlist(destination, needle)


def main():

    api = Api()
    if not api.login(credentials.email, credentials.password):
        print "Couldn't log in :("
        return

    playlists = api.get_all_playlist_ids(auto=False).values()[0]
    regen_playlist(api, playlists['All'], playlists['Neglected'])
    regen_playlist(api, playlists['Programming'], playlists['NewProgramming'])


if __name__ == '__main__':
    main()
