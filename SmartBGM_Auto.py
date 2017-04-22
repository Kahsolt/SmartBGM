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

from MusicDB import MUSIC_AUX_SCENE
from Slicer import Slicer
#from Analyzer import Analyzer
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

# Functions
def QString2String(qStr):
    return unicode(qStr.toUtf8(), 'utf-8', 'ignore')
def _String2Utf8(s):
    return s.encode('utf8')
def _Utf82String(s):
    return s.decode('utf8')

# 使得VideoWidget拥有QWidget的方法，主要是右键菜单
class myVideoWidget(phonon.Phonon.VideoWidget,QWidget):
    def __init__(self, parent):
        super(myVideoWidget,self).__init__()

class Progess(QDialog):
    def __init__(self, parent=None):
        super(Progess, self).__init__()
        self.setWindowTitle(self.tr("进度"))
        self.progressBar = QProgressBar()

        layout = QGridLayout()
        layout.addWidget(self.progressBar, 2, 2, 2, 2)
        # layout.addWidget(startPushButton,3,1)
        layout.setMargin(15)
        layout.setSpacing(0)
        self.setLayout(layout)

    def slotStart(self):
        num = 1000
        progressDialog = QProgressDialog(self)
        progressDialog.setWindowModality(Qt.WindowModal)
        progressDialog.setMinimumDuration(5)
        progressDialog.setWindowTitle(self.tr("请等待"))
        progressDialog.setLabelText(self.tr("拷贝..."))
        progressDialog.setCancelButtonText(self.tr("取消"))
        progressDialog.setRange(0, num)

        for i in range(num):
            progressDialog.setValue(i)
            QThread.msleep(100)
            if progressDialog.wasCanceled():
                return

class SmartBGM_Auto(QWidget):
    def __init__(self):
        super(SmartBGM_Auto, self).__init__()  # 初始化类，待补充

        # 绘制UI界面
        self.setWindowTitle(r'SmartBGM_Auto')
        self.setWindowIcon(QIcon(r'./icon/SmartBGM.ico'))
        self.UI = UI_SmartBGM_Auto()
        self.UI.setupUi(self)

        # 绑定UI Widgets事件
        self.connect(self.UI.videoPlayer, SIGNAL('customContextMenuRequested (const QPoint&)'), self.menu_open)
        self.connect(self.UI.btn_autoMatch, SIGNAL('clicked()'), self.btn_autoMatch_click)

        # 子控件
        self.wating_wdn = Progess()

        # 媒体文件路径: str-utf8
        self.videofile = None
        self.videofileLength = None
        # 媒体当前播放至的时间: QTime
        self.videoTime = None

    # 上下文右键菜单
    def menu_open(self):
        popMenu = QMenu()
        popMenu.addAction(QAction(QIcon(r'./icon/video.ico'), u'打开视频文件', self, enabled=True, triggered=self.menu_open_videoFile))
        popMenu.exec_(QCursor.pos())
    def menu_open_videoFile(self):
        file = self.menu_open_openFileDialog('video')
        if not file:
            return

        self.videofile = file
        self.videofileLength = 'TODO: how to get videofileLength!!';
        # 视频输出
        self.UI.mediaObjectVideo.setCurrentSource(phonon.Phonon.MediaSource(file))  # 加载当前的源文件
        phonon.Phonon.createPath(self.UI.mediaObjectVideo, self.UI.videoPlayer)  # 将视频对象和播放控件关联起来
        self.UI.videoPlayer.setAspectRatio(phonon.Phonon.VideoWidget.AspectRatioAuto)
        # 视频声道输出
        self.audioOutput_video = phonon.Phonon.AudioOutput(phonon.Phonon.VideoCategory, self)
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

    # 一键配乐
    def btn_autoMatch_click(self):
        slicer = Slicer(self.videofile)
        slicer.fps_rate(1)
        path_to_frame_slices_dir = slicer.slice()
        print '[slice:1] Sliced frames in ' + path_to_frame_slices_dir

        analyzer = Analyzer(path_to_frame_slices_dir)
        video_tags = []
        raw_tags = analyzer.analyze()
        for tag in raw_tags:
            video_tags.append(_Utf82String(tag[0]))
        if self.UI.cmb_scene.currentText() != '':
            video_tags.append(self.UI.cmb_scene.currentText())
        print '[analyze:2] Tags are ' + ','.join(video_tags)

        matcher = Matcher(video_tags)
        songs = matcher.match()
        print '[match:3] ' + str(len(songs)) + ' songs available'

        remixer = Remixer(self.videofile)
        ptrVideo = 0
        for song in songs:
            if ptrVideo < self.videofileLength:
                restTimespan = self.videofileLength - ptrVideo
                usedTime = (song[1] >= restTimespan) and restTimespan or song[1]
                remixer.mix(song[0], (ptrVideo, song[1]), (0, song[1]))
                ptrVideo += usedTime
                print '[merge:4] Mix task ["%s": (%d, %d)] executes!'% (song[0], ptrVideo, usedTime)
            else:
                break
        remixer.remix()
        print '[remix:5] SmartBGM auto mode done!'

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
    # 时间绑定
    def timeLcd_video_tick(self, time):
        # 以ms为单位
        self.videoTime = QTime((time / 3600000), (time / 60000) % 60, (time / 1000) % 60)
        self.UI.timeLcd_video.display(self.videoTime.toString('hh:mm:ss'))

    # 键盘事件 @Override
    def keyPressEvent(self, keyEvent):
        if keyEvent.key() == Qt.Key_Escape:
            self.close()

