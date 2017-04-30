#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#==========================
#  Name:        Slicer
#  Author:      zr; and kahsolt fucked it up
#  Time:        2017/04/22
#  Desciption:  Clip video into frame slices

# Configurations
SLICER_DEFAULT_FPS = 1
SLICER_TMP_IMG = "./tmp/img"

# Imports
import os

# Classes
class Slicer:
    def __init__(self, path_to_video):
        self.videofile = path_to_video
        self.fpsrate = SLICER_DEFAULT_FPS

        self.clearTmp()

    def clearTmp(self):
        cmdDel = r"rm " + SLICER_TMP_IMG + "/*.jpg"
        print '[Slicer] executing cmd "%s"' % (cmdDel)
        res = os.popen(cmdDel)

    def fps_rate(self,rate):
        self.fpsrate = rate

    def slice(self):
        cmdFfmpeg = 'ffmpeg -i "%s" -vf fps=%f "%s/%%d.jpg"'% (self.videofile, self.fpsrate, SLICER_TMP_IMG)
        print '[Slicer] executing cmd "%s"'% (cmdFfmpeg)
        res = os.popen(cmdFfmpeg)
        return SLICER_TMP_IMG + '/'

# Main Entrance
def main():
    # 1.Construct
    # slicer = Slicer('path_to_video')
    slicer = Slicer(path_to_video='test/cononL.mp4')

    # 2.Configure
    # slicer.sample_rate = 1    # extract one frame per second
    slicer.fps_rate(1)

    # 3.Call methods
    path_to_frame_slices_dir = slicer.slice()

if __name__ == '__main__':
    # Run a Module as Main will run the example test routine
    main()
