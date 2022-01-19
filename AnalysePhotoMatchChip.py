#!/usr/bin/env python
# coding=utf-8
__author__ = 'Jia Liangjun'
# *******************************************************************
#     Filename @  MatchChips.py
#       Author @  Jia Liangjun
#  Create date @  2019/1/10 9:56
#        Email @  LJjiahf@163.com
#  Description @  依据给定的模型对比芯片是否残缺
# ********************************************************************


import numpy as np
from PIL import Image, ImageDraw
import os
import pickle
import scipy.io as sio

# 单个芯片最佳范围 宽 295 高272
BestSize = (290, 275)
SquareSize = (290, 275)
LikeRatio = 0.95

# 字典格式存储文件 模版信息文件
# 字典格式： 第几行第几列芯片:芯片 左上 角的绝对像素值(x,y)
# 字典中参数的解释 Name：此芯片名称 Format 每张图片中待识别芯片的行列书，此数值与之后的芯片列表对应
# ChipSize 每个芯片所占用的绝对像素值大小，
# WhiteNum 如果采用留白方法，那么其中每个识别框中白色像素点出现的个数 BoxArea识别框的面积，其值为ChipSize的乘积
# WhiteBorder 白色边框的像素值宽度
'''是否可以使用留白Box的乘积呢？'''
# Position_Matrix = {'Name': '5', 'Format': '4x4', 'ChipSize': (290, 270), 'WhiteNum': 2700,
#                    'BoxArea': 78300, 'WhiteBorder': 40,
#                    '1_1': [357, 100], '1_2': [802, 96], '1_3': [1248, 96], '1_4': [1692, 98],
#                    '2_1': [355, 551], '2_2': [802, 548], '2_3': [1248, 546], '2_4': [1694, 545],
#                    '3_1': [355, 1003], '3_2': [802, 1001], '3_3': [1249, 998], '3_4': [1696, 995],
#                    '4_1': [364, 1458], '4_2': [804, 1455], '4_3': [1249, 1451], '4_4': [1696, 1448],
#                    }

# 两种字典 分为非嵌套组 以及嵌套组
# Position_Matrix = {'Name': '5', 'Format': '4x4', 'ChipSize': (305, 285), 'BlackNum': 68000,
#                    'WhiteBorder': 10,
#                    '1_1': [357, 100], '1_2': [802, 96], '1_3': [1248, 96], '1_4': [1692, 98],
#                    '2_1': [355, 551], '2_2': [802, 548], '2_3': [1248, 546], '2_4': [1694, 545],
#                    '3_1': [355, 1003], '3_2': [802, 1001], '3_3': [1249, 998], '3_4': [1696, 995],
#                    '4_1': [364, 1458], '4_2': [804, 1455], '4_3': [1249, 1451], '4_4': [1696, 1448],
#                    }

Position_Matrix = {'Format': '5x3', 'FormatMicro': '1x12', 'Proportion': 1.0, 'ChipSize': (38, 62),
                   'WhiteBorder': 5, 'BlackNum': 1200, 'ifNest': True,
                   '1_1': (145, 200), '1_2': (202, 200), '1_3': (259, 200), '1_4': (316, 200),
                   '1_5': (373, 200), '1_6': (430, 200), '1_7': (487, 200), '1_8': (544, 200),
                   '1_9': (601, 200), '1_10': (658, 200), '1_11': (715, 200), '1_12': (772, 200),
                   '1_13': (943, 200), '1_14': (1000, 200), '1_15': (1057, 200), '1_16': (1114, 200),
                   '1_17': (1171, 200), '1_18': (1228, 200), '1_19': (1285, 200), '1_20': (1342, 200),
                   '1_21': (1399, 200), '1_22': (1456, 200), '1_23': (1513, 200), '1_24': (1570, 200),
                   '1_25': (1741, 200), '1_26': (1798, 200), '1_27': (1855, 200), '1_28': (1912, 200),
                   '1_29': (1969, 200), '1_30': (2026, 200), '1_31': (2083, 200), '1_32': (2140, 200),
                   '1_33': (2197, 200), '1_34': (2254, 200), '1_35': (2311, 200), '1_36': (2368, 200)}
