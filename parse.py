import clang.cindex
import re
from construct import *

# 寻找类的构造函数
# className: 类名
# node: 类根节点
def findConstructors(className, node):
    global indent
    for c in node.get_children():
        if str(c.kind) == 'CursorKind.CONSTRUCTOR':
            params = re.search(r'\((.*)\)', c.displayname).group(1)
            params = params.split(',')
            print defConstructor(params)
            

# 寻找类的成员函数
# className: 类名
# node: 类根节点
def findMethod(className, node):
    global indent
    for c in node.get_children():
        if str(c.kind) == 'CursorKind.CXX_METHOD' \
           and str(c.spelling).find('operator') == -1: # 跳过运算符重载
            print defMethod(className, c.spelling)
            

# 寻找相应名称的类
# node: 文档根节点
# name: 类名
def findClass(node, name):
    global indent
    if str(node.kind) == 'CursorKind.CLASS_DECL' \
            and str(node.spelling) == name \
            and node.is_definition():
        print defClass(name)
        findConstructors(name, node)
        findMethod(name, node)

    for c in node.get_children():
        findClass(c, name)

def parse(fileName, classList):
    index = clang.cindex.Index.create()
    tu = index.parse(fileName, args=['-x', 'c++'])
    print '//---->>' + fileName ,
    print moduleBegin()
    for c in classList:
        print '\t//--' + c
        findClass(tu.cursor, c)
    print moduleEnd()
    print '//<<----' + fileName

if __name__ == '__main__':
    index = clang.cindex.Index.create()
    tu = index.parse("include/OgreVector3.h", args=['-x', 'c++'])

    #printNodes(tu.cursor)
    findClass(tu.cursor, 'Vector3')
