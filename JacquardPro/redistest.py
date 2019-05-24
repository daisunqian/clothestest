#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author  :   sqdai
@Contact :   654251408@qq.com
@Software:   PyCharm
@File    :   redistest.py
@Time    :   2019/5/7 11:04
'''
#!/usr/bin/env python
# -*- coding:utf-8 -*-
# import redis
#
# r = redis.Redis(host='192.168.0.110', port=6379,db=0)
# r.set('name', 'zhangsan')   #添加
# print (r.get('name'))   #获取

import zipfile

with zipfile.ZipFile('test.zip', mode='w') as zipf:

   zipf.write('redistest.py')
   zipf.write("login.py")

zipf = zipfile.ZipFile('test.zip')
print zipf.namelist()