Position_Matrix = {'Format': '2x5', 'FormatMicro': '1x1', 'Proportion': 1.0, 'ChipSize': (190, 293),
                   'ChipImagePath': 'TestAbove.bmp', 'Intervalwh': (26, 0), 'IntervalwhHuge': (0, 0),
                   'CurrentPos': (2, 3), 'WhiteBorder': 5,
                   '1_1': (321, 9), '1_2': (537, 9), '1_3': (753, 9), '1_4': (969, 9),
                   '1_5': (1185, 9), 'ifNest': False, 'RealIntervalw': 26, 'RealIntervalh': 0,
                   'RealIntervalwHuge': 0, 'RealIntervalhHuge': 0, 'RealChipHeight': 293,
                   'RealChipWidth': 190, 'ChipName': 'CustomerDefine5', 'BlackNum1_1': 52216,
                   'BlackNum1_2': 52884, 'BlackNum1_3': 52667, 'BlackNum1_4': 53137, 'BlackNum1_5': 54136,
                   '2_1': (324, 905), '2_2': (539, 905), '2_3': (754, 905),
                   '2_4': (969, 905), '2_5': (1184, 905), 'BlackNum2_1': 53266, 'BlackNum2_2': 52994,
                   'BlackNum2_3': 53226, 'BlackNum2_4': 53532, 'BlackNum2_5': 54211}

ChipSize_tmp = Position_Matrix.get('ChipSize')
WhiteBorder_tmp = Position_Matrix.get('WhiteBorder')
WhiteBorderBoxArea_tmp = (ChipSize_tmp[0] + WhiteBorder_tmp) * (ChipSize_tmp[1] + WhiteBorder_tmp)
# 计算两种BoxArea的值并写入字典中
Position_Matrix['BoxArea'] = ChipSize_tmp[0] * ChipSize_tmp[1]
Position_Matrix['WhiteBorderBoxArea'] = WhiteBorderBoxArea_tmp


# 得到阵列名称  输入变量 行 列(整数类型)
def GetArrayName(row, col):
    return str(row) + '_' + str(col)


# 获取列表l中每个元素加上num 返回
# 结果
# 要求 输入列表l 全部为实数 输入num为实数
def ListPlus(l1, l2):
    newlist = []
    length = len(l1)
    if length != len(l2):
        return
    for i in range(length):
        newlist.append(l1[i] + l2[i])
    return newlist


# 获取下一个x,y 坐标
# 输入 当前j,i 坐标 整体图片宽高  需要匹配的图片宽高
# 从左向右扫描 扫描完扫描下一行
def GetNextPos(CurPos, MatchSize, ImageSize):
    i = CurPos[1]
    j = CurPos[0]
    j += 2
    # 从左到右是否扫描完
    if j + MatchSize[0] > ImageSize[0]:
        j = 0
        i += 2
        print('line', i)
    # 是否所有行全都扫描 溢出了
    if i + MatchSize[0] > ImageSize[0]:
        return None, None
    return j, i


# 使用举矩形获取目标位置上下角中心位置
# 输入 图像的numpy矩阵 ( , )正方形大小
# 返回 数组用于表示表示左上 右下角位置
def SquareMeasurePosition(ImageArray, SizeOfSquare):
    PositionTxt = open('图片结果.txt', 'w')
    PositionList = []
    # 初始化全黑数组
    BlackSquare = np.zeros((SizeOfSquare[1], SizeOfSquare[0]), dtype=np.int8)
    height, width = np.shape(ImageArray)
    # 从(0,0)开始扫描 i,SizeOfSquare[1]表示行数 高度  j,SizeOfSquare[0]表示列数 宽度
    i = 0
    j = 0  # 因为之后j会+1 从第一个开始找

    # print(ResultSquare)
    while True:
        j, i = GetNextPos((j, i), SizeOfSquare, (height, width))
        ResultSquare = ImageArray[i:i + SizeOfSquare[1], j:j + SizeOfSquare[0]] - BlackSquare
        SumResultSquare = np.sum(ResultSquare)
        while SumResultSquare > SizeOfSquare[0] * SizeOfSquare[1] * (1 - LikeRatio):
            j, i = GetNextPos((j, i), SizeOfSquare, (height, width))
            if not i and not j:  # i=0 且 j=0
                return PositionList
            try:
                ResultSquare = ImageArray[i:i + SizeOfSquare[1], j:j + SizeOfSquare[0]] - BlackSquare
            except Exception as e:
                print('Error', i, j)
            SumResultSquare = np.sum(ResultSquare)
            # if j + SizeOfSquare[1] == w:
            #     i += 1
            #     j = 0
            #     if i + SizeOfSquare[1] > h:
            #         return PositionList
        print('发现位置坐标', (j, i))
        print('发现位置坐标', (j, i), file=PositionTxt)
        PositionList.append((j, i))
        # print('xy坐标', j, i)
        # print('区域矩阵', ResultSquare)
        # print('区域求和值', SumResultSquare)
        # return [j, i]


