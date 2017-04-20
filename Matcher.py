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
        self.nrank = 5
        self.musicDB = MusicDB()
        self.tags_video = tags_video

    def match(self):
        # THIS MODULE MUST QUERY MusicDB!!!
        return 'path_to_outfile'


# Main Entrance
def main():

    tags_video = [(818, 1.2973), (733, 1.2946), (815, 0.9228999999999999), (111, 0.6920000000000001), (904, 0.45990000000000003)]
    matcher = Matcher(tags_video)
    merge_tags = matcher.match()

    pass

if __name__ == '__main__':
    # Run a Module as Main will run the example test routine
    main()
