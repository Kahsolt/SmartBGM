# -*- coding: utf-8 -*-


from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import phonon
from SmartBGM_UI import Ui_Form
from audioTagUI import Ui_Form as subUI_Form
from PyQt4.QtCore import QThread
# from __future__ import scene_item

from Matcher import *
import sys
import os

QTextCodec.setCodecForTr(QTextCodec.codecForName("utf8"))



__author__ = 'llk2why'


try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

#多继承VideoWidget和QWidget
class myVideoWidget(phonon.Phonon.VideoWidget,QtGui.QWidget):
    def __init__(self,x):
        super(myVideoWidget,self).__init__()
        #self.videoPlayer = phonon.Phonon.VideoWidget(x)  # 声明VideoWidget控件


class Progess(QDialog):
 def __init__(self,parent=None):
     super(Progess,self).__init__(parent)
     self.setWindowTitle(self.tr("进度"))


     self.progressBar=QProgressBar()

     layout=QGridLayout()

     layout.addWidget(self.progressBar,2,2,2,2)
     # layout.addWidget(startPushButton,3,1)
     layout.setMargin(15)
     layout.setSpacing(0)

     self.setLayout(layout)



 def slotStart(self):
     num=1000


     progressDialog=QProgressDialog(self)
     progressDialog.setWindowModality(Qt.WindowModal)
     progressDialog.setMinimumDuration(5)
     progressDialog.setWindowTitle(self.tr("请等待"))
     progressDialog.setLabelText(self.tr("拷贝..."))
     progressDialog.setCancelButtonText(self.tr("取消"))
     progressDialog.setRange(0,num)

     for i in range(num):
        progressDialog.setValue(i)
        QThread.msleep(100)
        if progressDialog.wasCanceled():
            return