# 根据给定的 Chip大小 ChipSize 和位置字典 PosDict 来判断芯片缺损状态
# 输入 np数组类型的 ImgArray  元组ChipSize 字典类型PosDict 相似度similarity
# 返回值 返回有问题的芯片位置坐标 如果没问题 则返回[]
# 举例 芯片出现问题 返回['1_1','1_2','2_2']
def CompareModel(ImageArray, PosDict=Position_Matrix, similarity=0.95):
    ReturnList = []
    ChipSize = PosDict.get('ChipSize')
    maxcol, maxrow = PosDict.get('Format').split('x')
    maxrow = int(maxrow)
    maxcol = int(maxcol)
    # 自己构造一个全黑的矩阵
    BlackSquare = np.zeros((ChipSize[1], ChipSize[0]), dtype=np.int8)
    for row in range(1, maxrow + 1):
        for col in range(1, maxcol + 1):
            PosStr = str(row) + '_' + str(col)
            LeftUpperPos = PosDict.get(PosStr)
            # 原图中的矩形
            OriginRectangle = ImageArray[LeftUpperPos[1]:LeftUpperPos[1] + ChipSize[1],
                              LeftUpperPos[0]:LeftUpperPos[0] + ChipSize[0]]
            print('原图中白色像素点个数', np.sum(OriginRectangle))
            # 两者相减获得的结果矩阵
            ResultSquare = OriginRectangle - BlackSquare
            SumResultSquare = np.sum(ResultSquare)
            if SumResultSquare > ChipSize[0] * ChipSize[1] * (1 - similarity):
                ReturnList.append(PosStr)

    return ReturnList


# 此函数类似于一开始的CompareModel函数
# 但是使用留白的方法，这次划框使用的直接是一个黑色的芯片，外加外部的一定像素宽度的白色边框，
# 每次对比选定区域中黑色像素点的个数，一般来说黑色像素点只会少不会多，
# 这样就可以应对人为标定区域中芯片位置出现平移或者旋转
def CompareModelWithWhiteBorder(ImageArray, PosDict=Position_Matrix, similarity=0.1):
    ReturnList = []
    maxrow, maxcol = PosDict.get('Format').split('x')
    maxrow = int(maxrow)
    maxcol = int(maxcol)
    if PosDict.get('ifNest'):
        maxrowMicro, maxcolMicro = PosDict.get('FormatMicro').split('x')
        maxrowMicro = int(maxrowMicro)
        maxcolMicro = int(maxcolMicro)
    else:
        maxrowMicro = 1
        maxcolMicro = 1
    # print('maxcol', maxcolMicro, maxcol)
    # 获得希望的每个框中白色像素点的个数以及留白像素值
    # BlackNum = PosDict.get('BlackNum')
    WhiteBorder = PosDict.get('WhiteBorder')
    ChipSize = PosDict.get('ChipSize')
    # ChipSize = (ChipSize[0] + 2 * WhiteBorder, ChipSize[1] + 2 * WhiteBorder)
    # 芯片面积的像素值
    BoxArea = PosDict.get('BoxArea')

    '''这里需要判断最左上方边框是否在图像内（即不存在负值），可以通过掷出错误的形式'''
    LeftUpperPos = PosDict.get('1_1')
    if LeftUpperPos[0] - WhiteBorder < 0 or LeftUpperPos[1] - WhiteBorder < 0:
        print('留白太多')
        return
    # 逐行逐列根据模版扫描芯片
    for row in range(1, maxrow * maxrowMicro + 1):
        '''先测试一行'''
        # if row!=1:
        #     continue
        for col in range(1, maxcol * maxcolMicro + 1):
            PosStr = str(row) + '_' + str(col)
            LeftUpperPos = PosDict.get(PosStr)
            LeftUpperPos = (LeftUpperPos[0] - WhiteBorder, LeftUpperPos[1] - WhiteBorder)
            # 待检测中的矩形
            '''此矩形是含有白色边框的矩形'''
            TestRectangle = ImageArray[LeftUpperPos[1]:LeftUpperPos[1] + ChipSize[1] + 2 * WhiteBorder,
                            LeftUpperPos[0]:LeftUpperPos[0] + ChipSize[0] + 2 * WhiteBorder]
            # print('位置', [LeftUpperPos[0], LeftUpperPos[1],
            #              LeftUpperPos[0] + ChipSize[0] + 2 * WhiteBorder,
            #              LeftUpperPos[1] + ChipSize[1] + 2 * WhiteBorder])
            # 一些调试可能用到的语句
            # if PosStr == '1_1':
            #     print(LeftUpperPos, LeftUpperPos[1] + ChipSize[1] + WhiteBorder,
            #           LeftUpperPos[0] + ChipSize[0] + WhiteBorder)
            # if PosStr == '1_4':
            #     print(LeftUpperPos, LeftUpperPos[1] + ChipSize[1] + WhiteBorder,
            #           LeftUpperPos[0] + ChipSize[0] + WhiteBorder)

            SumWhiteTestImage = np.sum(TestRectangle)
            SumBlackTestImage = PosDict.get('WhiteBorderBoxArea') - SumWhiteTestImage
            BlackNum = PosDict.get('BlackNum' + PosStr)
            # 一些调试可能需要用到的语句
            # print(PosStr, '原图中黑色像素点个数', SumBlackTestImage)
            # print('boxarea', (BlackNum - BoxArea * (1 - similarity)))
            # print(PosStr, '原图中白色像素点个数', SumWhiteTestImage)
            # 这里相似程序比较难搞，调到0.97附近只有很小的波动范围，因此加一个参数 0.8 约束一下，使可调范围大一些
            if SumBlackTestImage < (BlackNum - BoxArea * similarity * 0.8):
                ReturnList.append(PosStr)
    return ReturnList


