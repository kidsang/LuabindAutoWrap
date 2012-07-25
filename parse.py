import clang.cindex
import re
from construct import *

ignore = ['inline']

# 寻找类的构造函数
# className: 类名
# node: 类根节点
def findConstructors(className, node):
    global indent
    for c in node.get_children():
        if str(c.kind) == 'CursorKind.CONSTRUCTOR':
            # 分离参数列表
            params = re.search(r'\((.*)\)', c.displayname).group(1)
            params = params.split(',')
            print defConstructor(params)
            

# 寻找类的成员函数
# className: 类名
# node: 类根节点
# lines: 文件原始内容
def findMethod(className, node, lines):
    global indent
    for c in node.get_children():
        if str(c.kind) == 'CursorKind.CXX_METHOD' \
           and str(c.spelling).find('operator') == -1: # 跳过运算符重载
            # 查找返回值
            ret = lines[c.location.line-1] \
                  [:c.location.column - 1]
            # 跳过静态函数
            if ret.find('static') != -1:
                continue
            # 清除不需要的关键词
            for i in ignore:
                ret = ret.replace(i, '')
            ret = re.sub(r'^\s*', '', ret)
            # 分离参数列表
            params = re.search(r'\((.*)\)', c.displayname).group(1)
            params = params.split(',')
            print defMethod(className, c.spelling, ret, params)
            

# 寻找相应名称的类
# node: 文档根节点
# name: 类名
# lines: 文件原始内容
def findClass(node, name, lines):
    global indent
    if str(node.kind) == 'CursorKind.CLASS_DECL' \
            and str(node.spelling) == name \
            and node.is_definition():
        print defClass(name)
        findConstructors(name, node)
        findMethod(name, node, lines)

    for c in node.get_children():
        findClass(c, name, lines)

def parse(fileName, classList):
    index = clang.cindex.Index.create()
    tu = index.parse(fileName, args=['-x', 'c++'])
    f = open(fileName)
    lines = f.readlines()
    f.close()
    print '//---->>' + fileName ,
    print moduleBegin()
    l = len(classList)
    for i in range(l):
        print '\t//--' + classList[i]
        findClass(tu.cursor, classList[i], lines)
        if i < l - 1:
            print ','
    
    print moduleEnd()
    print '//<<----' + fileName

