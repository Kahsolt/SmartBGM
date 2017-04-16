#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys, os, threading

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import phonon

from Dialog_Tags import Dialog_Tags

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

#多继承VideoWidget和QWidget
class myVideoWidget(phonon.Phonon.VideoWidget,QWidget):
    def __init__(self,x):
        super(myVideoWidget,self).__init__()
        #self.videoPlayer = phonon.Phonon.VideoWidget(x)  # 声明VideoWidget控件

class SmartBGM(QWidget):

    def __init__(self):
        super(SmartBGM, self).__init__()

        # 绘制UI界面
        self.setWindowTitle(u'SmartBGM')
        self.setWindowIcon(QIcon(r'./icon/SmartBGM.icon'))
        self.UI = UI_SmartBGM()
        self.UI.setupUi(self)

        #用以下两个量来标记是否已经打开了文件
        self.displayTime=None
        self.audioTime=None
        self.audiooutTime = None  #修改自章睿

        #初始化合并视频关键的三个参数
        self.cutinTime=None
        self.cutoutTime=None
        self.audio_stat_time=None
        
        #音频列表
        self.audiolist = {}

        #初始化文件路径
        self.videofile=None
        self.audiofile=None

        # 绑定播放控件的右键事件
        self.connect(self.UI.videoPlayer, SIGNAL('customContextMenuRequested (const QPoint&)'), self.openright)
        # 绑定视频切入切出的按钮
        self.connect(self.UI.btn_cutin,SIGNAL('clicked()'),self.audiocutin)
        self.connect(self.UI.btn_cutout, SIGNAL('clicked()'), self.audiocutout)
        # 绑定标签打开的按钮
        self.connect(self.UI.btn_tag,SIGNAL('clicked()'),self.tag_click)
        # 绑定加入用于确定音频开始点的按钮和对应的处理事件audio_start_clk
        self.connect(self.UI.btn_audio_start, SIGNAL('clicked()'), self.audio_start_clk)
        # 绑定音视频合并按钮和相应事件
        self.connect(self.UI.btn_merge,SIGNAL('clicked()'),self.video_merge)
        # 绑定combobox下拉选中条目的事件
        self.UI.comboBox.activated.connect(self.comboBoxItemClick)
        # 绑定同时播放按钮
        self.connect(self.UI.btn_play_together,SIGNAL('clicked()'),self.play_together_click)
        # 绑定合并音视频并保存按钮
        self.connect(self.UI.btn_save,SIGNAL('clicked()'),self.saveVideoAudio)

    # 合并音视频并保存按钮的响应事件
    def saveVideoAudio(self):
        Afile = self.audiofile.toUtf8()
        temp1 = os.path.split(Afile)
        Vfile = self.videofile.toUtf8()
        temp2 = os.path.split(Vfile)
        t1 = str(temp1[1])
        t2 = str(temp2[1])
        self.thread2 = combineThread(videoName=t2, audioName=t1, object=self.handler, finalname='resultFile.mp4')
        # self.connect(self.myThread, SIGNAL('setStatus'), self.st, Qt.QueuedConnection)
        self.thread2.start()
        # print('hello world')

    # 一起播放按钮
    def play_together_click(self):
        if self.videofile == None:
            self.alert(1)
            return
        if self.audiofile == None:
            self.alert(5)
            return

        self.mediaObjectAudio.play()
        self.playActionAudio.setEnabled(False)
        self.pauseActionAudio.setEnabled(True)
        self.stopActionAudio.setEnabled(True)

        self.mediaObjectVideo.play()
        self.playActionVideo.setEnabled(False)
        self.pauseActionVideo.setEnabled(True)
        self.stopActionVideo.setEnabled(True)

    #comboBox下拉点击响应函数
    def comboBoxItemClick(self):
        # print isinstance(self.UI.comboBox.currentText(), QString)
        tmp = unicode(self.UI.comboBox.currentText().toUtf8(), 'utf8', 'ignore')
        # tmp = self.UI.comboBox.currentText()
        # tmp = unicode(tmp, 'gb2312', 'ignore')
        print tmp
        tmp = str(tmp).encode('utf8')
        # tmp = tmp.decode('utf8')
        # print '>>>tmp\'type is:',type(tmp),' ',tmp
        # tmp = self.UI.comboBox.currentText().encoding('utf-8')
        # tmp = self.UI.comboBox.currentText().toUtf8()

        # file = self.audiolist[tmp.decode('utf8')].decode('utf8')
        # file = self.audiolist[Temp].encode('utf8')
        print tmp
        file = self.audiolist[tmp]
        # file = QString(os.path.abspath('.')+'\\Videos\\'+u'告别.mp3')
        file = QString(file)
        print unicode(file)
        self.audiofile = file       # still OK?

        self.mediaObjectAudio.setCurrentSource(phonon.Phonon.MediaSource(file))
        # 初始化音频的输出按钮
        self.audioOutput_audio = phonon.Phonon.AudioOutput(phonon.Phonon.VideoCategory, self)
        phonon.Phonon.createPath(self.mediaObjectAudio, self.audioOutput_audio)
        # 连接到音量
        # self.UI.volumeSlider.setAudioOutput(self.audioOutput_audio)
        # 连接到进度条
        self.UI.seekSlider_audio.setMediaObject(self.mediaObjectAudio)
        self.mediaObjectAudio.play()

    # 合并音视频按钮
    def video_merge(self):
        if self.videofile == None or \
                        self.cutinTime == None or \
                        self.cutoutTime == None or \
                        self.audiofile == None or \
                        self.audioTime == None:
            self.alert(6)
            return
        # 单独开一个线程，去执行操作
        temp1=self.audiofile  #BUG
        self.buildOperations()
        self.thread1 = myThread(audiofile=self.audiofile, audioTime=self.audioTime, cutinTime=self.cutinTime,
                                cutoutTime=self.cutoutTime, object=self.handler)
        # self.connect(self.myThread, SIGNAL('setStatus'), self.st, Qt.QueuedConnection)
        self.thread1.start()

        # thread1 = threading.Thread(target=self.threadF1())
        # thread1.setDaemon(True)
        # thread1.start()
        # self.handler=operations(audioName=self.audiofile, videoName=self.videofile)
        # self.handler.video_merge(cutinTime=self.cutinTime,cutoutTime=self.cutoutTime,\
        #                          audiofile=self.audiofile,audioTime=self.audioTime)

    def buildOperations(self):
        Afile = self.audiofile.toUtf8()
        temp1 = os.path.split(Afile)
        Vfile = self.videofile.toUtf8()
        temp2 = os.path.split(Vfile)
        t1 = str(temp1[1])
        t2 = str(temp2[1])
        self.handler = operations(audioName=t1, videoName=t2)

    # 加入的音乐起点按钮响应事件
    def audio_start_clk(self):
        if self.audioTime == None:
            self.alert(5)
            return

        self.UI.lbl_audio_start.setText(_translate("Form", self.audioTime.toString('mm:ss'), None))
        # print type(_translate("Form", self.audioTime.toString('mm:ss'),None))
        # print (_translate("Form", self.audioTime.toString('mm:ss'),None))
        self.audio_stat_time = self.audioTime

    # 配乐类型选择按钮
    def tag_click(self):
        dialog = Dialog_Tags(self)
        if dialog.exec_():
            pass
        dialog.destroy()

    # 音频嵌入的视频段开始点
    def audiocutin(self):
        if self.displayTime == None:
            self.alert(5)
            return
        # displayTime由mediaobject对象通过回调函数传入给lcdnumber，由此可将该数据赋给全局变量self.displaytime
        self.UI.lbl_cutin.setText(_translate("Form", self.displayTime.toString('hh:mm:ss'), None))
        self.cutinTime = self.displayTime
        #print self.cutinTime

    # 音频嵌入的视频段结束点
    def audiocutout(self):
        if self.displayTime == None:
            self.alert(1)
            return
        if self.cutinTime == None:
            self.alert(2)
            return
        if self.cutinTime > self.displayTime:
            self.alert(3)
            return

        #以下声明代码用于简化之后的代码表示
        Ta = self.cutinTime    #视频切入点的时间
        Tb = self.displayTime  #当前视频的时间
        Sta = Ta.hour()*3600+Ta.minute()*60+Ta.second()
        Stb = Tb.hour()*3600+Tb.minute()*60+Tb.second()-10

        #print Ta.hour() , Ta.minute() , Ta.second() , Tb.hour() , Tb.minute() , Tb.second() 输出时间

        if Sta > Stb:
            self.alert(4)
            return

        # displayTime由mediaobject对象通过回调函数传入给lcdnumber，由此可将该数据赋给全局变量self.displaytime
        self.UI.lbl_cutout.setText(_translate("Form", self.displayTime.toString('hh:mm:ss'), None))
        self.cutoutTime = self.displayTime
        #print self.cutoutTime

    # video screen 右键菜单
    def openright(self):
        popMenu = QMenu()#弹出菜单控件
        #添加弹出菜单项，自定义图标，并且绑定事件，分别为加载音频和加载视频
        popMenu.addAction(QAction(QIcon(r'./icon/video.ico'),u'打开视频文件',self,enabled = True, triggered=self.openvideo))
        popMenu.addAction(QAction(QIcon(r'./icon/audio.ico'),u'打开音频文件',self,enabled = True, triggered=self.openaudio))
        popMenu.exec_(QCursor.pos())

    # 响应combobox的改变
    def videoList_change(self):
        #file =
        self.mediaObjectAudio.setCurrentSource(phonon.Phonon.MediaSource(file))
        # 初始化音频的输出按钮
        self.audioOutput_audio = phonon.Phonon.AudioOutput(phonon.Phonon.VideoCategory, self)
        phonon.Phonon.createPath(self.mediaObjectAudio, self.audioOutput_audio)
        # 连接到音量
        # self.UI.volumeSlider.setAudioOutput(self.audioOutput_audio)
        # 连接到进度条
        self.UI.seekSlider_audio.setMediaObject(self.mediaObjectAudio)
        self.mediaObjectAudio.play()

    # 选择打开音频
    def openaudio(self):
        Qfile = self.addFiles('audio')
        if not Qfile:
            return

        self.audiolist.clear()# 当前的音频清单
        self.UI.comboBox.clear()

        self.audiofile=Qfile
        file = unicode(Qfile)

        fpath, fname = os.path.split(file)
        # print fpath,fname
        self.audiolist[fname] = file
        # print self.audiolist[fname]
        self.UI.comboBox.addItem(fname)

        self.mediaObjectAudio.setCurrentSource(phonon.Phonon.MediaSource(Qfile))
        #初始化音频的输出按钮
        self.audioOutput_audio = phonon.Phonon.AudioOutput(phonon.Phonon.VideoCategory,self)
        phonon.Phonon.createPath(self.mediaObjectAudio, self.audioOutput_audio)
        #连接到音量
        #self.UI.volumeSlider.setAudioOutput(self.audioOutput_audio)
        #连接到进度条
        self.UI.seekSlider_audio.setMediaObject(self.mediaObjectAudio)
        self.mediaObjectAudio.play()


    # 选择打开视频文件
    def openvideo(self):
        file = self.addFiles('video')
        if not file:
            return
        self.videofile=file
        self.mediaObjectVideo.setCurrentSource(phonon.Phonon.MediaSource(file))  #加载当前的源文件
        phonon.Phonon.createPath(self.mediaObjectVideo, self.UI.videoPlayer)     #将视频对象和播放控件关联起来
        #初始化视频输出
        self.UI.videoPlayer.setAspectRatio(phonon.Phonon.VideoWidget.AspectRatioAuto)
        #初始化音频的输出按钮
        self.audioOutput_video = phonon.Phonon.AudioOutput(phonon.Phonon.VideoCategory,self)
        phonon.Phonon.createPath(self.mediaObjectVideo, self.audioOutput_video)
        #连接到音量按钮
        self.UI.volumeSlider.setAudioOutput(self.audioOutput_video)
        self.UI.seekSlider_video.setMediaObject(self.mediaObjectVideo)
        self.mediaObjectVideo.play()

    # 错误警告信息
    def alert(self,err_num):
        if   err_num == 1:
            QMessageBox.question(self,(u'提示'),(u'请先读取视频！'),QMessageBox.Ok)
        elif err_num == 2:
            QMessageBox.question(self, (u'提示'), (u'请先指定音频插入的视频段的起始时间！'),
                                       QMessageBox.Ok)
        elif err_num == 3:
            QMessageBox.question(self, (u'提示'), (u'当前时间小于指定的视频段起始时间，请重新指定！'),
                                       QMessageBox.Ok)
        elif err_num == 4:
            QMessageBox.question(self, (u'提示'), (u'视频段的时间间距太小，请重新指定！'),
                                       QMessageBox.Ok)
        elif err_num == 5:
            QMessageBox.question(self, (u'提示'), (u'请先指定需要的配乐类型！'), QMessageBox.Ok)
        elif err_num == 6:
            QMessageBox.question(self, (u'提示'), (u'请指定音视频文件和对应的时间！'), QMessageBox.Ok)

    #选择文件
    def addFiles(self,filetype='all'):
        if filetype=='audio':
            tips=u'选择音频文件'
            expand = 'Audio Files(*.mp3 *.wav)'
        elif filetype=='video':
            tips = u'选择视频文件'
            expand = 'Video Files(*.mp4 *.avi *.mkv *.rmvb *.flv)'
        else:
            tips=u'请选择播放文件'
            expand = 'Files(*)'
        # getOpenFileName 只能选择一个  getOpenFileNames  可多个选择
        # files = QFileDialog.getOpenFileName(self, tips, QDesktopServices.storageLocation(
        #     QDesktopServices.DesktopLocation), expand)
        currentPath = os.getcwd()+r'\Videos'
        #currentPath = QDesktopServices.storageLocation(tGui.QDesktopServices.DesktopLocation)
        files = QFileDialog.getOpenFileName(self, tips,currentPath,expand)
        print type(files)

        if not files:
            return ''
        return files

    #视频状态改变事件处理
    def stateChanged(self,newState):

        if newState == phonon.Phonon.ErrorState:#如果出现错误状态，即刻报告
            if self.mediaObjectVideo.errorType() == phonon.Phonon.FatalError:
                QMessageBox.warning(self,"Fatal Error",
                        self.mediaObjectVideo.errorString())
            else:
                QMessageBox.warning(self,"Error",
                        self.mediaObjectVideo.errorString())

        elif newState == phonon.Phonon.PlayingState:#当按下播放按键时候，改变相应状态
            self.playActionVideo.setEnabled(False)
            self.pauseActionVideo.setEnabled(True)
            self.stopActionVideo.setEnabled(True)

        elif newState == phonon.Phonon.StoppedState:#当按下停止按键时候，改变相应状态
            self.stopActionVideo.setEnabled(False)
            self.playActionVideo.setEnabled(True)
            self.pauseActionVideo.setEnabled(False)
            self.timeLcd_video.display("00:00:00")

        elif newState == phonon.Phonon.PausedState:#当按下暂停案件时候，改变相应状态
            self.stopActionVideo.setEnabled(True)
            self.playActionVideo.setEnabled(True)
            self.pauseActionVideo.setEnabled(False)

    #音频状态改变事件处理
    def stateChanged_audio(self,newState):

        if newState == phonon.Phonon.ErrorState:#如果出现错误状态，即刻报告
            if self.mediaObjectVideo.errorType() == phonon.Phonon.FatalError:
                QMessageBox.warning(self,"Fatal Error",
                        self.mediaObjectVideo.errorString())
            else:
                QMessageBox.warning(self,"Error",
                        self.mediaObjectVideo.errorString())

        elif newState == phonon.Phonon.PlayingState:#当按下播放按键时候，改变相应状态
            self.playActionAudio.setEnabled(False)
            self.pauseActionAudio.setEnabled(True)
            self.stopActionAudio.setEnabled(True)

        elif newState == phonon.Phonon.StoppedState:#当按下停止按键时候，改变相应状态
            self.stopActionAudio.setEnabled(False)
            self.playActionAudio.setEnabled(True)
            self.pauseActionAudio.setEnabled(False)
            self.timeLcd_audio.display("00:00")

        elif newState == phonon.Phonon.PausedState:#当按下暂停案件时候，改变相应状态
            self.stopActionAudio.setEnabled(False)
            self.playActionAudio.setEnabled(True)
            self.pauseActionAudio.setEnabled(False)

    # 时间绑定
    def videotick(self,time):
        #相关函数的时间度量是以ms为单位
        self.displayTime = QTime((time /3600000),(time /60000)%60,(time / 1000)%60)
        self.timeLcd_video.display(self.displayTime.toString('hh:mm:ss'))

    # 时间绑定
    def audiotick(self,time):
        #相关函数的时间度量是以ms为单位
        self.audioTime = QTime((time /3600000),(time /60000)%60,(time / 1000)%60)
        self.timeLcd_audio.display(self.audioTime.toString('mm:ss'))

    #响应esc退出画面
    def keyPressEvent(self,event):
        if event.key() == Qt.Key_Escape:
            self.close()