# 创建配方文件的文件夹目录
def CreatConfigPath():
    # 配方文件存储目录 存储于当前执行目录下
    Config_Floder = 'config_file'
    if not os.path.exists(Config_Floder):
        os.makedirs(Config_Floder)
        print('Make configfile path', Config_Floder)


# 获取想要的一系列图片
def ChooseWantedKind(ChipsImage_Floder, CateGory_Wanted='5'):
    # CateGory_Wanted = '5'  # 想要五号类别的芯片
    ImageFileList = [x for x in os.listdir(ChipsImage_Floder) if x.split('-')[0] == CateGory_Wanted]
    print(ImageFileList)


# 获取当前执行目录的上一层目录
def GetFatherFloder():
    return os.path.abspath(os.path.pardir)


# 获取DataSource文件夹下 名为foldname文件夹中的 所有文件列表
# 返回文件列表
def GetTestImageFileList(foldname):
    Father_Floder = GetFatherFloder()
    ChipsImage_Floder = Father_Floder + '/DataSource/' + foldname
    # 寻找所有图片格式文件
    ImageFileList = [x for x in os.listdir(ChipsImage_Floder) if
                     (('.jpg' in x) or ('.bmp' in x) or ('.png' in x) or ('.jpeg' in x))]
    # 在每个图片文件名前加上文件夹目录
    ReutrnList = map((lambda x: ChipsImage_Floder + '/' + x), ImageFileList)
    return list(ReutrnList)


# 获取图片宽高
# 输入 图片文件名
def GetImageSize(img):
    img = Image.open(img)
    w, h = img.size
    return w, h


# 对输入的图片文件名进行识别 返回识别结果列表
def StartAnalysisImage(ImageName, BinaryThreshold=180, similarity=0.1,Dict=Position_Matrix):

    img = Image.open(ImageName)

    # 转化为灰度图
    GrayImage = img.convert('L')
    # 自己设置转化过程中二值化的阈值
    # 255为纯白 0为纯黑
    table = []
    for i in range(256):
        if i < BinaryThreshold:
            table.append(0)
        else:
            table.append(1)
    BinaryImage = GrayImage.point(table, '1')
    BinaryImageArray = np.array(BinaryImage) + 0


    # 这样结果就会是0 1 而不是True False

    # # 显示灰度和二值化图像
    # GrayImage.show()
    # BinaryImage.show()

    # 保存matlab文件 便于查看
    # sio.savemat('Graph.mat', {'Slice': BinaryImageArray})
    MatchResultList = CompareModelWithWhiteBorder(BinaryImageArray, Dict,
                                                  similarity=similarity)
    # print('残缺芯片位置',MatchResultList)
    return MatchResultList


# 创建文件夹用于存储标注之后的结果图片
def CreatCicledFolder():
    foldername = 'CicledImage'
    if not os.path.exists(foldername):
        os.makedirs(foldername)


