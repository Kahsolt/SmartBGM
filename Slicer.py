#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#==========================
#  Name:        Slicer
#  Author:      ???
#  Time:        yyyy/mm/dd
#  Desciption:  Clip video into frame slices

# Configurations
#
# put your module level global var here

# Imports
import numpy as np
import string
from subprocess import Popen

# put your imports here

# Classes
class Slicer:

    # def gettheCommand(self):
    #     self.CommandP2=self.videoName
    #     self.CommandP4=self.ImgperSecond
    #     Command=self.CommandP1+self.CommandP2+self.CommandP3+self.CommandP4+self.CommandP5
    #     p = Popen(args=cmd,shell=True)
    #     return p

    # delte all imgs in temp folder
    # I'm not sure this command is ok or not in ubuntu
    def initImgs(self):
        delCMD=r"rm "+self.imgDir+"/img/*.png"
        print delCMD
        p = Popen(args=delCMD, shell=True)

    # transfer video to imgs
    # def VTI(self):
    #     cmd = self.gettheCommand()
    #     p = Popen(args=cmd, shell=True)

    def __init__(self, path_to_video,sample_rate=0.1):

        self.videoName=path_to_video
        self.videodir=r"Videos"
        self.imgDir=r'tmp'
        self.batdir=r'VideotoImgs'

        # self.videoName=r'cononL.mp4'
        self.ImgperSecond="fps="+str(sample_rate)
        self.defaultCommand="ffmpeg -i videoname -vf imgpersecond image-%03d.png"
        self.CommandP1="ffmpeg -i "
        self.CommandP2=""
        self.CommandP3=" -vf "
        self.CommandP4=""
        self.CommandP5=r" tmp/img/image-%03d.png"
        self.initImgs()

    def slice(self):
        self.CommandP2=self.videoName
        self.CommandP4=self.ImgperSecond
        Command=self.CommandP1+self.CommandP2+self.CommandP3+self.CommandP4+self.CommandP5
        p = Popen(args=Command,shell=True)
        return r" tmp/img"
        # return 'path_to_frame_slices_dir'


# Main Entrance
def main():
    # 1.Construct
    # slicer = Slicer('path_to_video',sample_rate)
    s1=Slicer('test/cononL.mp4')
    
    #cmd=s1.gettheCommand()
    #p = Popen(args=cmd,shell=True)

    # 2.Configure
    # slicer.sample_rate = 1    # extract one frame per second
    

    # 3.Call methods
    # path_to_frame_slices_dir = slicer.slice()

    # format is tmp/img
    s1.slice()

if __name__ == '__main__':
    # Run a Module as Main will run the example test routine
    main()
