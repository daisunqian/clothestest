# -*- coding: utf-8 -*-

import hashlib

# 加密
def tomd5(data):
    md = hashlib.md5()  # 构造一个md5对象
    md.update(data.encode())
    res = md.hexdigest()
    return res


if __name__ == "__main__":
    import sys

    print tomd5('123456')