#继承QtGui.QWidget,实现show方法
class mainUI(QtGui.QWidget):
    def __init__(self):
        super(mainUI,self).__init__()#初始化类，待补充

        self.UI=Ui_Form()#实例化主界面
        self.UI.setupUi(self)#执行部署designer绘制的ui界面

        self.setWindowTitle(u'SmartBGM')#窗口标题
        self.setWindowIcon(QtGui.QIcon(r'\icon\SmartBGM.icon'))#设置窗口图标
        self.mediaObjectVideo = phonon.Phonon.MediaObject(self)#声明视频对象
        self.mediaObjectVideo.stateChanged.connect(self.stateChanged) # 对象改变时，应该是注册事件，响应按钮
        self.mediaObjectVideo.tick.connect(self.videotick) #连接到时间


        self.setupUi()#执行部署本类新建的控件效果

        # 绑定播放控件的右键事件
        self.connect(self.UI.videoPlayer, QtCore.SIGNAL('customContextMenuRequested (const QPoint&)'), self.openright)
        self.wating_wdn= Progess()

        # 一键合成按钮绑定事件
        self.connect(self.UI.btn_autoMatch,QtCore.SIGNAL('clicked()'),self.autoMatch)


        # combobox添加下拉标签，维护文件在外部，scene_items是list
        # for item in scene_item:
        #     self.UI.cmb_scene.addItem(item)


    def setupUi(self):
        #声明视频控制端行为  包含：播放，暂停，重新开始
        self.playActionVideo = QtGui.QAction(self.style().standardIcon(QtGui.QStyle.SP_MediaPlay),"Play",
                                             self,shortcut="Ctrl+P",enabled=False,triggered=self.mediaObjectVideo.play)
        self.pauseActionVideo = QtGui.QAction(self.style().standardIcon(QtGui.QStyle.SP_MediaPause),"Pause",
                                              self,shortcut="Ctrl+A",enabled=False,triggered=self.mediaObjectVideo.pause)
        self.stopActionVideo = QtGui.QAction(self.style().standardIcon(QtGui.QStyle.SP_MediaStop),"Stop",self,
                                             shortcut="Ctrl+S",enabled=False,triggered=self.mediaObjectVideo.stop)

        # 添加视频控制端   包含 播放， 暂停， 重新开始
        videobar = QtGui.QToolBar()
        videobar.addAction(self.playActionVideo)
        videobar.addAction(self.pauseActionVideo)
        videobar.addAction(self.stopActionVideo)
        # horizontalLayout_control_video是之前预留的布局，用于后续代码添加控件
        self.UI.horizontalLayout_control_video.addWidget(videobar)

        #  显示视频LED时间
        palette_videolcd = QtGui.QPalette()#声明调色板
        palette_videolcd.setBrush(QtGui.QPalette.Light,QtCore.Qt.darkGray)#设置刷子颜色
        self.timeLcd_video = self.UI.lcdNumber_video#将lcd数字灯赋给新的对象名
        self.timeLcd_video.setPalette(palette_videolcd)#设置配色方案
        self.timeLcd_video.display('00:00:00')#设置显示格式

        self.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint) #停用窗口最大化按钮
        self.setFixedSize(self.width(),self.height()) #禁止改变窗口的大小
        #  添加播放控件
        self.UI.videoPlayer = myVideoWidget(self)  # 声明VideoWidget控件
        self.UI.horizontalLayout_videoplayer.addWidget(self.UI.videoPlayer)  # 将videoPlayer加入到预留的布局里面
        # 设置播放控件能右键产生菜单的属性
        self.UI.videoPlayer.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

    # 需要读取combobox信息，以及checkbox信息
    def autoMatch(self):
        # self.subUI.show()
        # print 'a'
        # self.subUI.slotStart()
        num = 1000
        progressDialog = QProgressDialog(self)
        progressDialog.setWindowModality(Qt.WindowModal)
        progressDialog.setMinimumDuration(5)
        progressDialog.setWindowTitle(self.tr("请等待"))
        progressDialog.setLabelText(self.tr("配乐中 ..."))
        progressDialog.setCancelButtonText(self.tr("取消"))
        progressDialog.setRange(0, num)

        for i in range(num):
            progressDialog.setValue(i)
            QThread.msleep(100)
            if progressDialog.wasCanceled():
                return


    # video screen 右键菜单
    def openright(self):
        popMenu = QtGui.QMenu()#弹出菜单控件
        #添加弹出菜单项，自定义图标，并且绑定事件，分别为加载音频和加载视频
        popMenu.addAction(QtGui.QAction(QtGui.QIcon(r'.\icon\video.ico'),u'打开视频文件',self,enabled = True, triggered=self.openvideo))
        # popMenu.addAction(QtGui.QAction(QtGui.QIcon(r'.\icon\audio.ico'),u'音频文件',self,enabled = True, triggered=self.openaudio))
        popMenu.exec_(QtGui.QCursor.pos())

    # 选择打开音频
    # def openaudio(self):
    #     Qfile = self.addFiles('audio')
    #     if not Qfile:
    #         return
    #
    #     self.audiolist.clear()# 当前的音频清单
    #     self.UI.comboBox.clear()
    #
    #     self.audiofile=Qfile
    #     file = unicode(Qfile)
    #
    #     fpath, fname = os.path.split(file)
    #     # print fpath,fname
    #     self.audiolist[fname] = file
    #     # print self.audiolist[fname]
    #     self.UI.comboBox.addItem(fname)
    #
    #     self.mediaObjectAudio.setCurrentSource(phonon.Phonon.MediaSource(Qfile))
    #     #初始化音频的输出按钮
    #     self.audioOutput_audio = phonon.Phonon.AudioOutput(phonon.Phonon.VideoCategory,self)
    #     phonon.Phonon.createPath(self.mediaObjectAudio, self.audioOutput_audio)
    #     #连接到音量
    #     #self.UI.volumeSlider.setAudioOutput(self.audioOutput_audio)
    #     #连接到进度条
    #     self.UI.seekSlider_audio.setMediaObject(self.mediaObjectAudio)
    #     self.mediaObjectAudio.play()


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
            QtGui.QMessageBox.question(self,(u'提示'),(u'请先读取视频！'),QtGui.QMessageBox.Ok)
        elif err_num == 2:
            QtGui.QMessageBox.question(self, (u'提示'), (u'请先指定音频插入的视频段的起始时间！'),
                                       QtGui.QMessageBox.Ok)
        elif err_num == 3:
            QtGui.QMessageBox.question(self, (u'提示'), (u'当前时间小于指定的视频段起始时间，请重新指定！'),
                                       QtGui.QMessageBox.Ok)
        elif err_num == 4:
            QtGui.QMessageBox.question(self, (u'提示'), (u'视频段的时间间距太小，请重新指定！'),
                                       QtGui.QMessageBox.Ok)
        elif err_num == 5:
            QtGui.QMessageBox.question(self, (u'提示'), (u'请先指定需要的配乐类型！'), QtGui.QMessageBox.Ok)
        elif err_num == 6:
            QtGui.QMessageBox.question(self, (u'提示'), (u'请指定音视频文件和对应的时间！'), QtGui.QMessageBox.Ok)

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
        # files = QtGui.QFileDialog.getOpenFileName(self, tips, QtGui.QDesktopServices.storageLocation(
        #     QtGui.QDesktopServices.DesktopLocation), expand)
        currentPath = os.getcwd()+r'\Videos'
        #currentPath = QtGui.QDesktopServices.storageLocation(tGui.QDesktopServices.DesktopLocation)
        files = QtGui.QFileDialog.getOpenFileName(self, tips,currentPath,expand)
        print type(files)

        if not files:
            return ''
        return files

    #视频状态改变事件处理
    def stateChanged(self,newState):

        if newState == phonon.Phonon.ErrorState:#如果出现错误状态，即刻报告
            if self.mediaObjectVideo.errorType() == phonon.Phonon.FatalError:
                QtGui.QMessageBox.warning(self,"Fatal Error",
                        self.mediaObjectVideo.errorString())
            else:
                QtGui.QMessageBox.warning(self,"Error",
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

    # 时间绑定
    def videotick(self,time):
        #相关函数的时间度量是以ms为单位
        self.displayTime = QtCore.QTime((time /3600000),(time /60000)%60,(time / 1000)%60)
        self.timeLcd_video.display(self.displayTime.toString('hh:mm:ss'))



    #响应esc退出画面
    def keyPressEvent(self,event):
        if event.key()==QtCore.Qt.Key_Escape:
            self.close();

# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from PyQt4 import phonon

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(912, 633)
        self.layoutWidget = QtGui.QWidget(Form)
        self.layoutWidget.setGeometry(QtCore.QRect(0, 0, 911, 631))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.layoutWidget)
        self.verticalLayout_3.setMargin(0)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.horizontalLayout_videoplayer = QtGui.QHBoxLayout()
        self.horizontalLayout_videoplayer.setObjectName(_fromUtf8("horizontalLayout_videoplayer"))
        self.verticalLayout_3.addLayout(self.horizontalLayout_videoplayer)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.horizontalLayout_control_video = QtGui.QHBoxLayout()
        self.horizontalLayout_control_video.setObjectName(_fromUtf8("horizontalLayout_control_video"))
        self.horizontalLayout_2.addLayout(self.horizontalLayout_control_video)
        self.line = QtGui.QFrame(self.layoutWidget)
        self.line.setFrameShape(QtGui.QFrame.VLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.horizontalLayout_2.addWidget(self.line)
        self.seekSlider_video = phonon.Phonon.SeekSlider(self.layoutWidget)
        self.seekSlider_video.setObjectName(_fromUtf8("seekSlider_video"))
        self.horizontalLayout_2.addWidget(self.seekSlider_video)
        self.lcdNumber_video = QtGui.QLCDNumber(self.layoutWidget)
        self.lcdNumber_video.setNumDigits(8)
        self.lcdNumber_video.setObjectName(_fromUtf8("lcdNumber_video"))
        self.horizontalLayout_2.addWidget(self.lcdNumber_video)
        self.line_2 = QtGui.QFrame(self.layoutWidget)
        self.line_2.setFrameShape(QtGui.QFrame.VLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
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
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.btn_autoMatch = QtGui.QPushButton(self.layoutWidget)
        self.btn_autoMatch.setObjectName(_fromUtf8("btn_autoMatch"))
        self.horizontalLayout.addWidget(self.btn_autoMatch)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.cmb_scene = QtGui.QComboBox(self.layoutWidget)
        self.cmb_scene.setObjectName(_fromUtf8("cmb_scene"))
        self.horizontalLayout.addWidget(self.cmb_scene)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.chk_ost = QtGui.QCheckBox(self.layoutWidget)
        self.chk_ost.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.chk_ost.setObjectName(_fromUtf8("chk_ost"))
        self.horizontalLayout.addWidget(self.chk_ost)
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.horizontalLayout.setStretch(0, 10)
        self.horizontalLayout.setStretch(1, 2)
        self.horizontalLayout.setStretch(2, 10)
        self.horizontalLayout.setStretch(3, 5)
        self.horizontalLayout.setStretch(4, 1)
        self.horizontalLayout.setStretch(5, 2)
        self.horizontalLayout.setStretch(6, 1)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        spacerItem4 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem4)
        self.verticalLayout_3.setStretch(0, 50)
        self.verticalLayout_3.setStretch(1, 2)
        self.verticalLayout_3.setStretch(2, 2)
        self.verticalLayout_3.setStretch(3, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.btn_autoMatch.setText(_translate("Form", "一键配乐", None))
        self.chk_ost.setText(_translate("Form", "原声", None))




if __name__ == '__main__':
    app=QtGui.QApplication(sys.argv)
    mainapp = mainUI()
    app.setQuitOnLastWindowClosed(True)
    mainapp.show()
    sys.exit(app.exec_())
