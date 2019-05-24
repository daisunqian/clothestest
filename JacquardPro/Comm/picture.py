#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author  :   sqdai
@Contact :   654251408@qq.com
@Software:   PyCharm
@File    :   picture.py
@Time    :   2019/4/16 9:34

'''
import os

# l = []
# for root, dirs, files in os.walk('../'):
#     for file in files:
#         if os.path.splitext(file)[1] == '.jpg':
#             l.append(os.path.join(root, file))
#         if os.path.splitext(file)[1] == '.png':
#             l.append(os.path.join(root, file))
#         if os.path.splitext(file)[1] == '.ico':
#             l.append(os.path.join(root, file))
# print l
# print len(l)
# for i in range(len(l)):
#     if l[i].split('\\')[len(l[i].split('\\'))-1] == "no_img.jpg":
#         print 7777
# for i in range(len(l)):
#     if l[i] == './resource\\auto_chk.ico':
#         print 555
#     print l[i].split('\\')[1]
#     print l[i].split('\\')[len(l[i].split('\\'))-1]
class Pictures(object):
    appfilename = None
    auto_chkfilename = None
    backfilename = None
    closefilename = None
    clothesfilename = None
    exitfilename = None
    exit1filename = None
    innorevfilename = None
    no_imgfilename = None
    resetfilename = None
    startfilename = None
    stopfilename = None
    testfilename = None
    vitfilename = None

    def __init__(self):
        pass
        # cls.appfilename =None
        # cls.auto_chkfilename = None
        # cls.backfilename = None
        # cls.closefilename = None
        # cls.clothesfilename = None
        # cls.exitfilename = None
        # cls.exit1filename = None
        # cls.innorevfilename = None
        # cls.no_imgfilename = None
        # cls.resetfilename = None
        # cls.startfilename = None
        # cls.stopfilename = None
        # cls.testfilename = None
        # cls.vitfilename = None

    @classmethod
    def getpicture(cls, path):
        l = []
        paths = os.walk(path)
        print paths
        for root, dirs, files in paths:
            for file in files:
                print file
                if os.path.splitext(file)[1] == '.jpg':
                    l.append(os.path.join(root, file))
                if os.path.splitext(file)[1] == '.png':
                    l.append(os.path.join(root, file))
                if os.path.splitext(file)[1] == '.ico':
                    l.append(os.path.join(root, file))

        for i in range(len(l)):
            if l[i].split('\\')[len(l[i].split('\\')) - 1] == "no_img.jpg":
                cls.no_imgfilename = l[i]

        for i in range(len(l)):
            if l[i].split('\\')[len(l[i].split('\\')) - 1] == "app.png":
                cls.appfilename = l[i]

        for i in range(len(l)):
            if l[i].split('\\')[len(l[i].split('\\')) - 1] == "auto_chk.ico":
                cls.auto_chkfilename = l[i]

        for i in range(len(l)):
            if l[i].split('\\')[len(l[i].split('\\')) - 1] == "back.jpg":
                cls.backfilename = l[i]

        for i in range(len(l)):
            if l[i].split('\\')[len(l[i].split('\\')) - 1] == "close.ico":
                cls.closefilename = l[i]

        for i in range(len(l)):
            if l[i].split('\\')[len(l[i].split('\\')) - 1] == "clothes.ico":
                cls.clothesfilename = l[i]

        for i in range(len(l)):
            if l[i].split('\\')[len(l[i].split('\\')) - 1] == "exit.jpg":
                cls.exitfilename = l[i]

        for i in range(len(l)):
            if l[i].split('\\')[len(l[i].split('\\')) - 1] == "exit1.jpg":
                cls.exit1filename = l[i]

        for i in range(len(l)):
            if l[i].split('\\')[len(l[i].split('\\')) - 1] == "innorev.png":
                cls.innorevfilename = l[i]

        for i in range(len(l)):
            if l[i].split('\\')[len(l[i].split('\\')) - 1] == "reset.ico":
                cls.resetfilename = l[i]

        for i in range(len(l)):
            if l[i].split('\\')[len(l[i].split('\\')) - 1] == "start.ico":
                cls.startfilename = l[i]
        for i in range(len(l)):
            if l[i].split('\\')[len(l[i].split('\\')) - 1] == "stop.ico":
                cls.stopfilename = l[i]
        for i in range(len(l)):
            if l[i].split('\\')[len(l[i].split('\\')) - 1] == "test.ico":
                cls.testfilename = l[i]
        for i in range(len(l)):
            if l[i].split('\\')[len(l[i].split('\\')) - 1] == "vit.png":
                cls.vitfilename = l[i]

        for i in range(len(l)):
            if l[i].split('\\')[len(l[i].split('\\')) - 1] == "hands.jpg":
                cls.handsfilename = l[i]

if __name__ == '__main__':
    pic = Pictures()
    pic.getpicture("../")
    print pic.clothesfilename