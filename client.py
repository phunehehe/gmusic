#!/usr/bin/env python

from gmusicapi.api import Api
from gmusic import regen_playlist

import credentials


def main():

    api = Api()
    if not api.login(credentials.email, credentials.password):
        print "Couldn't log in :("
        return

    regen_playlist(api, 'All', 'Neglected')
    regen_playlist(api, 'Programming', 'NewProgramming')


if __name__ == '__main__':
    main()
