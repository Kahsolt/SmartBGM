#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#==========================
#  Name:        Matcher
#  Author:      ???
#  Time:        yyyy/mm/dd
#  Desciption:  Try match video tags with audio tags

# Configurations
#
# put your module level global var here

# Imports
from MusicDB import MusicDB

# Classes
class Matcher:

    def __init__(self, tags_video):
        self.musicDB = MusicDB()
        pass

    def remix(self):
        pass
        # THIS MODULE MUST QUERY MusicDB!!!
        return 'path_to_outfile'


# Main Entrance
def main():
    # 1.Construct
    # matcher = Matcher(tags_video)

    # 2.Configure
    # matcher.mode = ??     # if we have multiple selection algorithms

    # 3.Call methods
    # path_to_audio = matcher.match()

    pass

if __name__ == '__main__':
    # Run a Module as Main will run the example test routine
    main()
