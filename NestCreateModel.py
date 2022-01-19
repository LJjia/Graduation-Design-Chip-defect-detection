#!/usr/bin/env python
# -*- coding:utf-8 _*-
__author__ = 'LJjia'
# *******************************************************************
#     Filename @  Nest.py
#       Author @  Jia LiangJun
#  Create date @  2019/05/09 10:44
#        Email @  LJjiahf@163.com
#  Description @  此版本需使用嵌套组别，从txt中读取源数据，并且结果保存在字典中，
#                 每次调用程序只更新字典中的一行
#                 注：此程序只是用户自定义模版需要调用的
# ********************************************************************


import os
from PIL import Image, ImageDraw
import numpy as np
import pickle
import cv2


# 生成标注框的总函数入口，此函数连接两个函数，分别对应矩阵类型的芯片以及行类型的芯片
def CreateLabelBox(shape):
    return


# 行类型芯片 画标注框
# ImagePath 给定的原始图片路径
# TxtPath 给定有关尺寸大小，间距的txt文件路径
# CustomerGiveCoordinate 用户在图上标定的限定区域的位置
# DrawBoxOfChip规定所标注的图片框位置是处于上端还是下端 可选参数'Above' 和 'Below'
def CreateLabelBoxLine(OriginImagePath, TxtPath,ChipPosLeftDown,ChipPosRightDown,
                       curmacro_pos,DrawBoxOfChip='Above'):
    '''根据标注框和txt文本信息自动生成选定标注图片'''
    # ModelImage = Image.open(MarkImagePath)
    # 这部分暂时不加 先独立调试之后的程序
    # CustomerGiveCoordinateLeftUp = CustomerGiveCoordinate[0]
    #
    # '''还缺少根据用户标定的框，对原图进行裁剪，这里识别的是裁剪之后的图片'''
    # CornerInMarkBox = corner_detection('CornerTest/t13.jpg', 1)
    # if not CornerInMarkBox:
    #     return 'RedrawTheBox'
    # else:
    #     print('Find corner in mark area', CornerInMarkBox)
    # CornerInMarkBoxLeft = CornerInMarkBox[0]
    # CornerInMarkBoxRight = CornerInMarkBox[1]
    # ChipPosLeftDown = (CornerInMarkBoxLeft[0] + CustomerGiveCoordinateLeftUp[0],
    #                    CornerInMarkBoxLeft[1] + CustomerGiveCoordinateLeftUp[1])
    # ChipPosRightDown = (CornerInMarkBoxRight[0] + CustomerGiveCoordinateLeftUp[0],
    #                     CornerInMarkBoxRight[1] + CustomerGiveCoordinateLeftUp[1])
    # ChipImagew = ChipPosRightDown[0] - ChipPosLeftDown[0]

    # 假设芯片位置以及宽度已经给定
    # 最后获得了芯片在图像上的宽 以及芯片在图像上的位置
    # 芯片左边角和右边角位于图上的像素位置



    # 以下是一些需要传入的参数
    '''第二行中间处芯片的位置'''
    # ChipPosLeftDown = (753, 905)
    # ChipPosRightDown = (943, 905)


    '''第一行芯片的位置'''
    # ChipPosLeftDown = (753, 302)
    # ChipPosRightDown = (943, 302)


    ChipImagew = ChipPosRightDown[0] - ChipPosLeftDown[0]

    ParaDataDict = ReadSpecialLineFromTxtFile(TxtPath)
    # print('txt中参数', ParaDataDict)

    # 当前芯片的两个位置参数 分别是当前芯片所细分到组别中的位置
    # 这个参数不知道怎么传进来的
    '''这里直接是传入的当前芯片的位置'''
    # curmacro_pos = (1,3)

    # 获取原始图片位置
    '''在这里的filepath是写死了，固定在一个位置因此改为直接获取'''
    # ChipImagePath=GetOriginImageFromStrList(ParaDataList) # 如'middle.jpg'
    OriginImage = Image.open(OriginImagePath)


    '''因为之后只采用单画一个芯片，然后直接画一行的操作，这里想的方法是画微观中间的一个，然后把宏观的
    其他组都画出来，需要考虑组与组之间的间隙'''

    # 获取芯片的名字
    ChipName=ParaDataDict.get('ChipName')
    # 获取芯片 实际间距 实际宽高
    ChipRealitywh = (ParaDataDict.get('RealChipWidth'), ParaDataDict.get('RealChipHeight'))
    # 比例尺=图像上的像素值/实际长度 这里需要把长宽求一个平均
    proportion = ChipImagew / ChipRealitywh[0]
    if ParaDataDict.get('ifNest'):
        ChipRealIntervalwh = (ParaDataDict.get('RealIntervalw'), ParaDataDict.get('RealIntervalh'))
        ChipImageIntervalwh = (AccordingProporCalcPiexl(ChipRealIntervalwh[0], proportion),
                               AccordingProporCalcPiexl(ChipRealIntervalwh[1], proportion))
        ChipRealIntervalwhHuge = (ParaDataDict.get('RealIntervalwHuge'),
                                  ParaDataDict.get('RealIntervalhHuge'))
        ChipImageIntervalwhHuge = (AccordingProporCalcPiexl(ChipRealIntervalwhHuge[0], proportion),
                                   AccordingProporCalcPiexl(ChipRealIntervalwhHuge[1], proportion))
    else:
        ChipRealIntervalwh = (ParaDataDict.get('RealIntervalw'), ParaDataDict.get('RealIntervalh'))
        ChipImageIntervalwh = (AccordingProporCalcPiexl(ChipRealIntervalwh[0], proportion),
                               AccordingProporCalcPiexl(ChipRealIntervalwh[1], proportion))
        ChipRealIntervalwhHuge = (0, 0)
        ChipImageIntervalwhHuge = (0, 0)
    ChipImagewh = (AccordingProporCalcPiexl(ChipRealitywh[0], proportion),
                   AccordingProporCalcPiexl(ChipRealitywh[1], proportion))

    #先判断字典是否已经存在，如果存在，则更新字典，不存在则新建一个字典
    foldname = 'CustomerDefineModel'
    DictPath = foldname + '/' + ChipName+'.pickle'
    if os.path.exists(DictPath):
        # 载入字典
        with open(DictPath, 'rb')as Dict_File_Open:
            ChipPosDict = pickle.load(Dict_File_Open)
    else:
        # 阵列矩阵的类型 是2x5  2行5列 还是 4x4   以及所标示的芯片所处的位置
        if ParaDataDict.get('ifNest'):
            ChipArray = numxnum2tuple(ParaDataDict.get('Format'))
            ChipArrayMicro = numxnum2tuple(ParaDataDict.get('FormatMicro'))
            ChipPosDict = {'Format': (str(ChipArray[0]) + 'x' + str(ChipArray[1])),
                           'FormatMicro': (str(ChipArrayMicro[0]) + 'x' + str(ChipArrayMicro[1])),
                           'Proportion':proportion,
                           'ChipSize': ChipImagewh,
                           'ChipImagePath':OriginImagePath,
                           'Intervalwh':ChipImageIntervalwh,
                           'IntervalwhHuge':ChipImageIntervalwhHuge}
        else:
            ChipArray = numxnum2tuple(ParaDataDict.get('Format'))
            PosInArrayMicro = (0, 0)
            ChipPosDict = {'Format': (str(ChipArray[0]) + 'x' + str(ChipArray[1])),
                           'FormatMicro': (0, 0),  # 若出现0 一般都不正常
                           'Proportion': proportion,
                           'ChipSize': ChipImagewh,
                           'ChipImagePath':OriginImagePath,
                           'Intervalwh': ChipImageIntervalwh,
                           'IntervalwhHuge': ChipImageIntervalwhHuge}
    # 加入一些两个字典都需要的参数
    ChipPosDict['CurrentPos']=curmacro_pos
    ChipPosDict['WhiteBorder']=5
    PosInArray = curmacro_pos

    # 行扫描
    if ParaDataDict.get('ifNest'):
        ChipArray=numxnum2tuple(ChipPosDict.get('Format'))
        ChipArrayMicro=numxnum2tuple(ChipPosDict.get('FormatMicro'))
        '''这个地方对于处于中间位置的芯片，到底是使用1x12 还是 使用两个坐标的形式
        给定坐标形式：大组4*3 小组1*9 给定位置坐标 1*14 或者2*14'''
        for j in range(ChipArray[1] * ChipArrayMicro[1]):
            ChipCurPixel = AccordRowColIntervalGetPixelPos_Nest((PosInArray[0], j + 1),PosInArray,
                                                                ChipImageIntervalwh,
                                                                ChipImageIntervalwhHuge,
                                                                ChipImagewh,ChipPosLeftDown,
                                                                ChipArray, ChipArrayMicro,)
            if DrawBoxOfChip == 'Below':
                ChipCurPixel = LeftDown2LeftUpPos(ChipCurPixel, ChipImagewh)
            WriteToDict((PosInArray[0] , j + 1), ChipPosDict, ChipCurPixel)

    else:
        ChipArray = numxnum2tuple(ChipPosDict.get('Format'))
        for j in range(ChipArray[1]):
            ChipCurPixel = AccordRowColIntervalGetPixelPos((PosInArray[0] , j + 1), PosInArray,
                                                           ChipImageIntervalwh,
                                                           ChipImagewh, ChipPosLeftDown)
            if DrawBoxOfChip=='Below':
                ChipCurPixel = LeftDown2LeftUpPos(ChipCurPixel, ChipImagewh)
            WriteToDict((PosInArray[0] , j + 1), ChipPosDict, ChipCurPixel)


    '''下面可以选择是否合并字典'''
    ChipPosDict=DictMergeAtoB(dictA=ParaDataDict,dictB=ChipPosDict)
    print('芯片位置信息字典', ChipPosDict)

    if ParaDataDict.get('ifNest'):
        img = DrawLineToShowNest(OriginImage, ChipPosDict, CurLine=PosInArray[0])
    else:
        img=DrawLineToShow(OriginImage,ChipPosDict,CurLine=PosInArray[0])
    img.show()
    '''对应字典需要保存'''
    CustDefineDictSave(ChipPosDict, ChipName=ChipName+'Tmp')


