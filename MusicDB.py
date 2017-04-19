#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#==========================
#  Name:        MusicDB
#  Author:      Kahsolt
#  Time:        2017/3/6
#  Desciption:  Translate MySQLDB to localDB

# Configuration
MUSIC_DIR = r'./music/'
MUSIC_VOC=[
    '流行摇滚', '乡村民谣', '爵士蓝调', '金属朋克', '轻音乐', '古典', '国风', '电子', '说唱',
    '清晨', '下午茶', '夜晚', '学习工作', '运动旅行', '婚礼庆典', '影视', 'ACG',
    '清新明媚', '兴奋动感', '治愈感动', '怀旧伤感', '安静放松', '快乐', '浪漫', '孤独', '思念',
    '弦乐组', '管乐组', '室内乐', '钢琴', '电吉他', '口琴', '古筝', '二胡', '琵琶', '箫笛'
]
MUSIC_AUX_SCENE=[
    '运动旅行', '婚礼庆典',
]
DB_LOCAL_FILE = r'MusicDB.db'
DB_MYSQL_HOST = r'kahsolt.cc'
DB_MYSQL_USER = r'root'
DB_MYSQL_PASSWD = r'YLQ-kahsolt'
DB_MYSQL_SCHEMA = r'audiv'
DB_MYSQL_CHARSET = r'utf8'

# Imports
import mysql.connector

# Functions
def _String2Utf8(s):
    return s.encode('utf8')
def _Utf82String(s):
    return s.decode('utf8')

# Classes
class DBMySQL:
    def __init__(self):
        try:
            self.mysql = mysql.connector.connect(host=DB_MYSQL_HOST,
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
            return data
        except:
            print('DBMySQL: open cursor error')

    def toDict(self, querySet):
        dictSong={}
        for song in querySet:
            listTag= ''
            for idx in range(1, 5):
                if song[idx] != set():
                    listTag += _String2Utf8(','.join(list(song[idx])))
                if idx != 4:
                    listTag += ','
            dictSong[_String2Utf8(song[0])] = listTag
        return dictSong

    def getMusic(self):
        query = 'SELECT title, style, scene, emotion, instrument FROM music;'
        res = self.toDict(self.execsql(query))
        return res

class DBText:
    def read(self):
        try:
            cntSong = 0
            print '-----[Start of MusicDB]-----'
            with open(DB_LOCAL_FILE, 'r') as fdb:
                for line in fdb.readlines():
                    cntSong += 1
                    print line,
            print '-----[End of MusicDB]-----'
            print ('DBText: ' + str(cntSong / 2) + ' songs in total')
        except:
            print('DBText: no local db, update() needed')

    def write(self, dictSong):     # File Over Write!!
        try:
            with open(DB_LOCAL_FILE, 'w+') as fdb:
                for (title, tags) in dictSong.items():
                    fdb.write(title)
                    fdb.write('\n')
                    fdb.write(tags)
                    fdb.write('\n')
        except:
            print('DBText: write file error')

class MusicDB():
    def __init__(self):
        self.dbMySQL = DBMySQL()
        self.dbText = DBText()

    def update(self):
        try:
            self.dbText.write(self.dbMySQL.getMusic())
        except:
            print('MusicDB: update() failed')

    def list(self):
        self.dbText.read()

# Main Entrance
def main():
    # 0.Import the main class in this file
    #
    # from MusicDB import MusicDB

    # 1.Create a MusicDB object
    #   use it just like apt
    #
    musicDB = MusicDB()

    # 2.Update local textDB from the remote mysqlDB
    #   local textDB is auto created if not exist or over written
    #
    musicDB.update()

    # 3.Show all music in DB for a check (this should be very long...)
    #
    musicDB.list()

if __name__ == '__main__':
    main()
