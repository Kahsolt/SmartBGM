#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#==========================
#  Name:        SmartBGM
#  Author:      llk2why; and kahsolt fucked it up
#  Time:        2017/04/16
#  Desciption:  SmartBGM manual mode main editor

import sys, os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import phonon

from TagSelector import TagSelector
from Matcher import Matcher
from Remixer import Remixer

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s
try:
    _encoding = QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig)

def QString2String(qStr):
    return unicode(qStr.toUtf8(), 'utf-8', 'ignore')

# 使得VideoWidget拥有QWidget的方法，主要是右键菜单
class myVideoWidget(phonon.Phonon.VideoWidget,QWidget):
    def __init__(self, parent):
        super(myVideoWidget,self).__init__()

class SmartBGM(QWidget):
    def __init__(self):
        super(SmartBGM, self).__init__()

        # 绘制UI界面
        self.setWindowTitle(r'SmartBGM')
        self.setWindowIcon(QIcon(r'./icon/SmartBGM.ico'))
        self.UI = UI_SmartBGM()
        self.UI.setupUi(self)

        # 绑定UI Widgets事件
        self.connect(self.UI.videoPlayer, SIGNAL('customContextMenuRequested (const QPoint&)'), self.menu_open)
        self.connect(self.UI.btn_video_cutin, SIGNAL('clicked()'), self.btn_videoCutIn_click)
        self.connect(self.UI.btn_video_cutout, SIGNAL('clicked()'), self.btn_videoCutOut_click)
        self.connect(self.UI.btn_audio_cutin, SIGNAL('clicked()'), self.btn_audioCutIn_click)
        self.UI.cmb_music.activated.connect(self.cmb_music_click)
        # self.connect(self.UI.cmb_music, SIGNAL('activated()'), self.cmb_music_click)
        self.connect(self.UI.btn_tagsDialog, SIGNAL('clicked()'), self.btn_tagsDialog_click)
        self.connect(self.UI.btn_playTogether, SIGNAL('clicked()'), self.btn_playTogether_click)
        self.connect(self.UI.btn_merge, SIGNAL('clicked()'), self.btn_merge_click)
        self.connect(self.UI.btn_save, SIGNAL('clicked()'), self.btn_save_click)

        # 子控件
        self.tagSelector = TagSelector(self)
        # 音频列表
        self.audiolist = {} # {'title':('path', 300)}
        self.todoList = []

        # 媒体文件路径: str-utf8
        self.videofile = None
        self.videofileLength = None
        self.audiofile = None
        self.audiofileLength = None
        # 媒体当前播放至的时间: QTime
        self.videoTime = None
        self.audioTime = None
        # 媒体合并的三个关键参数: QTime
        self.cutinTime_video = None
        self.cutoutTime_video = None
        self.cutinTime_audio = None

    # 上下文右键菜单
    def menu_open(self):
        popMenu = QMenu()
        popMenu.addAction(QAction(QIcon(r'./icon/video.ico'), u'打开视频文件', self, enabled = True, triggered=self.menu_open_videoFile))
        popMenu.addAction(QAction(QIcon(r'./icon/audio.ico'), u'打开音频文件', self, enabled = True, triggered=self.menu_open_audioFile))
        popMenu.exec_(QCursor.pos())
    def menu_open_videoFile(self):
        file = self.menu_open_openFileDialog('video')
        if not file:
            return

        self.videofile = file
        self.videofileLength = None
        # 视频输出
        self.UI.mediaObjectVideo.setCurrentSource(phonon.Phonon.MediaSource(file))  #加载当前的源文件
        phonon.Phonon.createPath(self.UI.mediaObjectVideo, self.UI.videoPlayer)     #将视频对象和播放控件关联起来
        self.UI.videoPlayer.setAspectRatio(phonon.Phonon.VideoWidget.AspectRatioAuto)
        # 视频声道输出
        self.audioOutput_video = phonon.Phonon.AudioOutput(phonon.Phonon.VideoCategory,self)
        phonon.Phonon.createPath(self.UI.mediaObjectVideo, self.audioOutput_video)
        self.UI.volumeSlider.setAudioOutput(self.audioOutput_video)
        self.UI.seekSlider_video.setMediaObject(self.UI.mediaObjectVideo)
        self.UI.mediaObjectVideo.play()
    def menu_open_audioFile(self):
        file = self.menu_open_openFileDialog('audio')
        if not file:
            return

        fname = os.path.splitext(os.path.split(file)[1])[0]
        self.audiofile = file
        self.audiofileLength = None
        self.audiolist[fname] = (file, -1)
        self.UI.cmb_music.clear()
        self.UI.cmb_music.addItem(fname)

        # 音频输出
        self.UI.mediaObjectAudio.setCurrentSource(phonon.Phonon.MediaSource(file))
        self.audioOutput_audio = phonon.Phonon.AudioOutput(phonon.Phonon.VideoCategory,self)
        phonon.Phonon.createPath(self.UI.mediaObjectAudio, self.audioOutput_audio)
        #self.UI.volumeSlider.setAudioOutput(self.audioOutput_audio)
        self.UI.seekSlider_audio.setMediaObject(self.UI.mediaObjectAudio)
        self.UI.mediaObjectAudio.play()
    def menu_open_openFileDialog(self, filetype = 'all'):
        if filetype=='audio':
            tips = u'选择音频文件'
            extension = 'Audio Files(*.mp3 *.wav)'
        elif filetype=='video':
            tips = u'选择视频文件'
            extension = 'Video Files(*.mp4 *.avi *.mkv *.rmvb *.flv)'
        else:
            tips = u'请选择文件'
            extension = 'Files(*)'
        # currentPath = QDesktopServices.storageLocation(QDesktopServices.DesktopLocation)
        currentPath = './test'
        file = QFileDialog.getOpenFileName(self, tips, currentPath, extension)
        file = QString2String(file)
        print '[openFileDialog] File Selected: ' + (file or '<None>')
        return file

    # 视频嵌入开始点
    def btn_videoCutIn_click(self):
        if self.videoTime == None:
            self.err(5)
            return
        self.UI.lbl_cutin.setText(_translate("Form", self.videoTime.toString('hh:mm:ss'), None))
        self.cutinTime_video = self.videoTime
        print '[videoCutIn] Video cut in Time: ' + self.cutinTime_video.toString()
    # 视频嵌入结束点
    def btn_videoCutOut_click(self):
        if self.videoTime == None:
            self.err(1)
            return
        elif self.cutinTime_video == None:
            self.err(2)
            return
        elif self.cutinTime_video > self.videoTime:
            self.err(3)
            return
        #以下声明代码用于简化之后的代码表示
        Ta = self.cutinTime_video   #视频切入点的时间
        Tb = self.videoTime         #当前视频的时间
        Sta = Ta.hour()*3600+Ta.minute()*60+Ta.second()
        Stb = Tb.hour()*3600+Tb.minute()*60+Tb.second() - 10  # QEST: -10?
        # print Ta.hour(), Ta.minute(), Ta.second(), Tb.hour(), Tb.minute(), Tb.second() # 输出时间
        # if Sta > Stb:
        #    self.err(4)
        #    return
        self.UI.lbl_cutout.setText(_translate("Form", self.videoTime.toString('hh:mm:ss'), None))
        self.cutoutTime_video = self.videoTime
        print '[videoCutOut] Video cut out Time: ' + self.cutoutTime_video.toString()
    # 音频嵌入开始点
    def btn_audioCutIn_click(self):
        if self.audioTime == None:
            self.err(5)
            return
        self.UI.lbl_audio_start.setText(_translate("Form", self.audioTime.toString('mm:ss'), None))
        self.cutinTime_audio = self.audioTime
        print '[audioCutIn] audio cut out Time: ' + self.cutinTime_audio.toString()

    # 配乐类型选择按钮
    def btn_tagsDialog_click(self):
        self.tagSelector.exec_()    # Block main form thread
        tags = self.tagSelector.tagsSelected
        print '[tagsDialog] Tags received: ' + (len(tags) > 0 and ','.join(tags) or '<None>')

        matcher = Matcher(tags)
        songs = matcher.search()   # want less, to use match
        self.UI.cmb_music.clear()
        self.audiolist.clear()
        for song in songs:
            title = os.path.splitext(os.path.split(song[0])[1])[0]
            self.audiolist[title] = song
            self.UI.cmb_music.addItem(title)

    # 一起播放按钮
    def btn_playTogether_click(self):
        if self.videofile == None:
            self.err(1)
            return
        if self.audiofile == None:
            self.err(5)
            return

        self.UI.mediaObjectAudio.play()
        self.stateChanged_video(phonon.Phonon.PlayingState)
        self.UI.mediaObjectVideo.play()
        self.stateChanged_audio(phonon.Phonon.PlayingState)
        print '[playTogether] Play Together!'
    # 合并按钮
    def btn_merge_click(self):
        if self.videofile == None or \
                        self.cutinTime_video == None or \
                        self.cutoutTime_video == None or \
                        self.audiofile == None or \
                        self.cutinTime_audio == None:
            self.err(6)
            return

        cutinTime_video = self.cutinTime_video.hour()*3600+self.cutinTime_video.minute()*60+self.cutinTime_video.second()
        cutoutTime_video = self.cutoutTime_video.hour()*3600+self.cutoutTime_video.minute()*60+self.cutoutTime_video.second()
        cutinTime_audio = self.cutinTime_audio.minute()*60+self.cutinTime_audio.second()
        timespan_video = (cutinTime_video, cutoutTime_video - cutinTime_video)
        timeEnd_audio = self.audiofileLength or (cutoutTime_video - cutinTime_video)
        timespan_audio = (cutinTime_audio, timeEnd_audio)    # BUG: may here go wrong!!
        audiofile = self.audiofile
        self.todoList.append((audiofile, timespan_video, timespan_audio))
        print ('[merge] Merge task [' + str(cutinTime_video) + ', ' + str(cutoutTime_video) + ': "' + str(audiofile) + '", ' + str(cutinTime_audio) + ', ' + str(timeEnd_audio) +'] added!')
    # 保存按钮
    def btn_save_click(self):
        if self.todoList == []:
            self.err(7)
            return
        remixer = Remixer(self.videofile)
        for todo in self.todoList:
            remixer.mix(todo[0], todo[1], todo[2])
        remixer.remix()
        self.todoList = []
        print '[save] SmartBGM manual mode done!'

    # 音乐切换下拉框
    def cmb_music_click(self):
        curMusic = QString2String(self.UI.cmb_music.currentText())
        file = self.audiolist[curMusic][0]
        print '[music_click] Current Music: ' + file

        self.audiofile = file
        self.audiofileLength = self.audiolist[curMusic][1]
        # 音频输出
        self.UI.mediaObjectAudio.setCurrentSource(phonon.Phonon.MediaSource(file))
        self.audioOutput_audio = phonon.Phonon.AudioOutput(phonon.Phonon.VideoCategory, self)
        phonon.Phonon.createPath(self.UI.mediaObjectAudio, self.audioOutput_audio)
        # self.UI.volumeSlider.setAudioOutput(self.audioOutput_audio)
        self.UI.seekSlider_audio.setMediaObject(self.UI.mediaObjectAudio)
        self.UI.mediaObjectAudio.play()
    # 多媒体状态改变事件处理
    def stateChanged_video(self, newState):
        if newState == phonon.Phonon.ErrorState:
            if self.UI.mediaObjectVideo.errorType() == phonon.Phonon.FatalError:
                QMessageBox.warning(self, "Fatal Error", self.UI.mediaObjectVideo.errorString())
            else:
                QMessageBox.warning(self, "Error", self.UI.mediaObjectVideo.errorString())
        elif newState == phonon.Phonon.PlayingState:
            self.UI.playActionVideo.setEnabled(False)
            self.UI.pauseActionVideo.setEnabled(True)
            self.UI.stopActionVideo.setEnabled(True)
        elif newState == phonon.Phonon.StoppedState:
            self.UI.stopActionVideo.setEnabled(False)
            self.UI.playActionVideo.setEnabled(True)
            self.UI.pauseActionVideo.setEnabled(False)
            self.UI.timeLcd_video.display("00:00:00")
        elif newState == phonon.Phonon.PausedState:
            self.UI.stopActionVideo.setEnabled(True)
            self.UI.playActionVideo.setEnabled(True)
            self.UI.pauseActionVideo.setEnabled(False)
    def stateChanged_audio(self, newState):
        if newState == phonon.Phonon.ErrorState:
            if self.UI.mediaObjectVideo.errorType() == phonon.Phonon.FatalError:
                QMessageBox.warning(self, "Fatal Error", self.UI.mediaObjectVideo.errorString())
            else:
                QMessageBox.warning(self, "Error", self.UI.mediaObjectVideo.errorString())
        elif newState == phonon.Phonon.PlayingState:
            self.UI.playActionAudio.setEnabled(False)
            self.UI.pauseActionAudio.setEnabled(True)
            self.UI.stopActionAudio.setEnabled(True)
        elif newState == phonon.Phonon.StoppedState:
            self.UI.stopActionAudio.setEnabled(False)
            self.UI.playActionAudio.setEnabled(True)
            self.UI.pauseActionAudio.setEnabled(False)
            self.UI.timeLcd_audio.display("00:00")
        elif newState == phonon.Phonon.PausedState:
            self.UI.stopActionAudio.setEnabled(False)
            self.UI.playActionAudio.setEnabled(True)
            self.UI.pauseActionAudio.setEnabled(False)
    # 时间绑定
    def timeLcd_video_tick(self, time):
        # 以ms为单位
        self.videoTime = QTime((time / 3600000), (time / 60000) % 60, (time / 1000) % 60)
        self.UI.timeLcd_video.display(self.videoTime.toString('hh:mm:ss'))
    def timeLcd_audio_tick(self, time):
        # 以ms为单位
        self.audioTime = QTime((time / 3600000), (time / 60000) % 60, (time / 1000) % 60)
        self.UI.timeLcd_audio.display(self.audioTime.toString('mm:ss'))

    # 错误警告
    def err(self, errCode):
        dictError={
            1 : u'请先读取视频！',
            2 : u'请先指定音频插入的视频段的起始时间！',
            3 : u'当前时间小于指定的视频段起始时间，请重新指定！',
            4 : u'视频段的时间间距太小，请重新指定！',
            5 : u'请先指定需要的配乐类型！',
            6 : u'请指定音视频文件和对应的时间！',
            7 : u'请先添加音轨合并的任务！'
        }
        QMessageBox.question(self, (u'提示'), dictError[errCode], QMessageBox.Ok)
    # 键盘事件 @Override
    def keyPressEvent(self, keyEvent):
        if keyEvent.key() == Qt.Key_Escape:
            self.close()