# 此函数如果遇到一些错误
# 需要一些对应的错误返回值


# 从字符串列表中获取图片名
def GetOriginImageFromStrList(list):
    for i in list:
        tmp = i.strip()
        if ('filepath' in tmp) or ('FilePath' in tmp):
            filepath = tmp.split('&')[-1]
            return filepath
    return None


# 从字符串列表中获取间距值
def GetIntervalwhFromStrList(list):
    for i in list:
        tmp = i.strip()
        if ('IntervalWidth' in tmp) or ('intervalwidth' in tmp):
            width = tmp.split('&')[-1]
            width = StrNum2RealNum(width)
    for i in list:
        tmp = i.strip()
        if ('IntervalHeight' in tmp) or ('intervalheight' in tmp):
            height = tmp.split('&')[-1]
            height = StrNum2RealNum(height)
            return (width, height)
    return None


# 从字符串列表中获取芯片实际宽高
def GetRealitywhFromStrList(list):
    for i in list:
        tmp = i.strip()
        if ('RealityWidth' in tmp) or ('realitywidth' in tmp):
            width = tmp.split('&')[-1]
            width = StrNum2RealNum(width)
    for i in list:
        tmp = i.strip()
        if ('RealityHeight' in tmp) or ('realityheight' in tmp):
            height = tmp.split('&')[-1]
            height = StrNum2RealNum(height)
    # 如果有对应的值则返回
    if width and height:
        return (width, height)
    return None


