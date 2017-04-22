#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#==========================
#  Name:        Matcher
#  Author:      Kahsolt
#  Time:        2017/3/6
#  Desciption:  Use given tags to get recommended music piece in DB

# Configuration
MUSIC_ITEM_MAX = 15
MUSIC_MATCH_THRESHOLD = 0.25

# Imports
import random
from MusicDB import MUSIC_VOC, MUSIC_DIR, MUSIC_AUX_SCENE, DB_LOCAL_FILE

# Functions
def _String2Utf8(s):
    return s.encode('utf8')
def _Utf82String(s):
    return s.decode('utf8')

# Classes
class DB:
    def __init__(self):
        self.dictMusic = []
        try:
            with open(DB_LOCAL_FILE, 'r') as fdb:
                while True:
                    line = fdb.readline()   # should be title
                    if line == '':
                        break
                    else:
                        song = {}
                        song['title'] = line.strip('\n')
                        line = fdb.readline()
                        song['length'] = int(line.strip('\n'))
                        line = fdb.readline()
                        song['tags'] = line.strip('\n')
                        self.dictMusic.append(song)
        except:
            print('DB: no local db, MusicDB.update() needed')

    def _checkTags(self, tags):
        ntags = []
        for t in tags:
            if t in MUSIC_VOC or t in MUSIC_AUX_SCENE:
                ntags.append(t)
            else:
                print('DB: tag "' + t + '" is invalid, omitted')
        return ntags

    def _calcMatchScore(self, queryTags, songTags):
        if len(queryTags) == 0:
            return 1.0
        else:
            cnt = 0
            for t in queryTags:
                if t in songTags:
                    cnt += 1
            return cnt / len(queryTags)

    def query(self, tags):
        tags = self._checkTags(tags)
        res = []
        for song in self.dictMusic:
            if self._calcMatchScore(tags, song['tags']) == 1.0:
                s = (MUSIC_DIR + _Utf82String(song['title']), song['length'])
                res.append(s)
        return res

    def rank(self, tags):
        tags = self._checkTags(tags)
        res = []
        for song in self.dictMusic:
            if self._calcMatchScore(tags, song['tags']) > MUSIC_MATCH_THRESHOLD:
                s = (MUSIC_DIR + _Utf82String(song['title']), song['length'])
                res.append(s)
        #### another method: pick a certain number from the top
        # res = {}
        # for song in self.dictMusic:
        #     res[song['title']] = self._calcMatchScore(tags, song['tags'])
        # sorted(res.items(), key = lambda t:t[1], reverse = True)
        return res

class Matcher():
    def __init__(self, videoTags):
        self.db = DB()
        self.videoTags = videoTags

    def match(self):
        smartbgm = self.db.query(self.videoTags)
        random.shuffle(smartbgm)
        return smartbgm[:MUSIC_ITEM_MAX]

    def search(self):
        smartbgm = self.db.rank(self.videoTags)
        return smartbgm[:MUSIC_ITEM_MAX]

# Main Entrance
def main():
    # 0.Import the main class in this file
    #
    # from Matcher import Matcher

    # 1.Create a MusicDBAdmin object
    #   use it just like apt/aptitude
    #
    matcher = Matcher(['安静放松', '下午茶'])
    searcher = Matcher(['清晨', '安静放松', '下午茶'])

    # 2.Search for music using the given tag list
    #   invalid tags will rise a warning and be omitted
    #
    #   \return     a list of music names with base path (max item number = MUSIC_ITEM_MAX)
    #
    res = matcher.match()       # exactly matches all tags
    print(res)                  # utf8 can't be printed
    res = searcher.search()     # relatively matches some tags well (a bit slower)
    print(res)                  # utf8 can't be printed

if __name__ == '__main__':
    main()
