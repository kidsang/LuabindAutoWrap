import clang.cindex
import re
from construct import *

# 需要忽略的关键字
ignore = ['inline', 'virtual']
# 支持重载的运算符
op = ['+', '-', '*', '/', '==', '<', '<=']
# public区域
pubArea = []

# 辅助方法，判断当前节点是否处于公有区域
def isPublicArea(node):
    global pubArea
    pub = False
    for a in pubArea:
        if a[0] < node.location.line < a[1]:
            pub = True
            break
    return pub

# 辅助方法，返回函数参数列表
# string: 含有参数列表的字符串
def getParams(string):
    params = re.search(r'\((.*)\)', string).group(1)
    return params.split(',')

# 寻找公有属性
# className: 类名
# node: 类根节点
def findProperties(className, node):
    for c in node.get_children():
        if str(c.kind) == 'CursorKind.FIELD_DECL':
            # 判断public区域
            if not isPublicArea(c):
                continue
            print defProperty(className, c.spelling)
            

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

# 寻找类的枚举型
# node: 类根节点
def findEnum(node):
    for c in node.get_children():
        if str(c.kind) == 'CursorKind.ENUM_DECL':
            # 判断public区域
            if not isPublicArea(c):
                continue
            print '        //---->', c.displayname
            print '        .enum_("constants")'
            print '        ['
            enu = ''
            for cc in c.get_children():
                enu += ' ' * 4 + defEnum(cc.spelling, cc.enum_value) + '\n'
            enu = enu[:-2]
            print enu
            print '        ]'
            print '        //<----', c.displayname

# 寻找类的构造函数
# className: 类名
# node: 类根节点
def findConstructors(className, node):
    for c in node.get_children():
        if str(c.kind) == 'CursorKind.CONSTRUCTOR':
            # 判断public区域
            if not isPublicArea(c):
                continue
            # 分离参数列表
            params = getParams(c.displayname)
            print defConstructor(params)
            

# 寻找类的成员函数
# className: 类名
# node: 类根节点
# lines: 文件原始内容
def findMethod(className, node, lines):
    for c in node.get_children():
        if str(c.kind) == 'CursorKind.CXX_METHOD':
            # 判断public区域
            if not isPublicArea(c):
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
    if (str(node.kind) == 'CursorKind.CLASS_DECL' \
        or str(node.kind) == 'CursorKind.STRUCT_DECL') \
            and str(node.spelling) == name \
            and node.is_definition():
        if str(node.kind) == 'CursorKind.STRUCT_DECL':
            global pubArea
            pubArea.append([0, 99999])
        else:
            findPublicArea(node, lines)
        print defClass(name)
        findConstructors(name, node)
        findMethod(name, node, lines)
        findProperties(name, node)
        findEnum(node)

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

