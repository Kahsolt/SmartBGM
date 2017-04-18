#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#==========================
#  Name:        Matcher
#  Author:      Kahsolt
#  Time:        2017/3/6
#  Desciption:  Use given tags to get recommended music piece in DB

# Configuration
MUSIC_ITEM_MAX = 20
MUSIC_MATCH_THRESHOLD = 0.5
MUSIC_DIR = r'./music/'
MUSIC_VOC=[
    '流行摇滚', '乡村民谣', '爵士蓝调', '金属朋克', '轻音乐', '古典', '国风', '电子', '说唱',
    '清晨', '下午茶', '夜晚', '学习工作', '运动旅行', '婚礼庆典', '影视', 'ACG',
    '清新明媚', '兴奋动感', '治愈感动', '怀旧伤感', '安静放松', '快乐', '浪漫', '孤独', '思念',
    '弦乐组', '管乐组', '室内乐', '钢琴', '电吉他', '口琴', '古筝', '二胡', '琵琶', '箫笛'
]
DB_LOCAL_FILE = r'MusicDB.db'

# Imports
import random

# Functions
def _String2Utf8(s):
    return s.encode('utf8')
def _Utf82String(s):
    return s.decode('utf8')

# Classes
class DBText:
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
                        song['tags'] = line.strip('\n')
                        self.dictMusic.append(song)
        except:
            print('DBText: no local db, MusicDB.update() needed')

    def __checkTags(self, tags):
        ntags = []
        for t in tags:
            if t in MUSIC_VOC:
                ntags.append(t)
            else:
                print('MusicDBAdmin: tag "' + t + '" is invalid, omitted')
        return ntags

    def __calcMatchScore(self, queryTags, songTags):
        if len(queryTags) == 0:
            return 1.0
        else:
            cnt = 0
            for t in queryTags:
                if t in songTags:
                    cnt += 1
            return cnt / len(queryTags)

    def query(self, tags):
        tags = self.__checkTags(tags)
        res = []
        for song in self.dictMusic:
            if self.__calcMatchScore(tags, song['tags']) == 1.0:
                res.append(MUSIC_DIR + _Utf82String(song['title']))
        return res

    def rank(self, tags):
        tags = self.__checkTags(tags)
        res = []
        for song in self.dictMusic:
            if self.__calcMatchScore(tags, song['tags']) > MUSIC_MATCH_THRESHOLD:
                res.append(MUSIC_DIR + _Utf82String(song['title']))
        #### another method: pick a certain number from th top
        # res = {}
        # for song in self.dictMusic:
        #     res[song['title']] = self.__calcMatchScore(tags, song['tags'])
        # sorted(res.items(), key = lambda t:t[1], reverse = True)
        return res

class Matcher():
    def __init__(self):
        self.dbText = DBText()

    def match(self,tags):
        smartbgm = self.dbText.query(tags)
        random.shuffle(smartbgm)
        return smartbgm[:MUSIC_ITEM_MAX]

    def search(self, tags):
        smartbgm = self.dbText.rank(tags)
        return smartbgm[:MUSIC_ITEM_MAX]

# Main Entrance
def main():
    # 0.Import the main class in this file
    #
    # from Matcher import Matcher

    # 1.Create a MusicDBAdmin object
    #   use it just like apt/aptitude
    #
    matcher = Matcher()

    # 2.Search for music using the given tag list
    #   invalid tags will rise a warning and be omitted
    #
    #   \return     a list of music names with base path (max item number = MUSIC_MAX)
    #
    tags = ['安静放松', '下午茶']
    res = matcher.match(tags)       # exactly matches all tags
    print(res)          # utf8 can't be printed
    tags = ['清晨', '学习工作', '安静放松', '下午茶']
    res = matcher.search(tags)      # relatively mathes some tags well (a bit slower)
    print(res)          # utf8 can't be printed

if __name__ == '__main__':
    main()
