#!/usr/bin/env python
#-*- coding:utf-8 _*-
__author__ = 'LJjia'
# *******************************************************************
#     Filename @  ConfirmSatisfy.py
#       Author @  Jia LiangJun
#  Create date @  2019/05/13 20:39
#        Email @  LJjiahf@163.com
#  Description @  此程序用于用户确定标定的宽是否满足要求
# ********************************************************************
import os
from PIL import Image
import pickle
import numpy as np


# 用户确认所画出的位置数据结果是否满意
def CustConfirmPosDict(satisfy,ChipName):
    foldname = 'CustomerDefineModel'
    # 因为此处使用先创建临时字典再导入字典的形式，而不是直接更新字典
    filenameTmp = foldname + '/' + ChipName+'Tmp'+'.pickle'
    if not os.path.exists(filenameTmp):
        print('未找到保存的文件')
        return
    filename=foldname + '/' + ChipName +'.pickle'

    if satisfy:
        #保存对应位置的图片
        if not os.path.exists(filename):
            # 如果是最初创立字典
            SaveModelImage(filenameTmp,filename,ifFirst=True)
        else:
            # 如果已经创立过字典
            SaveModelImage(filenameTmp,filename,ifFirst=False)
        return 'Done'
    else:
        if os.path.exists(filenameTmp):
            os.remove(filenameTmp)
        return 'Done'


# 保存小图片
def SaveModelImage(ModelDictPath,OriginModelDictPath,ifFirst,SaveFormat='jpg'):
    Suffix, ImgSaveFormat = GetImageSuffixAndSaveFormat(SaveFormat)
    with open(ModelDictPath, 'rb')as ModelDict:
        Dict = pickle.load(ModelDict)
    # print('载入字典',Dict)
    ImagePath=Dict.get('ChipImagePath')
    ChipName=Dict.get('ChipName')
    if Dict.get('ifNest'):
        Format=numxnum2tuple(Dict.get('Format'))
        FormatMicro=numxnum2tuple(Dict.get('FormatMicro'))
        ColNum=Format[1]*FormatMicro[1]
    else:
        Format = numxnum2tuple(Dict.get('Format'))
        ColNum= Format[1]
    # 获取当前行
    CurLine=Dict.get('CurrentPos')[0]

    ChipSize=Dict.get('ChipSize')
    img=Image.open(ImagePath)
    # 创建保存目录
    FolderPath=CreatMatchModelFolder(ChipName,CurLine)
    # 保存和统计图像时是否也加入白边保存
    ifWhiteBorder=True
    # 获取白边的宽度 之后可能需要用到，看在字典中有没有写
    WhiteWidth=Dict.get('WhiteBorder')
    for col in range(1,ColNum+1):
        PosStr=str(CurLine)+'_'+str(col)
        ChipLeftUpPos=Dict.get(PosStr)
        if ifWhiteBorder:
            cropimg = img.crop(GetCropTupleWithWhiteBorder(ChipLeftUpPos, ChipSize))
        else:
            cropimg=img.crop(GetCropTuple(ChipLeftUpPos,ChipSize))
        cropimg.save(FolderPath+'/'+PosStr+Suffix,ImgSaveFormat)
        BlackNum=GetBlackNum(cropimg)
        WriteToDict(Dict,key='BlackNum'+PosStr,value=BlackNum)

    # print('保存字典',Dict)
    # # 改变字典维度计算方法
    # ChangeDictTuple(Dict,'Foramt')
    # ChangeDictTuple(Dict, 'ForamtMicro')
    if ifFirst:
        # 如果是第一次创立字典
        with open(OriginModelDictPath, 'wb') as Config_File_Save:
            pickle.dump(Dict, Config_File_Save)
        if os.path.exists(ModelDictPath):
            os.remove(ModelDictPath)
    else:
        # 如果之前已经创立了字典 ，采用字典合并的形式
        with open(OriginModelDictPath, 'rb')as ModelDict:
            OriginDict = pickle.load(ModelDict)
        OriginDict=DictMergeAtoB(dictA=Dict,dictB=OriginDict)
        # 覆盖旧字典并删除tmp
        with open(OriginModelDictPath, 'wb') as Config_File_Save:
            pickle.dump(OriginDict, Config_File_Save)
        if os.path.exists(ModelDictPath):
            os.remove(ModelDictPath)

# 改变字典元组中的顺序
def ChangeDictTuple(dict,key):
    value=dict.get(key)
    dict[key]=(value[1],value[0])


# 两个字典的合并，重复的部分，B中的内容会被A的部分覆盖掉
def DictMergeAtoB(dictA, dictB):
    dictB = dict(dictB, **dictA)
    return dictB


# 更新字典中的内容 注意这里的字典的key-value 如果存在，则会被覆盖
def WriteToDict(Dict,key,value):
    Dict[key]=value


# 获取图片中黑色像素点的个数
# 输入PIL格式图片，二值化阈值  返回黑色像素点个数
def GetBlackNum(img,BinaryThreshold=180):
    # 转化为灰度图
    GrayImage = img.convert('L')
    #  自己设置转化过程中二值化的阈值
    #  255为全白 0为全黑
    table = []
    for i in range(256):
        if i < BinaryThreshold:
            table.append(0)
        else:
            table.append(1)
    BinaryImage = GrayImage.point(table, '1')
    BinaryImageArray = np.array(BinaryImage) + 0  # 这样结果就会是0 1 而不是True False
    BlackNum=BinaryImageArray.shape[0]*BinaryImageArray.shape[1]-np.sum(BinaryImageArray)
    return BlackNum

# 创建文件夹用于存储标注之后的结果图片
def CreatMatchModelFolder(ChipName,CurLine):
    foldername = 'MatchModel'+'/'+ChipName+'/'+'Line'+str(CurLine)
    if not os.path.exists(foldername):
        os.makedirs(foldername)
    return foldername

# 方便获取crop元组
def GetCropTuple(whPixel,ChipSize):
    tmp=( whPixel[0],whPixel[1],whPixel[0]+ChipSize[0] ,whPixel[1]+ChipSize[1])
    return tmp
# 带有白边的crop元组
def GetCropTupleWithWhiteBorder(whPixel,ChipSize,WhiteWidth=5):

    tmp=( whPixel[0]-WhiteWidth,whPixel[1]-WhiteWidth,
          whPixel[0]+ChipSize[0]+WhiteWidth ,whPixel[1]+ChipSize[1]+WhiteWidth)
    # print('裁剪位置',tmp)
    return tmp



# 把 '4x4' 字符串变为元组(4,4)
def numxnum2tuple(ArrayStr):
    returntuple = (int(ArrayStr.split('x')[0]), int(ArrayStr.split('x')[1]))
    return returntuple

# 获得不同格式的图片的后缀名和保存格式
def GetImageSuffixAndSaveFormat(types):
    if types == 'bmp' or types == 'BMP':
        return '.bmp', 'bmp'
    if types == 'jpg' or types == 'JPG':
        return '.jpg', 'jpeg'
    if types == 'jpeg' or types == 'JPEG':
        return '.jpeg', 'jpeg'




if __name__ == '__main__':
    CustConfirmPosDict(True,'CustomerDefine5')
