#!/usr/bin/env python

import random
import unicodedata
import json
from datetime import datetime


def regen_playlist(api, source_name, length=20):

    playlists = api.get_all_user_playlist_contents()
    songs = api.get_all_songs()

    source = next(p for p in playlists if p['name'] == source_name)
    now = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    destination_id = api.create_playlist('%s %s' % (source_name, now))


    # Put songs into a map with play counts as keys
    song_index = {}

    for track in source['tracks']:
        track_id = track['trackId']
        try:
            song = next(s for s in songs if s['id'] == track_id)
        except StopIteration:
            print 'Something is wrong with track'
            print json.dumps(track)
            continue
        play_count = song['playCount']
        if play_count not in song_index:
            song_index[play_count] = [track_id]
        else:
            song_index[play_count].append(track_id)


    # Put songs into a weighted list, songs with lower play count appears more
    # times
    max_weight = max(song_index.iterkeys())
    haystack = []
    for play_count, songs in song_index.iteritems():
        # Plus one in case play_count is the same as max_weight
        weight = max_weight - play_count + 1
        haystack.extend(songs * weight)


    # Take random songs from the weighted list
    needle = random.sample(haystack, length)

    api.add_songs_to_playlist(destination_id, needle)
