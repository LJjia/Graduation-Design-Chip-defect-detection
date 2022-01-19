#!/usr/bin/env python
# -*- coding:utf-8 _*-
__author__ = 'LJjia'
# *******************************************************************
#     Filename @  SimpleTest.py
#       Author @  Jia LiangJun
#  Create date @  2019/04/29 10:22
#        Email @  LJjiahf@163.com
#  Description @  仅仅用于简单测试文件样例
# ********************************************************************

import cv2
import pickle
def corner_detection(flag_location ,img_name):
    img = cv2.imread(img_name,cv2.IMREAD_GRAYSCALE)
    if img.any:
        dst = cv2.cornerHarris(img, 4, 3, 0.06)
        R = dst > 0.1 * dst.max()#shape得到的是（y,x）
        x_end = R.shape[1]//3
        x_start = (R.shape[1]//3)*2
        y_end = R.shape[0]//3
        y_start = (R.shape[0]//3)*2
        # print(x_end)
        # print(x_start)
        coordinate_x_1 = []#储存得到的点用
        coordinate_y_1 = []
        coordinate_x_2 = []
        coordinate_y_2 = []
        final_left = []   #最终得到的左边坐标
        final_right = []   #最终得到的右边坐标
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
        print('参数：' + '\n', coordinate_x_1, '\n', coordinate_y_1, '\n', coordinate_x_2, '\n', coordinate_y_2, '\n')
        '''---两种取角点方式，以flag_location区分---'''
        if flag_location == 0:
            if not(coordinate_x_1 and coordinate_y_1 and coordinate_x_2 and coordinate_x_2):
                print('有未检测到角点区域，请重新取图！')
            else:

                '''---得到左边x坐标---'''
                data = sorted(coordinate_x_1)#排序
                '''---取中位数---'''
                # size = len(data)
                '''---取极值---'''
                x_2 = min(data)
                final_left.append(x_2)

                '''---得到左边y坐标---'''
                data = sorted(coordinate_y_1)#排序
                '''---取中位数---'''
                '''---取极值---'''
                x_2 = max(data)
                final_left.append(x_2)

                '''---得到右边x坐标---'''
                data = sorted(coordinate_x_2)#排序
                '''---取中位数---'''
                '''---取极值---'''
                x_2=max(data)
                final_right.append(x_2)

                '''---得到右边y坐标---'''
                data = sorted(coordinate_y_2)#排序
                '''---取中位数---'''
                '''---取极值---'''
                x_2=max(data)
                # if abs(x_1 - x_2) < 10:
                #
                # else:
                #     final_right.append(x_2)
                final_right.append(x_2)
                '''---合并参数---'''

                print('结果：',final_left,final_right)
        elif flag_location == 1:
            if not(coordinate_x_1 and coordinate_y_1 and coordinate_x_2 and coordinate_x_2):
                print('有未检测到角点区域，请重新取图！')
            else:
                '''---得到左边x坐标---'''
                data = sorted(coordinate_x_1)#排序
                '''---取中位数---'''
                # size = len(data)
                '''---取极值---'''
                x_2 = min(data)
                final_left.append(x_2)

                '''---得到左边y坐标---'''
                data = sorted(coordinate_y_1)#排序
                '''---取中位数---'''
                '''---取极值---'''
                x_2 = min(data)
                final_left.append(x_2)

                '''---得到右边x坐标---'''
                data = sorted(coordinate_x_2)#排序
                '''---取中位数---'''
                '''---取极值---'''
                x_2=max(data)
                final_right.append(x_2)

                '''---得到右边y坐标---'''
                data = sorted(coordinate_y_2)#排序
                '''---取中位数---'''
                '''---取极值---'''
                x_2=min(data)
                # if abs(x_1 - x_2) < 10:
                #
                # else:
                #     final_right.append(x_2)
                final_right.append(x_2)
                '''---合并参数---'''

                print('结果：',final_left,final_right)
        else:
            print('没有这个图像！')

    return (final_left,final_right)
if __name__ == '__main__':
    flag = 0
    corner_detection(flag,'cropabove.jpg')


    # with open('CustmoDefineModel', 'wb') as Config_File_Save:
    #     pickle.dump(Dict, Config_File_Save)
    # with open('CustomerDefineModel/t.pickle', 'rb')as Config_File_Open:
    #     dict2show = pickle.load(Config_File_Open)
    #
    # print(dict2show)