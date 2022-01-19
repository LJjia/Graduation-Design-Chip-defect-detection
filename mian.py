import tkinter as tk
import os
import time
from PIL import Image
from tkinter import messagebox
import pickle
import NestCreateModel
import ConfirmSatisfy
import AnalysePhotoMatchChip


# 绘制第1行
def drawline1():
    ChipPosLeftDown = (753, 302)
    ChipPosRightDown = (943, 302)
    curmacro_pos = (1, 3)
    print('draw line 1')
    NestCreateModel.CreateLabelBoxLine(OriginImagePath='Origin.jpg',
                                       TxtPath='ChipInfo.txt', ChipPosLeftDown=ChipPosLeftDown,
                                       ChipPosRightDown=ChipPosRightDown, curmacro_pos=curmacro_pos,
                                       DrawBoxOfChip='Below')
    sat = tk.messagebox.askyesno(title='计算结果', message='您对这个结果是否满意')
    ConfirmSatisfy.CustConfirmPosDict(sat, 'CustomerDefine5')


# 绘制第2行
def drawline2():
    ChipPosLeftDown = (753, 905)
    ChipPosRightDown = (943, 905)
    curmacro_pos = (2, 3)
    print('draw line 2')
    NestCreateModel.CreateLabelBoxLine(OriginImagePath='Origin.jpg',
                                       TxtPath='ChipInfo.txt', ChipPosLeftDown=ChipPosLeftDown,
                                       ChipPosRightDown=ChipPosRightDown, curmacro_pos=curmacro_pos,
                                       DrawBoxOfChip='Above')
    sat = tk.messagebox.askyesno(title='计算结果', message='您对这个结果是否满意')
    ConfirmSatisfy.CustConfirmPosDict(sat, 'CustomerDefine5')


def showdict():
    print('用户生成的模版字典')
    foldername = 'CustomerDefineModel'
    dictname = 'CustomerDefine5.pickle'
    # pickle格式读取文件
    with open(foldername + '/' + dictname, 'rb')as dictfile:
        dict2show = pickle.load(dictfile)
    print(dict2show)


def showtestimg():
    imglist = [x for x in os.listdir('.') if '.jpg' in x]
    for i in imglist:
        img = Image.open(i)
        w, h = img.size
        img = img.resize((w // 4, h // 4))
        # time.sleep(1)
        img.show()


def showtestresult():
    foldername = 'CustomerDefineModel'
    dictname = 'CustomerDefine5.pickle'
    # pickle格式读取文件
    with open(foldername + '/' + dictname, 'rb')as dictfile:
        modeldict = pickle.load(dictfile)
    # 字典中的一些值要修改
    ChipSize_tmp = modeldict.get('ChipSize')
    WhiteBorder_tmp = modeldict.get('WhiteBorder')
    WhiteBorderBoxArea_tmp = (ChipSize_tmp[0] + WhiteBorder_tmp) * (ChipSize_tmp[1] + WhiteBorder_tmp)
    # 计算两种BoxArea的值并写入字典中
    modeldict['BoxArea'] = ChipSize_tmp[0] * ChipSize_tmp[1]
    modeldict['WhiteBorderBoxArea'] = WhiteBorderBoxArea_tmp


    imglist = [x for x in os.listdir('.') if '.jpg' in x]
    for TestImage in imglist:
        DamageLocation = AnalysePhotoMatchChip.StartAnalysisImage(TestImage, similarity=0.12,
                                                                  Dict=modeldict)
        img = AnalysePhotoMatchChip.DrawRectangeWithWhiteBorder(Image.open(TestImage),
                                                                DamageLocation, modeldict,
                                                                LineWidth=4)
        w, h = img.size
        img = img.resize((w // 4, h // 4))
        img.show()


window = tk.Tk()
window.title('芯片残缺检测')
window.geometry('300x200')
ButtonLine1 = tk.Button(window, height=2, text='计算第1行', command=drawline1)
ButtonLine1.pack()
ButtonLine2 = tk.Button(window, height=2, text='计算第2行', command=drawline2)
ButtonLine2.pack()

ButtonShowDict = tk.Button(window, height=2, text='展示生成的模版字典', command=showdict)
ButtonShowDict.pack()
ButtonShowTest = tk.Button(window, height=2, text='展示待检测图片', command=showtestimg)
ButtonShowTest.pack()
ButtonShowResult = tk.Button(window, height=2, text='展示检测结果', command=showtestresult)
ButtonShowResult.pack()


if __name__ == '__main__':
    window.mainloop()
