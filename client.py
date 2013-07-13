#!/usr/bin/env python

from gmusicapi import Webclient
from gmusic import regen_playlist

import credentials


def main():

    api = Webclient()
    if not api.login(credentials.email, credentials.password):
        print "Couldn't log in :("
        return

    regen_playlist(api, 'All', '_All', 20)
    regen_playlist(api, 'Programming', '_Programming', 20)


if __name__ == '__main__':
    main()
