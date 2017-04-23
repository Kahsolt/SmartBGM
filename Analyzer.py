#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#==========================
#  Name:        Analyzer
#  Author:      llk2why
#  Time:        2017/04/16
#  Desciption:  Analyze video clips to generate video tags

# Configurations
#
# put your module level global var here

# Imports
#
# put your imports here
from Slicer import *
import numpy as np
import sys,os
import json
import caffe

IMAGE_INFO_SINGLE = False
IMAGE_INFO = False

class Analyzer:
    def __init__(self,path_to_img):
        self.nrank = 5

        self.path_to_img = path_to_img

        self.idset = []
        for i in range(1,1001):
            self.idset.append(i)

    def recognition(self): #通过caffe识别每张图片的内容
        this_location = os.path.abspath('.')
        # image_dir = os.path.join(this_location,'tmp/pics')
        image_dir = self.path_to_img
        FOUT_TAG = os.path.join(this_location,'tags_google.json')
        IMAGE_EXT = '.jpg'
        caffe_root = '/home/lincoln/caffe-master/'


        #googlenet Net
        googlenet_DIR = 'bvlc_googlenet'
        googlenet_root = caffe_root+'models/'+googlenet_DIR+'/'
        googlenet_model_file = googlenet_root + 'deploy.prototxt'
        googlenet_pretrained_file = googlenet_root + '{0}.caffemodel'.format(googlenet_DIR)
        googlenet_mean_file = caffe_root + 'python/caffe/imagenet/ilsvrc_2012_mean.npy'
        imagenet_labels_filename = caffe_root + 'data/ilsvrc12/synset_words.txt'

        googlenet_net = caffe.Net(googlenet_model_file,googlenet_pretrained_file,caffe.TEST)
        transformer = caffe.io.Transformer({'data': googlenet_net.blobs['data'].data.shape})
        transformer.set_transpose('data', (2,0,1))
        transformer.set_mean('data', np.load(googlenet_mean_file).mean(1).mean(1))
        transformer.set_raw_scale('data', 255)
        transformer.set_channel_swap('data', (2,1,0))
        #googlenet Net
        labels_ilsvrc = np.loadtxt(imagenet_labels_filename, str, delimiter='\t')

        caffe.set_device(0)
        caffe.set_mode_gpu()


        image_paths=[]
        for root,dirs,files in os.walk(image_dir):
            for file in files:
                if file.endswith('jpg'):
                    if file not in image_paths:
                        image_paths.append(int(os.path.splitext(file)[0]))
            image_paths.sort()
            for i in range(0,len(image_paths)):
                image_paths[i]=os.path.join(root,str(image_paths[i])+IMAGE_EXT)


        img_data = []
        if IMAGE_INFO_SINGLE:
            print image_paths

        for img in image_paths:
            im=caffe.io.load_image(img)
            googlenet_net.blobs['data'].data[...] = transformer.preprocess('data',im)
            out = googlenet_net.forward()
            output_prob = out['prob'][0]

            record = []
            image_name = os.path.split(img)[1]
            if IMAGE_INFO_SINGLE:
                print image_name
            top_inds=output_prob.argsort()[::-1][:5]
            for i in np.arange(top_inds.size):
                if IMAGE_INFO_SINGLE:
                    print top_inds[i],output_prob[top_inds[i]], labels_ilsvrc[top_inds[i]]
                line = output_prob[top_inds[i]], labels_ilsvrc[top_inds[i]]
                line = list(line)
                statistics = {} #每种可能
                statistics['pos']=str(float(line[0]))[:6]
                # statistics['id']=line[1].split(' ')[0]
                statistics['id'] = top_inds[i]
                record.append(statistics) #每张图片可能性的集合

            img_data.append(record)  #顺序存入可能性集合，内容为集合

        if IMAGE_INFO:
            for i in img_data:
                print i

        print '[Analyzer.py recognition]: video recognized'
        return img_data


    def merge(self, video_tags):
        img_unit = {}

        for i in self.idset:  # 遍历所有分类索引键，所有的分类可能性初始化为零
            img_unit[i] = float(0.0)

        for i in video_tags: # [[{},{},{},{},{}]..]
            for j in i:
                img_unit[j['id']] += float(j['pos'])

        #给字典排序,输出排序后的元组结构（id,pos_sum）
        img_unit = sorted(img_unit.items(),key= lambda d:d[1],\
                          reverse=True)[:self.nrank]

        # 打开合并分类文件 RecognitionDB.txt
        f = open("RecognitionDB.txt")
        line = f.readline()
        idset = []
        while line:
            item = []
            line = line.split('\t')

            item.append(line[0])
            item.append(line[2])
            # item.append(line[3][:-2])
            item.append(line[3])

            line = f.readline()

            idset.append(item)
        f.close()

        res = []

        for tup in img_unit:
            for item in idset:
                if int(tup[0])>=int(item[1]) and int(tup[0])<=int(item[2]):
                    # toptup.append(item[0])
                    # toptup.append(tup[0])
                    # toptup.append(tup[1])
                    toptup = (item[0],tup[0],tup[1])
                    res.append(toptup)
                    break


        print '[Analyzer.py  merge]: video tags merged'
        return res


    def analyze(self): #
        video_tags= self.recognition()
        collection = self.merge(video_tags)
        # print collection
        return collection




# Main Entrance
def main():

    path_to_frame_slices_dir = '/home/lincoln/Desktop/SmartBGM/tmp/img'
    analyzer = Analyzer(path_to_frame_slices_dir)
    collection = analyzer.analyze()
    for item in collection:
        print item[0],item[1:]


def unittest():
    pass

if __name__ == '__main__':
    # Run a Module as Main will run the example test routine
    way = 1
    if way ==1 :
        main()
    else:
        unittest()