class UI_SmartBGM_Auto(object):
    def setupUi(self, parent):
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
        self.cmb_scene = QComboBox(self.layoutWidget)
        self.cmb_scene.setObjectName(_fromUtf8("cmb_scene"))
        self.horizontalLayout.addWidget(self.cmb_scene)
        spacerItem2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.chk_ost = QCheckBox(self.layoutWidget)
        self.chk_ost.setLayoutDirection(Qt.RightToLeft)
        self.chk_ost.setObjectName(_fromUtf8("chk_ost"))
        self.horizontalLayout.addWidget(self.chk_ost)
        spacerItem3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.horizontalLayout.setStretch(0, 10)
        self.horizontalLayout.setStretch(1, 2)
        self.horizontalLayout.setStretch(2, 10)
        self.horizontalLayout.setStretch(3, 5)
        self.horizontalLayout.setStretch(4, 1)
        self.horizontalLayout.setStretch(5, 2)
        self.horizontalLayout.setStretch(6, 1)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        spacerItem4 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem4)
        self.verticalLayout_3.setStretch(0, 50)
        self.verticalLayout_3.setStretch(1, 2)
        self.verticalLayout_3.setStretch(2, 2)
        self.verticalLayout_3.setStretch(3, 1)

        self.retranslateUi(parent)
        QMetaObject.connectSlotsByName(parent)

        self.mediaObjectVideo = phonon.Phonon.MediaObject(parent)  # 声明视频对象
        self.mediaObjectVideo.stateChanged.connect(parent.stateChanged_video)  # 对象改变时，应该是注册事件，响应按钮
        self.mediaObjectVideo.tick.connect(parent.timeLcd_video_tick)  # 连接到时间
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
        self.horizontalLayout_control_video.addWidget(videobar)

        #  显示视频LED时间
        palette_videolcd = QPalette()  # 声明调色板
        palette_videolcd.setBrush(QPalette.Light, Qt.darkGray)  # 设置刷子颜色
        self.timeLcd_video = self.lcdNumber_video  # 将lcd数字灯赋给新的对象名
        self.timeLcd_video.setPalette(palette_videolcd)  # 设置配色方案
        self.timeLcd_video.display('00:00:00')  # 设置显示格式

        #  添加播放控件
        self.videoPlayer = myVideoWidget(self)  # 声明VideoWidget控件
        self.horizontalLayout_videoplayer.addWidget(self.videoPlayer)  # 将videoPlayer加入到预留的布局里面
        # 设置播放控件能右键产生菜单的属性
        self.videoPlayer.setContextMenuPolicy(Qt.CustomContextMenu)

        # cmb_scene 初始化
        for scene in MUSIC_AUX_SCENE:
            self.cmb_scene.addItem(scene.decode('utf8'))

    def retranslateUi(self, parent):
        parent.resize(912, 633)
        parent.setObjectName(_fromUtf8("Form"))
        parent.setWindowFlags(Qt.WindowMinimizeButtonHint)  # 停用窗口最大化按钮
        parent.setFixedSize(parent.width(), parent.height())  # 禁止改变窗口的大小

        self.btn_autoMatch.setText(_translate("Form", "一键配乐", None))
        self.chk_ost.setText(_translate("Form", "原声", None))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    smartBGM_Auto = SmartBGM_Auto()
    smartBGM_Auto.show()
    sys.exit(app.exec_())
