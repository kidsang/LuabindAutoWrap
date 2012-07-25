import clang.cindex
import re
from construct import *

# 需要忽略的关键字
ignore = ['inline']
# 支持重载的运算符
op = ['+', '-', '*', '/', '==', '<', '<=']
# public区域
pubArea = []

# 辅助方法，返回函数参数列表
# string: 含有参数列表的字符串
def getParams(string):
    params = re.search(r'\((.*)\)', string).group(1)
    return params.split(',')

# 寻找public区域
# node: 类根节点
# lines: 文件原始内容
def findPublicArea(node, lines):
    global pubArea
    pubArea = []
    pub = False
    b = -1
    for c in node.get_children():
        if str(c.kind) == 'CursorKind.CXX_ACCESS_SPEC_DECL':
            if lines[c.location.line - 1].find('public') != -1:
                if pub == False:
                    b = c.location.line
                pub = True
            elif pub == True:
                pubArea.append([b, c.location.line])
                b = -1
                pub = False
    if b != -1:
        pubArea.append([b, 999999])    

# 寻找类的构造函数
# className: 类名
# node: 类根节点
def findConstructors(className, node):
    global indent
    for c in node.get_children():
        if str(c.kind) == 'CursorKind.CONSTRUCTOR':
            # 判断public区域
            pub = False
            for a in pubArea:
                if a[0] < c.location.line < a[1]:
                    pub = True
                    break
            if pub == False:
                continue
            # 分离参数列表
            params = getParams(c.displayname)
            print defConstructor(params)
            

# 寻找类的成员函数
# className: 类名
# node: 类根节点
# lines: 文件原始内容
def findMethod(className, node, lines):
    global indent
    for c in node.get_children():
        if str(c.kind) == 'CursorKind.CXX_METHOD':
            # 判断public区域
            pub = False
            for a in pubArea:
                if a[0] < c.location.line < a[1]:
                    pub = True
                    break
            if pub == False:
                continue
            if str(c.spelling).find('operator') == -1: # 非运算符重载
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
                params = getParams(c.displayname)
                print defMethod(className, c.spelling, ret, params)
            else : #运算符重载
                for o in op:
                    if c.spelling.replace('operator', '') == o:
                        # 分离参数列表
                        params = getParams(c.displayname)
                        if len(params) != 1 or params[0] == '':
                            break
                        print defOperator(o, params)
                        break
                        

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
        findPublicArea(node, lines)
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