# 在图片上画一个矩形框用以表示识别成功
# 输入 Pillow格式图片 需要划框位置的左上角绝对坐标列表 需要划x位置的左上角绝对坐标列表 框的大小  单位都是像素
# 返回 划过框的图片
def DrawRectange(img, DamagePosList, PosDict=Position_Matrix, LineWidth=8):
    ChipSize = PosDict.get('ChipSize')
    maxrow, maxcol = PosDict.get('Format').split('x')
    maxrow = int(maxrow)
    maxcol = int(maxcol)

    draw = ImageDraw.Draw(img)
    LineColor = GetLineColor(img.mode)

    for row in range(1, maxrow + 1):
        for col in range(1, maxcol + 1):
            PosStr = str(row) + '_' + str(col)
            # 如果是完整的芯片的序号:
            if PosStr not in DamagePosList:
                ChipTopLeftCorner = PosDict.get(PosStr)
                draw.line([tuple(ChipTopLeftCorner),
                           (ChipTopLeftCorner[0] + ChipSize[0], ChipTopLeftCorner[1]),
                           (ChipTopLeftCorner[0] + ChipSize[0], ChipTopLeftCorner[1] + ChipSize[1]),
                           (ChipTopLeftCorner[0], ChipTopLeftCorner[1] + ChipSize[1]),
                           tuple(ChipTopLeftCorner)],
                          fill=LineColor, width=LineWidth)
            # 找到残缺的芯片则画x
            if PosStr in DamagePosList:
                ChipTopLeftCorner = PosDict.get(PosStr)
                draw.line([tuple(ChipTopLeftCorner),
                           (ChipTopLeftCorner[0] + ChipSize[0], ChipTopLeftCorner[1] + ChipSize[1])],
                          fill=LineColor, width=LineWidth)
                draw.line([(ChipTopLeftCorner[0] + ChipSize[0], ChipTopLeftCorner[1]),
                           (ChipTopLeftCorner[0], ChipTopLeftCorner[1] + ChipSize[1]), ],
                          fill=LineColor, width=LineWidth)
    return img


# 此函数类似上面DrawRectange函数 不过此函数绘出的边界是带有白色留白部分的边框
def DrawRectangeWithWhiteBorder(img, DamagePosList, PosDict=Position_Matrix, LineWidth=8):
    ChipSize = PosDict.get('ChipSize')
    maxrow, maxcol = PosDict.get('Format').split('x')
    maxrow = int(maxrow)
    maxcol = int(maxcol)
    WhiteBorder = PosDict.get('WhiteBorder')

    if PosDict.get('ifNest'):
        maxrowMicro, maxcolMicro = PosDict.get('FormatMicro').split('x')
        maxrowMicro = int(maxrowMicro)
        maxcolMicro = int(maxcolMicro)
    else:
        maxrowMicro = 1
        maxcolMicro = 1

    # 创建绘图对象
    draw = ImageDraw.Draw(img)
    # 根据图片类型获取对应颜色
    LineColor = GetLineColor(img.mode)

    for row in range(1, maxrow * maxrowMicro + 1):
        '''先测试一行'''
        # if row!=1:
        #     continue
        for col in range(1, maxcol * maxcolMicro + 1):
            PosStr = str(row) + '_' + str(col)
            # 如果是完整的芯片的序号:
            if PosStr not in DamagePosList:
                ChipTopLeftCorner = PosDict.get(PosStr)
                draw.line(GetDrawLineBoardPos(ChipTopLeftCorner, ChipSize, WhiteBorder, shape='o'),
                          fill=LineColor, width=LineWidth)
            # 找到残缺的芯片则画x
            if PosStr in DamagePosList:
                ChipTopLeftCorner = PosDict.get(PosStr)
                draw.line(GetDrawLineBoardPos(ChipTopLeftCorner, ChipSize, WhiteBorder, shape='x1'),
                          fill=LineColor, width=LineWidth)
                draw.line(GetDrawLineBoardPos(ChipTopLeftCorner, ChipSize, WhiteBorder, shape='x2'),
                          fill=LineColor, width=LineWidth)
    return img


