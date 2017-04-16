#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#==========================
#  Name:        MusicDB
#  Author:      Kahsolt
#  Time:        2017/3/6
#  Desciption:  Static DB that hold all music tag info

# Configurations
MUSIC_DIR = r'./music/'
MUSIC_EXT = r'.mp3'
MUSIC_VOC=['流行摇滚', '乡村民谣', '爵士蓝调', '金属朋克', '轻音乐', '古典', '国风', '电子', '说唱',
           '清晨','下午茶','夜晚','学习工作','运动旅行','婚礼庆典','影视','ACG',
           '清新明媚','兴奋动感','治愈感动','怀旧伤感','安静放松','快乐','浪漫','孤独','思念',
           '弦乐组','管乐组','室内乐','钢琴','电吉他','口琴','古筝','二胡','琵琶','箫笛']

DB_LOCAL_FILE = r'MusicDB.db'
DB_MYSQL_HOST = r'kahsolt.tk'
DB_MYSQL_USER = r'root'
DB_MYSQL_PASSWD = r'YLQ-kahsolt'
DB_MYSQL_SCHEMA = r'audiv'
DB_MYSQL_CHARSET = r'utf8'

# Consts
MODE_ONLINE = 'Online'
MODE_OFFLINE = 'Offline'

# Imports
try:
	import MySQLdb
except:
    print('MusicDB: MySQLdb lib is missing, Local Mode availble only.')

# Classes
class DBMySQL:
    def __init__(self):
        try:
            self.mysql = MySQLdb.connect(host=DB_MYSQL_HOST,
                                         user=DB_MYSQL_USER,
                                         passwd=DB_MYSQL_PASSWD,
                                         db=DB_MYSQL_SCHEMA,
                                         charset=DB_MYSQL_CHARSET)
        except:
            print('DBMySQL: open connection error')

    def execsql(self,query):
        try:
            cursor = self.mysql.cursor()
            cursor.execute(query)
            data = cursor.fetchall()
            cursor.close()
            return map(list, data)  # tuple => list
        except:
            print('DBMySQL: open cursor error')

    def getMusic(self):
        query = 'SELECT title, style, scene, emotion, instrument FROM music;'
        return self.execsql(query)

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
                        song['tags'] = fdb.readline().strip('\n').split(',')
                        fdb.readline()    # skip the seperator line
                        self.dictMusic.append(song)
        except:
            print('DBText: no local db, online update() needed')

    def write(self, mysqlTable):     # File Over Write!!
        try:
            with open(DB_LOCAL_FILE, 'w+') as fdb:
                for song in mysqlTable:
                    fdb.write(song[0])
                    fdb.write('\n')
                    for idx in range(1,5):  # merge all tags
                        if song[idx]!='':
                            fdb.write(song[idx])
                        if idx != 4:
                            fdb.write(',')
                    fdb.write('\n')
                    fdb.write('\n')  # separator line
        except:
            print('DBText: write file error')

    def __checkTags(self, tags):
        ntags = []
        for t in tags:
            if t in MUSIC_VOC:
                ntags.append(t)
            else:
                print('MusicDB: tag \'' + t + '\' is invalid, omitted')
        return ntags

class MusicDB:
    def __init__(self, mode = MODE_OFFLINE):
        self.mode = mode
        if self.mode == MODE_ONLINE:
            self.dbMySQL = DBMySQL()
        else:
            print('MusicDB: working in local mode')
        self.dbText = DBText()

    def update(self):
        if self.mode == MODE_OFFLINE:
            print('MusicDB: working in local mode, operation failed')
            return
        try:
            self.dbText.write(self.dbMySQL.getMusic())
        except:
            print('MusicDB: update failed')

    def list(self):
        print(self.dbText)

# Main Entrance
def main():
    # 0.Import the main class in this file
    #
    # from MusicDB import MusicDB

    # 1.Create a MusicDB object
    #   use it just like apt/aptitude
    #
    musicDB = MusicDB()

    # 2.Update local textDB from the remote mysqlDB (if needed)
    #   local textDB is auto created if not exist or over written
    #
    # musicDB.update()

    # 3.Show all music in DB for a check (this should be very long...)
    #
    # musicDB.list()

    # 4.Search for music using the given tag list
    #   invalid tags will rise a warning and be omitted
    #
    #   \return     a list of music names with base path (max item number = MUSIC_MAX)
    #
    tags = ['安静放松', '下午茶']
    res = musicDB.match(tags)       # exactly matches all tags
    print(res)
    tags = ['清晨', '学习工作', '安静放松', '下午茶']
    res = musicDB.search(tags)      # relatively mathes some tags well (a bit slower)
    print(res)

if __name__ == '__main__':
    main()
