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

class Analyzer:
    def __init__(self,path_to_img):
        self.path_to_img = path_to_img
        self.class_name=['动物世界','海洋生物','中国传统文化','穆斯林',\
        '潮流','运输工具','生活用品','艺术、乐器','房子家具','军用物品','运动',\
        '人','服饰','室外','建筑','游乐园','景色','浪漫','特殊','工具',\
                         '雄壮、中世纪','水果蔬菜']
        self.class_len = len(self.class_name)
        self.id_set={}
        self.id_set[self.class_name[0]] = \
        {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,\
         23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,\
         42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,\
         61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,\
         80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,\
         99,100,101,102,103,104,105,106,107,108,109,110,111,112,\
         113,114,115,116,117,118,119,120,121,122,123,124,125,126,\
         127,128,129,130,131,132,133,134,135,136,137,138,139,140,\
         141,142,143,144,145,146,147,148,149,150,151,152,153,154,\
         155,156,157,158,159,160,161,162,163,164,165,166,167,168,\
         169,170,171,172,173,174,175,176,177,178,179,180,181,182,\
         183,184,185,186,187,188,189,190,191,192,193,194,195,196,\
         197,198,199,200,201,202,203,204,205,206,207,208,209,210,\
         211,212,213,214,215,216,217,218,219,220,221,222,223,224,\
         225,226,227,228,229,230,231,232,233,234,235,236,237,238,\
         239,240,241,242,243,244,245,246,247,248,249,250,251,252,\
         253,254,255,256,257,258,259,260,261,262,263,264,265,266,\
         267,268,269,270,271,272,273,274,275,276,277,278,279,280,\
         281,282,283,284,285,286,287,288,289,290,291,292,293,294,\
         295,296,297,298,299,300,301,302,303,304,305,306,307,308,\
         309,310,311,312,313,314,315,316,317,318,319,320,321,322,\
         323,324,325,326,327,328,329,330,331,332,333,334,335,336,\
         337,338,339,340,341,342,343,344,345,346,347,348,349,350,\
         351,352,353,354,355,356,357,358,359,360,361,362,363,364,\
         365,366,367,368,369,370,371,372,373,374,375,376,377,378,\
         379,380,381,382,383,384,385,386,387,388,389,390,391,392,\
         393,394,395,396,397,398}
        self.id_set[self.class_name[1]] = \
        {108,109,110,111,112,113,114,115,116,117,118,119,120,121,\
         122,123,124,125,126,127,128,129,130,131,132,133,134,135,\
         136,137,138,139,140,141,142,143,144,145,146,147,148,149,\
         150,151}
        self.id_set[self.class_name[2]] = \
        {399,589,613}
        self.id_set[self.class_name[3]] = \
        {400}
        self.id_set[self.class_name[4]] = \
        {401,402,403}
        self.id_set[self.class_name[5]] = \
        {404,405,406,408,409,437,467,469,511,512,556,570,574,575,\
         576,577,578,610,626,628,629,655,657,661,662,818}
        self.id_set[self.class_name[6]] = \
        {410,411,412,413,415,416,419,420,421,422,427,428,429,435,\
         436,439,441,442,444,446,447,452,453,456,463,464,470,471,\
         473,474,476,478,479,480,481,482,483,484,486,488,489,490,\
         491,492,493,494,495,496,497,498,500,503,504,505,506,507,\
         508,509,510,517,522,524,525,528,529,531,532,534,549,550,\
         551,552,553,554,565,566,568,620
}
        self.id_set[self.class_name[7]] = \
        {487,514,543,544,545,547,548,559,560,567,580}
        self.id_set[self.class_name[8]] = \
        {424,425,426,454,527,528,529,533,534,535,546,557}
        self.id_set[self.class_name[9]] = \
        {414,448,466,472,473,500,501,519,520,521,658}
        self.id_set[self.class_name[10]] = \
        {417,418,423,430,431,434,445,451,457,523,561,984}
        self.id_set[self.class_name[11]] = \
        {432,440,618,653}
        self.id_set[self.class_name[12]] = \
        {458,460,465,475,515,516,611,615,656,659}
        self.id_set[self.class_name[13]] = \
        {446,459,468,499,558,572,583}
        self.id_set[self.class_name[14]] = \
        {438,443,449,450,455,468,499,526,537,538,539,555,557,572,\
         625}
        self.id_set[self.class_name[15]] = \
        {477}
        self.id_set[self.class_name[16]] = \
        {438,461,526,537,538,541,555,971,972,973,974,975,976,977,\
         978,979,980,981,982}
        self.id_set[self.class_name[17]] = \
        {471,573,579,580}
        self.id_set[self.class_name[18]] = \
        {462,518,530,536,540,562,563,564,571,581,582,584,585,586,\
         587,588,589,590,591,592,593,594,595,596,597,598,599,600,\
         601,602,603,604,605,606,607,608,609,612,613,614,616,617,\
         622,623,626,627,628,629,630,631,632,633,634,635,636,637,\
         638,639,640,641,642,643,644,645,646,647,648,649,650,651,\
         652,663,664,665,666,667,668,669,670,671,672,673,674,675,\
         676,677,678,679,680,681,682,683,684,685,686,687,688,689,\
         690,691,692,693,694,695,696,697,698,699,700,701,702,703,\
         704,705,706,707,708,709,710,711,712,713,714,715,716,717,\
         718,719,720,721,722,723,724,725,726,727,728,729,730,731,\
         732,733,734,735,736,737,738,739,740,741,742,743,744,745,\
         746,747,748,749,750,751,752,753,754,755,756,757,758,759,\
         760,761,762,763,764,765,766,767,768,769,770,771,772,773,\
         774,775,776,777,778,779,780,781,782,783,784,785,786,787,\
         788,789,790,791,792,793,794,795,796,797,798,799,800,801,\
         802,803,804,805,806,807,808,809,810,811,812,813,814,815,\
         816,817,818,819,820,821,822,823,824,825,826,827,828,829,\
         830,831,832,833,834,835,836,837,838,839,840,841,842,843,\
         844,845,846,847,848,849,850,851,852,853,854,855,856,857,\
         858,859,860,861,862,863,864,865,866,867,868,869,870,871,\
         872,873,874,875,876,877,878,879,880,881,882,883,884,885,\
         886,887,888,889,890,891,892,893,894,895,896,897,898,899,\
         900,901,902,903,904,905,906,907,908,909,910,911,912,913,\
         914,915,916,917,918,919,920,921,922,923,924,925,926,927,\
         928,929,930,931,932,933,934,935,936,937,938,939,940,941,\
         942,943,944,945,946,947,948,949,950,951,952,953,954,955,\
         956,957,958,959,960,961,962,963,964,965,966,967,968,969,\
         970,971,972,973,974,975,976,977,978,979,980,981,982,983,\
         984,985,986,987,988,989,990,991,992,993,994,995,996,997,\
         998,999,1000}
        self.id_set[self.class_name[19]] = \
        {478,479,480,481,482,483,484,619,620,624,654,660}
        self.id_set[self.class_name[20]] = \
        {462,485,501,502,519,520,521,569,584}
        self.id_set[self.class_name[21]] = \
        {924,925,926,927,928,929,930,931,932,933,934,935,936,937,\
         938,939,940,941,942,943,944,945,946,947,948,949,950,951,\
         952,953,954,955,956,957,958,959,960,961,962,963,964,965,\
         966,967,968,969,970,985,986,987,988,989,990,991,992,993,\
         994,995,996,997,998,999}

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
        print image_paths
        # sys.exit()

        for img in image_paths:
            im=caffe.io.load_image(img)
            googlenet_net.blobs['data'].data[...] = transformer.preprocess('data',im)
            out = googlenet_net.forward()
            output_prob = out['prob'][0]

            record = []
            image_name = os.path.split(img)[1]
            print image_name
            top_inds=output_prob.argsort()[::-1][:5]
            for i in np.arange(top_inds.size):
                print top_inds[i],output_prob[top_inds[i]], labels_ilsvrc[top_inds[i]]
                line = output_prob[top_inds[i]], labels_ilsvrc[top_inds[i]]
                line = list(line)
                statistics = {} #每种可能
                statistics['pos']=str(float(line[0]))[:6]
                # statistics['id']=line[1].split(' ')[0]
                statistics['id'] = top_inds[i]
                record.append(statistics) #每张图片可能性的集合

            img_data.append(record)  #顺序存入可能性集合，内容为集合

        # json_data=json.dumps(img_data)
        # with open(FOUT_TAG,"w") as jd:
        #     json.dump(json_data,jd)

        return (img_data,len(image_paths))

    '''
    将识别内容归为大类,返回大类信息,10nset+nleft,10张图片一个信息集合，
    余下来的图片划归为一个信息集合
    video_tags 包含每张图片前五的可能性的识别信息
    '''
    def collect(self, video_tags, num):
        nset = num/10 #nset个完整的10张图片集
        nleft = num%10 #nleft张余下的图片

        collection = [] # 大类信息集合,每个成员包含10张图片数据,最后一个成员包含余下的数据


        for i in range(nset): #遍历每套图片集
            img_unit = {} # 用于统计每个十张图片的信息
            for j in self.class_name: #遍历所有分类索引键，所有的分类可能性初始化为零
                img_unit[j]=float(0.0)
            for j in range(10): #遍历每张图片
                index = 10*i+j  #stuck here. [[{},{},{},{},{}]..]
                for k in video_tags[index]: #遍历每张图片识别结果的所有可能性
                    for m in self.class_name: #遍历每种分类的名字
                        if k['id'] in self.id_set[m]: #给分类增加识别权重
                            img_unit[m] += float(k['pos'])
                            # print float(k['pos'])
            # print json.dumps(img_unit, encoding="UTF-8", ensure_ascii=False)
            img_unit = self.gettop(img_unit)
            collection.append(img_unit)

        img_unit = {}
        for j in self.class_name:  # 遍历所有分类索引键，所有的分类可能性初始化为零
            img_unit[j] = float(0.0)
        for j in range(nleft):  # 遍历每张图片
            index = 10 * nset + j  # stuck here. video_tags=[[{},{},{},{},{}]..]
            for k in video_tags[index]:  # 遍历每张图片识别结果的所有可能性
                for m in self.class_name:  # 遍历每种分类的名字
                    if k['id'] in self.id_set[m]:  # 给分类增加识别权重
                        img_unit[m] += float(k['pos'])
                        # print float(k['pos'])
        # print json.dumps(img_unit, encoding="UTF-8", ensure_ascii=False)
        img_unit = self.gettop(img_unit) # {id:value,id:value...} to [[id,value],[],[]...]
        collection.append(img_unit)

        # print json.dumps(collection, encoding="UTF-8", ensure_ascii=False)
        return collection

    def pos_cmp(self,x,y):
        if x[1] < y[1]:
            return 1
        if x[1] > y[1]:
            return -1
        return 0

    def gettop(self,img_unit):
        sorted_res = []

        for key in img_unit.keys():
            tmp = []
            tmp.append(key)
            tmp.append(img_unit[key])
            sorted_res.append(tmp)

        sorted_res = sorted(sorted_res,self.pos_cmp)

        if sorted_res[0][0] == '特殊':
            sorted_res = sorted_res[1:6]
        else:
            sorted_res = sorted_res[5]

        return sorted_res




    def analyze(self): #
        video_tags, img_len = self.recognition()
        collection_tags = self.collect(video_tags, img_len)
        return collection_tags




# Main Entrance
def main():

    path_to_frame_slices_dir = '/home/lincoln/Desktop/SmartBGM/tmp/img'

    analyzer = Analyzer(path_to_frame_slices_dir)

    collection = analyzer.analyze()

    for i in range(len(collection)):
        print json.dumps(collection[i], encoding="UTF-8", ensure_ascii=False)


def unittest():
    path_to_frame_slices_dir = '/home/lincoln/Desktop/SmartBGM/tmp/img'

    analyzer = Analyzer(path_to_frame_slices_dir)

    analyzer.collect({}, 95)

if __name__ == '__main__':
    # Run a Module as Main will run the example test routine
    way = 1
    if way ==1 :
        main()
    else:
        unittest()