# 计算芯片和对应像素之间的比例尺
# 输入真实长度reallen  比例尺=图像上的像素值/实际长度proportion
# 返回整数类型的像素值 四舍五入方法
def AccordingProporCalcPiexl(reallen, proportion):
    result = round(reallen * proportion)
    return result


# 将字符串类型的数据转化为 实数类型
# 参数type可选择float类型或者int类型
def StrNum2RealNum(strnum, type='float'):
    result = float(strnum)
    if type == 'float':
        return result
    elif type == 'int':
        return round(result)


# 从字符串列表中获取芯片矩阵格式 如是2x5还是 4x4
# 返回类型 元组类型如(2,5)  (4,4)
def GetChipArrayFromStrList(list):
    for i in list:
        tmp = i.strip()
        if ('Array' in tmp) or ('Matrix' in tmp):
            arraystr = tmp.split('&')[-1]
            array = tuple(map(int, arraystr.split('x')))
            return array
    return None


#  从字符串列表中获取芯片所处在矩阵中的位置 比如 1x2
# 表示划款的芯片处于芯片阵列中的一行二列
def GetChipPosInArrayFromStrList(list):
    for i in list:
        tmp = i.strip()
        if ('PosInArray' in tmp) or ('PosInMatrix' in tmp):
            arraystr = tmp.split('&')[-1]
            array = tuple(map(int, arraystr.split('x')))
            return array
    return None



