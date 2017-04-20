#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#==========================
#  Name:        Slicer
#  Author:      zr
#  Time:        2017/04/16
#  Desciption:  Clip video into frame slices

# Configurations
path_to_img=r"tmp/img/"
fps_rate=0.1

# Imports
import numpy as np
import string
from subprocess import Popen

# Classes
class Slicer:

    # delte all imgs in temp folder
    def initImgs(self):
        delCMD=r"rm "+path_to_img+"*.jpg"
        print delCMD
        p = Popen(args=delCMD, shell=True)

    def __init__(self, path_to_video):

        self.videoName=path_to_video
        # self.videodir=r"Videos"
        # self.imgDir=r'tmp'
        # self.batdir=r'VideotoImgs'

        # self.videoName=r'cononL.mp4'
        self.ImgperSecond="fps=1"
        self.defaultCommand="ffmpeg -i videoname -vf imgpersecond %d.jpg"
        self.CommandP1="ffmpeg -i "
        self.CommandP2=""
        self.CommandP3=" -vf "
        self.CommandP4=""
        self.CommandP5=" "+path_to_img+r"%d.jpg"
        self.initImgs()

    def fps_rate(self,rate):
        fps_rate=rate
        self.ImgperSecond="fps="+str(fps_rate)

    def slice(self):
        self.CommandP2='"'+self.videoName+'"'
        self.CommandP4=self.ImgperSecond
        Command=self.CommandP1+self.CommandP2+self.CommandP3+self.CommandP4+self.CommandP5
        p = Popen(args=Command,shell=True)
        return r"tmp/img/"
        # return 'path_to_frame_slices_dir'


# Main Entrance
def main():
    # 1.Construct
    # slicer = Slicer('path_to_video',sample_rate)
    slicer=Slicer(path_to_video='test/campus.flv')
    
    #cmd=s1.gettheCommand()
    #p = Popen(args=cmd,shell=True)

    # 2.Configure
    # slicer.sample_rate = 1    # extract one frame per second
    slicer.fps_rate(1)

    # 3.Call methods
    # path_to_frame_slices_dir = slicer.slice()

    # format is tmp/img
    path_to_frame_slices_dir=slicer.slice()

if __name__ == '__main__':
    # Run a Module as Main will run the example test routine
    main()
