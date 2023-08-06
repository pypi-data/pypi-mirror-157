#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib

def add_(num1, num2):
    return num1 + num2


def md5_(name):
    # 创建md5对象
    m = hashlib.md5()
    b = name.encode(encoding='utf-8')
    m.update(b)
    str_md5 = m.hexdigest()
    return str_md5


def sha1(name):
    sha1 = hashlib.sha1()
    key = name.encode('utf-8')
    sha1.update(key)
    sha1_str = sha1.hexdigest()
    return sha1_str