# 在图片上将芯片画出以示标注
def DrawLineToShow(img, PosDict,CurLine, LineWidth=8):
    ChipSize = PosDict.get('ChipSize')
    maxrow, maxcol = PosDict.get('Format').split('x')
    # maxrow = int(maxrow)
    maxcol = int(maxcol)

    draw = ImageDraw.Draw(img)
    LineColor = GetLineColor(img.mode)

    # for row in range(1, maxrow + 1):
    for col in range(1, maxcol + 1):
        PosStr = str(CurLine) + '_' + str(col)
        ChipTopLeftCorner = PosDict.get(PosStr)
        draw.line([tuple(ChipTopLeftCorner),
                   (ChipTopLeftCorner[0] + ChipSize[0], ChipTopLeftCorner[1]),
                   (ChipTopLeftCorner[0] + ChipSize[0], ChipTopLeftCorner[1] + ChipSize[1]),
                   (ChipTopLeftCorner[0], ChipTopLeftCorner[1] + ChipSize[1]),
                   tuple(ChipTopLeftCorner)],
                  fill=LineColor, width=LineWidth)
    return img



# 在图片上将芯片画出以示标注  此函数与之前类似 不过是有嵌套的部分
def DrawLineToShowNest(img, PosDict, CurLine,LineWidth=8):
    ChipSize = PosDict.get('ChipSize')
    maxrow, maxcol = PosDict.get('Format').split('x')
    maxrowMicro,maxcolMicro=PosDict.get('FormatMicro').split('x')
    maxcol = int(maxcol)
    maxcolMicro=int(maxcolMicro)

    draw = ImageDraw.Draw(img)
    LineColor = GetLineColor(img.mode)


    for col in range(1, maxcol*maxcolMicro + 1):
        PosStr = str(CurLine) + '_' + str(col)
        ChipTopLeftCorner = PosDict.get(PosStr)
        draw.line([tuple(ChipTopLeftCorner),
                   (ChipTopLeftCorner[0] + ChipSize[0], ChipTopLeftCorner[1]),
                   (ChipTopLeftCorner[0] + ChipSize[0], ChipTopLeftCorner[1] + ChipSize[1]),
                   (ChipTopLeftCorner[0], ChipTopLeftCorner[1] + ChipSize[1]),
                   tuple(ChipTopLeftCorner)],
                  fill=LineColor, width=LineWidth)
    return img


# 根据输入的对应芯片矩阵行列数 以及间距 求芯片对应像素坐标
# 参数DrawBoxOfChip 表示用户标注的框是标注芯片的下方还是芯片的上方，这会影响之后是
# 朝上方还是下方画标注框 可选参数 'Below' 'Top'

