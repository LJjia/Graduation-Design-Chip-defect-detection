#!/usr/bin/env python
#-*- coding:utf-8 _*-
__author__ = 'LJjia'
# *******************************************************************
#     Filename @  test.py
#       Author @  Jia LiangJun
#  Create date @  2019/05/30 09:46
#        Email @  LJjiahf@163.com
#  Description @  
# ********************************************************************
from PIL import Image
img=Image.open('TestAbove.jpg')
cropimg1=img.crop((736,238,952,326))
cropimg2=img.crop((744,868,956,968))

cropimg1.save('cropabove.jpg','JPEG')
cropimg2.save('cropbelow.jpg','JPEG')