class UI_SmartBGM(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("UI_SmartBGM"))
        Form.resize(911, 627)
        self.line_3 = QFrame(Form)
        self.line_3.setGeometry(QRect(10, 580, 891, 16))
        self.line_3.setFrameShape(QFrame.HLine)
        self.line_3.setFrameShadow(QFrame.Sunken)
        self.line_3.setObjectName(_fromUtf8("line_3"))
        self.layoutWidget = QWidget(Form)
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
        self.btn_cutin = QPushButton(self.layoutWidget)
        self.btn_cutin.setObjectName(_fromUtf8("btn_cutin"))
        self.horizontalLayout_3.addWidget(self.btn_cutin)
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
        self.btn_cutout = QPushButton(self.layoutWidget)
        self.btn_cutout.setObjectName(_fromUtf8("btn_cutout"))
        self.horizontalLayout_4.addWidget(self.btn_cutout)
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
        self.comboBox = QComboBox(self.layoutWidget)
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
        self.horizontalLayout_5.addWidget(self.comboBox)
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
        self.btn_audio_start = QPushButton(self.layoutWidget)
        self.btn_audio_start.setContextMenuPolicy(Qt.CustomContextMenu)
        self.btn_audio_start.setObjectName(_fromUtf8("btn_audio_start"))
        self.horizontalLayout_6.addWidget(self.btn_audio_start)
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
        self.btn_tag = QPushButton(self.layoutWidget)
        self.btn_tag.setObjectName(_fromUtf8("btn_tag"))
        self.horizontalLayout.addWidget(self.btn_tag)
        spacerItem18 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem18)
        self.btn_play_together = QPushButton(self.layoutWidget)
        self.btn_play_together.setObjectName(_fromUtf8("btn_play_together"))
        self.horizontalLayout.addWidget(self.btn_play_together)
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

        self.retranslateUi(Form)
        QMetaObject.connectSlotsByName(Form)

        self.mediaObjectVideo = phonon.Phonon.MediaObject(Form)  # 声明视频对象
        self.mediaObjectVideo.stateChanged.connect(Form.stateChanged)  # 对象改变时，应该是注册事件，响应按钮
        self.mediaObjectVideo.tick.connect(Form.videotick)  # 连接到时间

        self.mediaObjectAudio = phonon.Phonon.MediaObject(Form)  # 声明音频对象
        self.mediaObjectAudio.stateChanged.connect(Form.stateChanged_audio)  # 对象改变时，应该是注册事件，响应按钮
        self.mediaObjectAudio.tick.connect(Form.audiotick)  # 连接到时间

        # 声明视频控制端行为  包含：播放，暂停，重新开始
        self.playActionVideo = QAction(Form.style().standardIcon(QStyle.SP_MediaPlay), "Play",
                                       Form, shortcut="Ctrl+P", enabled=False, triggered=self.mediaObjectVideo.play)
        self.pauseActionVideo = QAction(Form.style().standardIcon(QStyle.SP_MediaPause), "Pause",
                                        Form, shortcut="Ctrl+A", enabled=False, triggered=self.mediaObjectVideo.pause)
        self.stopActionVideo = QAction(Form.style().standardIcon(QStyle.SP_MediaStop), "Stop",
                                       Form, shortcut="Ctrl+S", enabled=False, triggered=self.mediaObjectVideo.stop)

        # 添加视频控制端   包含 播放， 暂停， 重新开始
        videobar = QToolBar()
        videobar.addAction(self.playActionVideo)
        videobar.addAction(self.pauseActionVideo)
        videobar.addAction(self.stopActionVideo)
        # horizontalLayout_control_video是之前预留的布局，用于后续代码添加控件
        self.horizontalLayout_control_video.addWidget(videobar)

        # 声明音频控制端行为  包含：播放，暂停，重新开始
        self.playActionAudio = QAction(Form.style().standardIcon(QStyle.SP_MediaPlay), "Play", Form,
                                       shortcut="Ctrl+Alt+P", enabled=False, triggered=self.mediaObjectAudio.play)
        self.pauseActionAudio = QAction(Form.style().standardIcon(QStyle.SP_MediaPause), "Pause", Form,
                                        shortcut="Ctrl+Alt+A", enabled=False, triggered=self.mediaObjectAudio.pause)
        self.stopActionAudio = QAction(Form.style().standardIcon(QStyle.SP_MediaStop), "Stop", Form,
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

        Form.setWindowFlags(Qt.WindowMinimizeButtonHint)  # 停用窗口最大化按钮
        Form.setFixedSize(Form.width(), Form.height())  # 禁止改变窗口的大小
        #  添加播放控件
        self.videoPlayer = myVideoWidget(Form)  # 声明VideoWidget控件
        self.horizontalLayout_videoplayer.addWidget(self.videoPlayer)  # 将videoPlayer加入到预留的布局里面
        # 设置播放控件能右键产生菜单的属性
        self.videoPlayer.setContextMenuPolicy(Qt.CustomContextMenu)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.btn_cutin.setText(_translate("Form", "切入点", None))
        self.lbl_cutin.setText(_translate("Form", "00:00:00", None))
        self.btn_cutout.setText(_translate("Form", "切出点", None))
        self.lbl_cutout.setText(_translate("Form", "00:00:00", None))
        self.btn_audio_start.setText(_translate("Form", "开始点", None))
        self.lbl_audio_start.setText(_translate("Form", "00:00", None))
        self.btn_tag.setText(_translate("Form", "配乐类型", None))
        self.btn_play_together.setText(_translate("Form", "同时播放", None))
        self.btn_merge.setText(_translate("Form", "添加音频", None))
        self.btn_save.setText(_translate("Form", "写入并保存", None))

class UI_SmartBGM_Auto(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("UI_SmartBGM_Auto"))
        Form.resize(912, 633)
        self.layoutWidget = QWidget(Form)
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

        self.retranslateUi(Form)
        QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.btn_autoMatch.setText(_translate("Form", "一键配乐", None))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    smartBGM = SmartBGM()
    smartBGM.show()
    sys.exit(app.exec_())

