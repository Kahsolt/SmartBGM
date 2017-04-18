#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#==========================
#  Name:        SmartBGM_Auto
#  Author:      llk2why; and kahsolt fucked it up
#  Time:        2017/04/17
#  Desciption:  SmartBGM auto mode main editor

import sys, os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import phonon

from Slicer import Slicer
from Analyzer import Analyzer
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

class SmartBGM_Auto(QWidget):
    # 构造函数
    def __init__(self):
        super(SmartBGM_Auto, self).__init__()

        # 绘制UI界面
        self.setWindowTitle(u'SmartBGM_Auto')
        self.setWindowIcon(QIcon(r'./icon/SmartBGM.ico'))
        self.UI = UI_SmartBGM_Auto()
        self.UI.setupUi(self)

        # 绑定UI Widgets事件
        self.connect(self.UI.videoPlayer, SIGNAL('customContextMenuRequested (const QPoint&)'), self.menu_open)
        self.connect(self.UI.btn_merge, SIGNAL('clicked()'), self.btn_merge_click)
        self.connect(self.UI.btn_save, SIGNAL('clicked()'), self.btn_save_click)

        # 媒体文件路径: str-utf8
        self.videofile=None

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

        self.videofile=file
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
        currentPath = QDesktopServices.storageLocation(QDesktopServices.DesktopLocation)
        file = QFileDialog.getOpenFileName(self, tips, currentPath, extension)
        file = QString2String(file)
        print '[openFileDialog] File Selected: ' + (file or '<None>')
        return file

    # 键盘事件 @Override
    def keyPressEvent(self, keyEvent):
        if keyEvent.key() == Qt.Key_Escape:
            self.close()

class UI_SmartBGM_Auto(object):
    def setupUi(self, parent):
        parent.setObjectName(_fromUtf8("UI_SmartBGM_Auto"))
        parent.resize(912, 633)
        self.layoutWidget = QWidget(parent)
        self.layoutWidget.setGeometry(QRect(0, 0, 911, 631))
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
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.btn_autoMatch = QPushButton(self.layoutWidget)
        self.btn_autoMatch.setObjectName(_fromUtf8("btn_autoMatch"))
        self.horizontalLayout.addWidget(self.btn_autoMatch)
        spacerItem1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        spacerItem2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem2)
        self.verticalLayout_3.setStretch(0, 50)
        self.verticalLayout_3.setStretch(1, 2)
        self.verticalLayout_3.setStretch(2, 2)
        self.verticalLayout_3.setStretch(3, 1)

        self.retranslateUi(parent)
        QMetaObject.connectSlotsByName(parent)

    def retranslateUi(self, parent):
        parent.setWindowTitle(_translate("Form", "Form", None))
        self.btn_autoMatch.setText(_translate("Form", "一键配乐", None))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    smartBGM_Auto = SmartBGM_Auto()
    smartBGM_Auto.show()
    sys.exit(app.exec_())
