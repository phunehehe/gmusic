#!/usr/bin/env python

import random
import unicodedata


def regen_playlist(api, source_name, destination_name, length=50):

    playlists = api.get_all_playlist_ids(auto=False).values()[0]
    source = playlists[source_name]
    destination = playlists[destination_name]

    # Put songs into a map with play counts as keys
    song_index = {}
    songs = api.get_playlist_songs(source)

    for song in songs:
        play_count = song['playCount']
        if play_count not in song_index:
            song_index[play_count] = [song]
        else:
            song_index[play_count].append(song)

    # Put songs into a weighted list, songs with lower play count appears more times
    max_weight = max(song_index.iterkeys())
    haystack = []
    for play_count, songs in song_index.iteritems():
        weight = max_weight - play_count
        haystack.extend(songs * weight)

    # Take random songs from the weighted list
    needle = random.sample(haystack, length)
    api.change_playlist(destination, needle)