def AccordRowColIntervalGetPixelPos(CurPosInArray, MarkPosInArray, Intervalwh, ChipImagewh,
                                    ChipLeftUpPixel, DrawBoxOfChip='Below'):
    '''在这里需要统一一下传入的参数：
    对于标定芯片位置，皆采用一个角点坐标外加芯片Size的形式
    如果这里的DrawBoxOfChip==Below 那么这里的芯片脚坐标就为左下角，需要注意返回值也为左下角坐标，
    Size为正常尺寸不变
    如果这里的DrawBoxOfChip==Top  那么这里芯片的脚坐标就为左上角，需要注意返回值也为右下角坐标，
    Size大小为正常尺寸不变'''
    if DrawBoxOfChip == 'Below':
        ShiftingPixelY = (CurPosInArray[0] - MarkPosInArray[0]) * (Intervalwh[1] + ChipImagewh[1])
        ShiftingPixelX = (CurPosInArray[1] - MarkPosInArray[1]) * (Intervalwh[0] + ChipImagewh[0])
        CurPosPixel = (ChipLeftUpPixel[0] + ShiftingPixelX, ChipLeftUpPixel[1] + ShiftingPixelY)
    elif DrawBoxOfChip == 'Top':
        ShiftingPixelY = (CurPosInArray[0] - MarkPosInArray[0]) * (Intervalwh[1] + ChipImagewh[1])
        ShiftingPixelX = (CurPosInArray[1] - MarkPosInArray[1]) * (Intervalwh[0] + ChipImagewh[0])
        CurPosPixel = (ChipLeftUpPixel[0] + ShiftingPixelX, ChipLeftUpPixel[1] + ShiftingPixelY)
    return CurPosPixel


#   此函数和上面的函数作用差不多，只不过此函数是应对嵌套类型的芯片 因为在此只使用行画框，因此多两个参数Format，
#   FormatMicro
def AccordRowColIntervalGetPixelPos_Nest(CurPosInArray, MarkPosInArray, Intervalwh, IntervalwhHuge,
                                         ChipImagewh, ChipLeftUpPixel, Format, FormatMicro,
                                         DrawBoxOfChip='Below'):
    # 构造辅助list
    AssistList = []
    for i in range(Format[1]):
        # 构造出的list形式[[1,9],[10,18],[19,27]]
        AssistList.append([i * FormatMicro[1] + 1, (i + 1) * FormatMicro[1]])
    MacroCurNum = 0
    for i in AssistList:
        MacroCurNum += 1
        if CurPosInArray[1] >= i[0] and CurPosInArray[1] <= i[1]:
            break
    MacroMarkNum = 0
    for i in AssistList:
        MacroMarkNum += 1
        if MarkPosInArray[1] >= i[0] and MarkPosInArray[1] <= i[1]:
            break
    # 计算X方向上Shift
    ShiftingPixelX = (CurPosInArray[1] - MarkPosInArray[1]) * (Intervalwh[0] + ChipImagewh[0]) + (
                (MacroCurNum - MacroMarkNum) * (IntervalwhHuge[0] - Intervalwh[0]) )

    ShiftingPixelY = 0
    CurPosPixel = (ChipLeftUpPixel[0] + ShiftingPixelX, ChipLeftUpPixel[1] + ShiftingPixelY)
    return CurPosPixel

# 根据左下方坐标以及芯片大小 得到左上方坐标
def LeftDown2LeftUpPos(LeftDownPixel, ChipSize):
    return (LeftDownPixel[0], LeftDownPixel[1] - ChipSize[1])


# 根据左上方坐标以及芯片大小 得到左下方坐标
def LeftUp2LeftDownPos(LeftUpPixel, ChipSize):
    return (LeftUpPixel[0], LeftUpPixel[1] + ChipSize[1])


# 每次调用这个函数，对应行列矩阵的芯片 将其坐标写入字典中
def WriteToDict(CurPosInArray, Dict, CurPixel):
    PosStr = str(CurPosInArray[0]) + '_' + str(CurPosInArray[1])
    Dict[PosStr] = CurPixel


# 根据传入图像的格式获取对应的线条颜色 便于绘图
def GetLineColor(img_mode):
    if img_mode == 'RGB':
        return (255, 0, 0)
    elif img_mode == 'L':
        # 纯黑填充
        return (0,)
    else:
        return (0,)


