#!/usr/bin/env python

from gmusicapi import Mobileclient
from gmusic import regen_playlist

import credentials


def main():

    api = Mobileclient()
    if not api.login(credentials.email, credentials.password):
        print "Couldn't log in :("
        return

    regen_playlist(api, 'All')
    regen_playlist(api, 'Programming')


if __name__ == '__main__':
    main()