# 为方便留白绘制，特地写的得到绘图多个像素值的程序
# 变量TopLeft表示需要画的图形左上角像素位置，ChipSize表示芯片的大小,WhiteBorder表示白色边框长度
# shape表示需要绘制的形状 是矩形(对应参数为'o')还是X(对应参数为'x1' 'x2') 因为X需要用两笔来画，
# 所以分成x1 x2两个函数
# 返回值为一个list
def GetDrawLineBoardPos(TopLeft, ChipSize, WhiteBorder, shape='o'):
    # 芯片四个角，全为元组类型
    BoardLeftUp = (TopLeft[0] - WhiteBorder, TopLeft[1] - WhiteBorder)
    BoardRightUp = (TopLeft[0] + ChipSize[0] + WhiteBorder, TopLeft[1] - WhiteBorder)
    BoardRighDown = (TopLeft[0] + ChipSize[0] + WhiteBorder, TopLeft[1] + ChipSize[1] + WhiteBorder)
    BoardLeftDown = (TopLeft[0] - WhiteBorder, TopLeft[1] + ChipSize[1] + WhiteBorder)
    # 绘制矩形
    if shape == 'o':
        return [BoardLeftUp, BoardRightUp, BoardRighDown, BoardLeftDown, BoardLeftUp]
    if shape == 'x1':
        return [BoardLeftUp, BoardRighDown]
    if shape == 'x2':
        return [BoardRightUp, BoardLeftDown]


# 根据传入图像的格式获取对应的线条颜色 便于绘图
def GetLineColor(img_mode):
    if img_mode == 'RGB':
        return (255, 0, 0)
    elif img_mode == 'L':
        # 纯黑填充
        return (0,)
    else:
        return (0,)


# 在图片上画一个X用以表示识别失败 芯片残损
def DrawX():
    pass


# 测试所有图片文件并保存
# ImageFileList 文件名列表  SaveFormat：保存的文件格式
def TestAllImageAndSave(ImageFileList, SaveFormat='jpg', similarity=0.1):
    # 创建保存图片的文件夹
    CreatCicledFolder()
    # 根据输入参数获取保存的文件后缀 以及 Image的保存格式
    Suffix, ImgSaveFormat = GetImageSuffixAndSaveFormat(SaveFormat)
    # 遍历列表检测图片文件
    for TestImage in ImageFileList:
        DamageLocation = StartAnalysisImage(TestImage, similarity=similarity)
        img = DrawRectangeWithWhiteBorder(Image.open(TestImage), DamageLocation, Position_Matrix)
        # 获取文件名
        imgName = os.path.basename(TestImage)
        img.save('CicledImage' + '/' + imgName.split('.')[0] + Suffix, ImgSaveFormat)


# 获得不同格式的图片的后缀名和保存格式
def GetImageSuffixAndSaveFormat(types):
    if types == 'bmp' or types == 'BMP':
        return '.bmp', 'bmp'
    if types == 'jpg' or types == 'JPG':
        return '.jpg', 'jpeg'
    if types == 'jpeg' or types == 'JPEG':
        return '.jpeg', 'jpeg'


# print(BinaryImageArray)

# drawline = SquareMeasurePosition(BinaryImageArray, SquareSize)
# print(drawline)
# drawlineFile = 'drawlin.pickle'
# with open(drawlineFile, 'wb') as Config_File_Save:
#     pickle.dump(drawline, Config_File_Save)


# # 制作绘图
# draw = ImageDraw.Draw(GrayImage)
# # 注意一下PIL中划线第一个位置坐标是水平方向，第二个位置坐标是竖直方向
# draw.line([tuple(drawline), tuple(ListPlus(drawline, BestSize))], fill=(0,), width=1)  # 全黑填充
# # draw.line([(74,27),(369,299)],fill=(0,),width=1)#全黑填充


if __name__ == '__main__':
    ImageFileList = GetTestImageFileList('SomeTest')
    # 创建保存的画完框的图片的目录
    CreatCicledFolder()
    # 选择一张图片用作测试
    print('测试文件列表')
    for i in ImageFileList:
        print(i)
    TestImage = 't.jpg'
    print('测试文件名', TestImage)
    print('图片宽高', GetImageSize(TestImage))
    # TestAllImageAndSave(ImageFileList,similarity=0.1)
    DamageLocation = StartAnalysisImage(TestImage, similarity=0.12)
    img = DrawRectangeWithWhiteBorder(Image.open(TestImage), DamageLocation, Position_Matrix,
                                      LineWidth=4)
    img.show()

# pickle格式保存文件
# Config_File_Name = Config_Floder + '/' + 'Name' + Position_Matrix.get('Name') + '.pickle'
# with open(Config_File_Name, 'wb') as Config_File_Save:
#     pickle.dump(Position_Matrix, Config_File_Save)
# pickle格式读取文件
# with open(Config_File_Name, 'rb')as Config_File_Open:
# 	dict2show = pickle.load(Config_File_Open)