def CustDefineDictSave(Dict, ChipName):
    foldername = 'CustomerDefineModel'
    if not os.path.exists(foldername):
        os.makedirs(foldername)
    Config_File_Name = foldername + '/' + ChipName + '.pickle'
    with open(Config_File_Name, 'wb') as Config_File_Save:
        pickle.dump(Dict, Config_File_Save)



'''注意这里的Below的含义是 标注的框位于芯片的位置，是标注的芯片下端还是，对应第一行
对应的Above表示的是标注的是芯片的上半部分，对应第二行'''
# 边角检测函数 img_name为图片文件路径
# flag_location为标注框 是标注芯片的上半部分还是下半部分
# 如果标注下半部分，也就是上排芯片MarkLocOfChip='Below'
# 如果标注上半部分，也就是下排芯片MarkLocOfChip='Above'
def corner_detection(img_name, MarkLocOfChip):
    img = cv2.imread(img_name, cv2.IMREAD_GRAYSCALE)
    if img.any:
        dst = cv2.cornerHarris(img, 2, 3, 0.04)
        R = dst > 0.1 * dst.max()  # shape得到的是（y,x）
        x_end = R.shape[1] // 5
        x_start = (R.shape[1] // 5) * 4
        y_end = R.shape[0] // 3
        y_start = (R.shape[0] // 3) * 2
        # print(x_end)
        # print(x_start)
        coordinate_x_1 = []  # 储存得到的点用
        coordinate_y_1 = []
        coordinate_x_2 = []
        coordinate_y_2 = []
        final_left = []  # 最终得到的左边坐标
        final_right = []  # 最终得到的右边坐标
        '''--- 获得左边区域点---'''
        for i in range(0, x_end):  # j是纵长度，i是横长度
            for j in range(y_end, y_start):
                if R[j][i] == True:
                    coordinate_x_1.append(i)
                    coordinate_y_1.append(j)
        coordinate_x_1 = sorted(coordinate_x_1)
        coordinate_y_1 = sorted(coordinate_y_1)

        '''--- 获得右边区域点---'''
        for i in range(x_start, R.shape[1]):  # j是纵长度，i是横长度
            for j in range(y_end, y_start):
                if R[j][i] == True:
                    coordinate_x_2.append(i)
                    coordinate_y_2.append(j)
        coordinate_x_2 = sorted(coordinate_x_2)
        coordinate_y_2 = sorted(coordinate_y_2)
        # print('参数：' + '\n', coordinate_x_1, '\n', coordinate_y_1, '\n', coordinate_x_2, '\n',
        #       coordinate_y_2, '\n')
        '''---两种取角点方式，以flag_location区分---'''
        if MarkLocOfChip == 'Below':
            if not (coordinate_x_1 and coordinate_y_1 and coordinate_x_2 and coordinate_y_2):
                print('有未检测到角点区域，请重新取图！')
            else:
                # 皆选择取最大值最小值的方法
                '''---得到左边x坐标---'''
                tmp = min(coordinate_x_1)
                final_left.append(tmp)
                '''---得到左边y坐标---'''
                tmp = max(coordinate_y_1)
                final_left.append(tmp)
                '''---得到右边x坐标---'''
                tmp = max(coordinate_x_2)
                final_right.append(tmp)
                '''---得到右边y坐标---'''
                tmp = max(coordinate_y_2)
                final_right.append(tmp)
                '''---合并参数---'''
                print('结果：', final_left, final_right)
                
        elif MarkLocOfChip == 'Above':
            if not (coordinate_x_1 and coordinate_y_1 and coordinate_x_2 and coordinate_y_2):
                print('有未检测到角点区域，请重新取图！')
            else:
                # 皆适用取得极大值极小值的方式
                '''---得到左边x坐标---'''
                tmp = min(coordinate_x_1)
                final_left.append(tmp)
                '''---得到左边y坐标---'''
                tmp = min(coordinate_y_1)
                final_left.append(tmp)
                '''---得到右边x坐标---'''
                tmp = max(coordinate_x_2)
                final_right.append(tmp)
                '''---得到右边y坐标---'''
                tmp = min(coordinate_y_2)
                final_right.append(tmp)
                '''---合并参数---'''
                print('结果：', final_left, final_right)
        else:
            print('没有这个图像！')

    return (final_left, final_right)


# 根据给定文件名读取txt文件
# 因为txt文件需要读取的部分在txt中固定的行数位置，所以这里在程序中写死了 (测试中直接从第五行读取文件)
def ReadSpecialLineFromTxtFile(txtpath):
    linenum = 0
    FirstLine = 5
    LastLine = 8
    DistanceParaStrList = []
    with open(txtpath) as file:
        for line in file:
            linenum += 1
            if (linenum >= FirstLine) and (linenum <= LastLine):
                DistanceParaStrList.append(line.strip())
            if linenum > LastLine:
                break
    # print('txt读取到的文档内容',DistanceParaStrList)
    # # 芯片矩阵的维度字符串
    # DimensionStrList = DistanceParaStrList[0].split(' ')
    # # 间距字符串
    # IntervalStrList = DistanceParaStrList[1].split(' ')
    # # 芯片长宽字符串
    # ChipwhStrList = DistanceParaStrList[2].split(' ')
    #
    # ReturnDict = {}
    # # 判断嵌套形式是否嵌套
    # if int(DimensionStrList[1].split('&')[-1].split('x')[-1]) > 1:
    #     ReturnDict['ifNest'] = True
    # else:
    #     ReturnDict['ifNest'] = False
    # # 将内容写入字典
    # BatchWriteToDictFromStrList(ReturnDict, DimensionStrList)
    # BatchWriteToDictFromStrList(ReturnDict, IntervalStrList)
    # BatchWriteToDictFromStrList(ReturnDict, ChipwhStrList)

    # 换一种方法写
    ReturnDict={}
    # 不使用split(' ')即表示删除空格换行之类的空字符
    DimensionStrList=DistanceParaStrList[0].split()
    if int(DimensionStrList[1].split('&')[-1].split('x')[-1]) > 1:
        ReturnDict['ifNest'] = True
    else:
        ReturnDict['ifNest'] = False
    for i in DistanceParaStrList:
        BatchWriteToDictFromStrList(ReturnDict,i.split())
    return ReturnDict



'''
result=dict(dict1,**dict2)
此种做法 对于两个字典中重合的部分，相同的key，在这里任务dict2的优先级高
即dict1重合的内容会被dict2覆盖
'''


# 将list列表中的数据批量写入dict字典中
# list形式如 ['row&4', 'col&3', 'nest_row&1', 'nest_col&9']
def BatchWriteToDictFromStrList(dict, list):
    for para in list:
        # 如果是矩阵维度
        if ('x' in para.split('&')[-1]) or ('ChipName' in para.split('&')[0]):
            dict[para.split('&')[0]] = para.split('&')[-1]
        elif type(eval(para.split('&')[-1])) == float:
            dict[para.split('&')[0]] = float(para.split('&')[-1])
        elif type(eval(para.split('&')[-1])) == int:
            dict[para.split('&')[0]] = int(para.split('&')[-1])

        else:
            print('Not a int or float or string type')
            return
    return


# 把 '4x4' 字符串变为元组(4,4)
def numxnum2tuple(ArrayStr):
    returntuple = (int(ArrayStr.split('x')[0]), int(ArrayStr.split('x')[1]))
    return returntuple


# 两个字典的合并，重复的部分，B中的内容会被A的部分覆盖掉
def DictMergeAtoB(dictA, dictB):
    dictB = dict(dictB, **dictA)
    return dictB

if __name__ == '__main__':
    CreateLabelBoxLine(OriginImagePath='TestAbove.jpg',
                       TxtPath='ChipInfo.txt', ChipPosLeftDown=None,
                       ChipPosRightDown=None,curmacro_pos=None,
                       DrawBoxOfChip='Above')
    # ReadSpecialLineFromTxtFile('ChipInfo.txt')
    # print(numxnum2tuple('4x4'))

    '''剩下的还有改变为从字典中读取的方式，以及检测的时候带上使用嵌套检测'''