class UI_SmartBGM(object):
    def setupUi(self, parent):
        self.line_3 = QFrame(parent)
        self.line_3.setGeometry(QRect(10, 580, 891, 16))
        self.line_3.setFrameShape(QFrame.HLine)
        self.line_3.setFrameShadow(QFrame.Sunken)
        self.line_3.setObjectName(_fromUtf8("line_3"))
        self.layoutWidget = QWidget(parent)
        self.layoutWidget.setGeometry(QRect(0, 0, 911, 621))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.verticalLayout_3 = QVBoxLayout(self.layoutWidget)
        self.verticalLayout_3.setMargin(0)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.horizontalLayout_videoplayer = QHBoxLayout()
        self.horizontalLayout_videoplayer.setObjectName(_fromUtf8("horizontalLayout_videoplayer"))
        self.verticalLayout_3.addLayout(self.horizontalLayout_videoplayer)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.horizontalLayout_control_video = QHBoxLayout()
        self.horizontalLayout_control_video.setObjectName(_fromUtf8("horizontalLayout_control_video"))
        self.horizontalLayout_2.addLayout(self.horizontalLayout_control_video)
        self.line = QFrame(self.layoutWidget)
        self.line.setFrameShape(QFrame.VLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.horizontalLayout_2.addWidget(self.line)
        self.seekSlider_video = phonon.Phonon.SeekSlider(self.layoutWidget)
        self.seekSlider_video.setObjectName(_fromUtf8("seekSlider_video"))
        self.horizontalLayout_2.addWidget(self.seekSlider_video)
        self.lcdNumber_video = QLCDNumber(self.layoutWidget)
        self.lcdNumber_video.setNumDigits(8)
        self.lcdNumber_video.setObjectName(_fromUtf8("lcdNumber_video"))
        self.horizontalLayout_2.addWidget(self.lcdNumber_video)
        self.line_2 = QFrame(self.layoutWidget)
        self.line_2.setFrameShape(QFrame.VLine)
        self.line_2.setFrameShadow(QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.horizontalLayout_2.addWidget(self.line_2)
        self.volumeSlider = phonon.Phonon.VolumeSlider(self.layoutWidget)
        self.volumeSlider.setObjectName(_fromUtf8("volumeSlider"))
        self.horizontalLayout_2.addWidget(self.volumeSlider)
        self.horizontalLayout_2.setStretch(0, 10)
        self.horizontalLayout_2.setStretch(2, 40)
        self.horizontalLayout_2.setStretch(3, 5)
        self.horizontalLayout_2.setStretch(4, 20)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(_fromUtf8("horizontalLayout_7"))
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        spacerItem = QSpacerItem(18, 18, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        spacerItem1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.btn_video_cutin = QPushButton(self.layoutWidget)
        self.btn_video_cutin.setObjectName(_fromUtf8("btn_video_cutin"))
        self.horizontalLayout_3.addWidget(self.btn_video_cutin)
        spacerItem2 = QSpacerItem(18, 18, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.lbl_cutin = QLabel(self.layoutWidget)
        self.lbl_cutin.setObjectName(_fromUtf8("lbl_cutin"))
        self.horizontalLayout_3.addWidget(self.lbl_cutin)
        spacerItem3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem3)
        self.horizontalLayout_3.setStretch(0, 10)
        self.horizontalLayout_3.setStretch(1, 5)
        self.horizontalLayout_3.setStretch(2, 3)
        self.horizontalLayout_3.setStretch(3, 5)
        self.horizontalLayout_3.setStretch(4, 10)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        spacerItem4 = QSpacerItem(18, 18, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem4)
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        spacerItem5 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem5)
        self.btn_video_cutout = QPushButton(self.layoutWidget)
        self.btn_video_cutout.setObjectName(_fromUtf8("btn_video_cutout"))
        self.horizontalLayout_4.addWidget(self.btn_video_cutout)
        spacerItem6 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem6)
        self.lbl_cutout = QLabel(self.layoutWidget)
        self.lbl_cutout.setObjectName(_fromUtf8("lbl_cutout"))
        self.horizontalLayout_4.addWidget(self.lbl_cutout)
        spacerItem7 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem7)
        self.horizontalLayout_4.setStretch(0, 10)
        self.horizontalLayout_4.setStretch(1, 5)
        self.horizontalLayout_4.setStretch(2, 3)
        self.horizontalLayout_4.setStretch(3, 5)
        self.horizontalLayout_4.setStretch(4, 10)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        spacerItem8 = QSpacerItem(18, 18, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem8)
        self.horizontalLayout_7.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        spacerItem9 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem9)
        self.cmb_music = QComboBox(self.layoutWidget)
        self.cmb_music.setObjectName(_fromUtf8("cmb_music"))
        self.horizontalLayout_5.addWidget(self.cmb_music)
        spacerItem10 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem10)
        self.seekSlider_audio = phonon.Phonon.SeekSlider(self.layoutWidget)
        self.seekSlider_audio.setObjectName(_fromUtf8("seekSlider_audio"))
        self.horizontalLayout_5.addWidget(self.seekSlider_audio)
        spacerItem11 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem11)
        self.lcdNumber_audio = QLCDNumber(self.layoutWidget)
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lcdNumber_audio.sizePolicy().hasHeightForWidth())
        self.lcdNumber_audio.setSizePolicy(sizePolicy)
        self.lcdNumber_audio.setObjectName(_fromUtf8("lcdNumber_audio"))
        self.horizontalLayout_5.addWidget(self.lcdNumber_audio)
        spacerItem12 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem12)
        self.horizontalLayout_5.setStretch(0, 8)
        self.horizontalLayout_5.setStretch(1, 20)
        self.horizontalLayout_5.setStretch(2, 1)
        self.horizontalLayout_5.setStretch(4, 1)
        self.horizontalLayout_5.setStretch(5, 3)
        self.horizontalLayout_5.setStretch(6, 4)
        self.verticalLayout_2.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        spacerItem13 = QSpacerItem(13, 18, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem13)
        self.horizontalLayout_control_audio = QHBoxLayout()
        self.horizontalLayout_control_audio.setObjectName(_fromUtf8("horizontalLayout_control_audio"))
        self.horizontalLayout_6.addLayout(self.horizontalLayout_control_audio)
        spacerItem14 = QSpacerItem(13, 18, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem14)
        self.btn_audio_cutin = QPushButton(self.layoutWidget)
        self.btn_audio_cutin.setContextMenuPolicy(Qt.CustomContextMenu)
        self.btn_audio_cutin.setObjectName(_fromUtf8("btn_audio_cutin"))
        self.horizontalLayout_6.addWidget(self.btn_audio_cutin)
        spacerItem15 = QSpacerItem(13, 18, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem15)
        self.lbl_audio_start = QLabel(self.layoutWidget)
        self.lbl_audio_start.setObjectName(_fromUtf8("lbl_audio_start"))
        self.horizontalLayout_6.addWidget(self.lbl_audio_start)
        spacerItem16 = QSpacerItem(13, 18, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem16)
        self.horizontalLayout_6.setStretch(0, 6)
        self.horizontalLayout_6.setStretch(1, 12)
        self.horizontalLayout_6.setStretch(2, 2)
        self.horizontalLayout_6.setStretch(4, 1)
        self.horizontalLayout_6.setStretch(5, 3)
        self.horizontalLayout_6.setStretch(6, 8)
        self.verticalLayout_2.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_7.addLayout(self.verticalLayout_2)
        self.verticalLayout_3.addLayout(self.horizontalLayout_7)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem17 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem17)
        self.btn_tagsDialog = QPushButton(self.layoutWidget)
        self.btn_tagsDialog.setObjectName(_fromUtf8("btn_tagsDialog"))
        self.horizontalLayout.addWidget(self.btn_tagsDialog)
        spacerItem18 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem18)
        self.btn_playTogether = QPushButton(self.layoutWidget)
        self.btn_playTogether.setObjectName(_fromUtf8("btn_playTogether"))
        self.horizontalLayout.addWidget(self.btn_playTogether)
        spacerItem19 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem19)
        self.btn_merge = QPushButton(self.layoutWidget)
        self.btn_merge.setContextMenuPolicy(Qt.CustomContextMenu)
        self.btn_merge.setObjectName(_fromUtf8("btn_merge"))
        self.horizontalLayout.addWidget(self.btn_merge)
        spacerItem20 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem20)
        self.btn_save = QPushButton(self.layoutWidget)
        self.btn_save.setObjectName(_fromUtf8("btn_save"))
        self.horizontalLayout.addWidget(self.btn_save)
        spacerItem21 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem21)
        self.horizontalLayout.setStretch(0, 20)
        self.horizontalLayout.setStretch(1, 10)
        self.horizontalLayout.setStretch(2, 20)
        self.horizontalLayout.setStretch(3, 10)
        self.horizontalLayout.setStretch(4, 20)
        self.horizontalLayout.setStretch(5, 10)
        self.horizontalLayout.setStretch(6, 20)
        self.horizontalLayout.setStretch(7, 10)
        self.horizontalLayout.setStretch(8, 20)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.verticalLayout_3.setStretch(0, 50)
        self.verticalLayout_3.setStretch(1, 1)
        self.verticalLayout_3.setStretch(2, 10)
        self.verticalLayout_3.setStretch(3, 3)

        self.retranslateUi(parent)
        QMetaObject.connectSlotsByName(parent)

        self.mediaObjectVideo = phonon.Phonon.MediaObject(parent)  # 声明视频对象
        self.mediaObjectVideo.stateChanged.connect(parent.stateChanged_video)  # 对象改变时，应该是注册事件，响应按钮
        self.mediaObjectVideo.tick.connect(parent.timeLcd_video_tick)  # 连接到时间

        self.mediaObjectAudio = phonon.Phonon.MediaObject(parent)  # 声明音频对象
        self.mediaObjectAudio.stateChanged.connect(parent.stateChanged_audio)  # 对象改变时，应该是注册事件，响应按钮
        self.mediaObjectAudio.tick.connect(parent.timeLcd_audio_tick)  # 连接到时间

        # 声明视频控制端行为  包含：播放，暂停，重新开始
        self.playActionVideo = QAction(parent.style().standardIcon(QStyle.SP_MediaPlay), "Play",
                                       parent, shortcut="Ctrl+P", enabled=False, triggered=self.mediaObjectVideo.play)
        self.pauseActionVideo = QAction(parent.style().standardIcon(QStyle.SP_MediaPause), "Pause",
                                        parent, shortcut="Ctrl+A", enabled=False, triggered=self.mediaObjectVideo.pause)
        self.stopActionVideo = QAction(parent.style().standardIcon(QStyle.SP_MediaStop), "Stop",
                                       parent, shortcut="Ctrl+S", enabled=False, triggered=self.mediaObjectVideo.stop)
        # 添加视频控制端   包含 播放， 暂停， 重新开始
        videobar = QToolBar()
        videobar.addAction(self.playActionVideo)
        videobar.addAction(self.pauseActionVideo)
        videobar.addAction(self.stopActionVideo)
        # horizontalLayout_control_video是之前预留的布局，用于后续代码添加控件
        self.horizontalLayout_control_video.addWidget(videobar)

        # 声明音频控制端行为  包含：播放，暂停，重新开始
        self.playActionAudio = QAction(parent.style().standardIcon(QStyle.SP_MediaPlay), "Play", parent,
                                       shortcut="Ctrl+Alt+P", enabled=False, triggered=self.mediaObjectAudio.play)
        self.pauseActionAudio = QAction(parent.style().standardIcon(QStyle.SP_MediaPause), "Pause", parent,
                                        shortcut="Ctrl+Alt+A", enabled=False, triggered=self.mediaObjectAudio.pause)
        self.stopActionAudio = QAction(parent.style().standardIcon(QStyle.SP_MediaStop), "Stop", parent,
                                       shortcut="Ctrl+Alt+S", enabled=False, triggered=self.mediaObjectAudio.stop)
        # 添加音频控制端   包含 播放， 暂停， 重新开始
        audiobar = QToolBar()
        audiobar.addAction(self.playActionAudio)
        audiobar.addAction(self.pauseActionAudio)
        audiobar.addAction(self.stopActionAudio)
        # horizontalLayout_control_video是之前预留的布局，用于后续代码添加控件
        self.horizontalLayout_control_audio.addWidget(audiobar)

        #  显示视频LED时间
        palette_videolcd = QPalette()  # 声明调色板
        palette_videolcd.setBrush(QPalette.Light, Qt.darkGray)  # 设置刷子颜色
        self.timeLcd_video = self.lcdNumber_video  # 将lcd数字灯赋给新的对象名
        self.timeLcd_video.setPalette(palette_videolcd)  # 设置配色方案
        self.timeLcd_video.display('00:00:00')  # 设置显示格式
        #  显示音频LED时间
        palette_audiolcd = QPalette()  # 声明调色板
        palette_audiolcd.setBrush(QPalette.Light, Qt.darkBlue)  # 设置刷子颜色
        self.timeLcd_audio = self.lcdNumber_audio  # 将lcd数字灯赋给新的对象名
        self.timeLcd_audio.setPalette(palette_audiolcd)  # 设置配色方案
        self.timeLcd_audio.display('00:00')  # 设置显示格式

        #  添加播放控件
        self.videoPlayer = myVideoWidget(parent)  # 声明VideoWidget控件
        self.horizontalLayout_videoplayer.addWidget(self.videoPlayer)  # 将videoPlayer加入到预留的布局里面
        # 设置播放控件能右键产生菜单的属性
        self.videoPlayer.setContextMenuPolicy(Qt.CustomContextMenu)

    def retranslateUi(self, parent):
        parent.setObjectName(_fromUtf8("SmartBGM"))
        parent.resize(911, 627)
        parent.setWindowFlags(Qt.WindowMinimizeButtonHint)  # 停用窗口最大化按钮
        parent.setFixedSize(parent.width(), parent.height())  # 禁止改变窗口的大小

        self.btn_video_cutin.setText(_translate("btn_video_cutin", "视频切入点", None))
        self.lbl_cutin.setText(_translate("lbl_cutin", "00:00:00", None))
        self.btn_video_cutout.setText(_translate("btn_video_cutout", "视频切出点", None))
        self.lbl_cutout.setText(_translate("lbl_cutout", "00:00:00", None))
        self.btn_audio_cutin.setText(_translate("btn_audio_cutin", "音频切入点", None))
        self.lbl_audio_start.setText(_translate("lbl_audio_start", "00:00", None))
        self.btn_tagsDialog.setText(_translate("btn_tagsDialog", "配乐类型", None))
        self.btn_playTogether.setText(_translate("btn_playTogether", "同时播放", None))
        self.btn_merge.setText(_translate("btn_merge", "添加音轨", None))
        self.btn_save.setText(_translate("btn_save", "写入并保存", None))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    smartBGM = SmartBGM()
    smartBGM.show()
    sys.exit(app.exec_())
