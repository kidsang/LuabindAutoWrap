import clang.cindex
import re
from construct import *

def displayEnum(node):
    for c in node.get_children():
        print defEnum(c.spelling, c.enum_value)

def findEnum(node):
    for c in node.get_children():
        if str(c.kind) == 'CursorKind.ENUM_DECL':
            print '//---->', c.displayname
            displayEnum(c)
            print '//<----', c.displayname
            

def findNamespace(node, name):
    for c in node.get_children():
        if str(c.kind) == 'CursorKind.NAMESPACE' \
           and c.spelling == name:
            findEnum(c)

if __name__ == '__main__':
    index = clang.cindex.Index.create()
    fileName = 'include/OIS/OISMouse.h'
    tu = index.parse(fileName, args=['-x', 'c++'])
    findNamespace(tu.cursor, 'OIS')
    
