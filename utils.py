# -*- coding: utf-8 -*-
__author__ = 'linzhonghong'
#
from threading import Thread
import ConfigParser
import os
import re
import sys
import shutil
import hashlib

# 线程装饰器
def call_thread(func):
    def _wrapper(*args, **kwargs):
        t = Thread(target=func, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()
    return _wrapper

# 图片迭代
def getNextImageID(count):
    imID = 0
    while True:
        yield imID
        imID += 1
        if imID == count:
            imID = 0

# 编辑配置
class ModifyConf(object):
    def __init__(self,filename):
        self.filename = filename
        self.config = ConfigParser.ConfigParser()

    def write(self,section,**keyv):
        self.config.read(self.filename)
        section_name = section
        fp = open(self.filename, 'w')
        if not self.config.has_section(section):
            self.config.add_section( section_name  )
            [self.config.set(section, key, keyv[key]) for key in keyv]
        else:
            [self.config.set(section, key, keyv[key]) for key in keyv if self.config.has_option(section, key) ]
        self.config.write( fp )
        fp.close()

    def clear_section(self, section):
        self.config.read(self.filename)
        fp = open(self.filename, 'w')
        if self.config.has_section(section):
            [self.config.set(section, key, '') for key in self.config.options(section)]
        self.config.write( fp )
        fp.close()

    def set_option(self, section, option, value):
        self.config.read(self.filename)
        fp = open(self.filename, 'w')
        if self.config.has_section(section):
#            print 'hassss'
            self.config.set(section, option, value)
        self.config.write( fp )
        fp.close()

    def read(self,section,key):
        self.config.read(self.filename)
        return self.config.get(section,key)

    def read_all(self, section):
        self.config.read(self.filename)
        return self.config.items(section)

def str2digit(string):
    return int(hashlib.md5(string).hexdigest(), 16)

def md5(string):
    return hashlib.md5(string).hexdigest()

def encrypt(key, s):
    b = bytearray(str(s).encode("gbk"))
    n = len(b) # 求出 b 的字节数
    c = bytearray(n*2)
    j = 0
    for i in range(0, n):
        b1 = b[i]
        b2 = b1 ^ key # b1 = b2^ key
        c1 = b2 % 16
        c2 = b2 // 16 # b2 = c2*16 + c1
        c1 = c1 + 65
        c2 = c2 + 65 # c1,c2都是0~15之间的数,加上65就变成了A-P 的字符的编码
        c[j] = c1
        c[j+1] = c2
        j = j+2
    return c.decode("utf-8")

def decrypt(key, s):
    c = bytearray(str(s).encode("utf-8"))
    n = len(c) # 计算 b 的字节数
    if n % 2 != 0 :
        return ""
    n = n // 2
    b = bytearray(n)
    j = 0
    for i in range(0, n):
        c1 = c[j]
        c2 = c[j+1]
        j = j+2
        c1 = c1 - 65
        c2 = c2 - 65
        b2 = c2*16 + c1
        b1 = b2^ key
        b[i]= b1
    try:
        return b.decode("utf-8")
    except:
        return "failed"

# os.path.expanduser('~') finds out the user HOME dir where
CONF_DIR = os.path.expanduser('~') + os.sep + '.dnspod_desktop'

def init_conf():
    configfile = CONF_DIR + os.sep + 'conf.ini'
    path = os.path.split(os.path.realpath(sys.argv[0]))[0].decode('gb2312') + os.sep + 'etc'
    if not os.path.exists(CONF_DIR):
        os.mkdir(CONF_DIR)
    if not os.path.exists(configfile):
        shutil.copy(path+os.sep+'conf.ini', configfile)

def get_auth():
#    path = os.path.split(os.path.realpath(sys.argv[0]))[0] + os.sep + 'etc'
    path = CONF_DIR
    ret = {}
    with open(path+os.sep+'secret.txt','r') as f:
        for line in f:
            k,v = line.strip('\n').split('@')
            ret[k] = v
    return ret

def get_conf(section='db', key=''):
    confdir = CONF_DIR
    conf = ModifyConf(confdir+os.sep+'conf.ini')
    return conf.read(section, key)

def set_conf(section='db', key='', value=''):
    confdir = CONF_DIR
    conf = ModifyConf(confdir+os.sep+'conf.ini')
    conf.set_option(section, key, value)

def clear_conf(section='db'):
    confdir = CONF_DIR
    conf = ModifyConf(confdir+os.sep+'conf.ini')
    conf.clear_section(section)
#
def validateIP(text):
    return re.search(r"^((?:(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d))))$", text) or False