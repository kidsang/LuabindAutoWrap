def moduleBegin():
    out = \
    '''
    module(L)
    ['''
    return out

def moduleEnd():
    out = '];'
    return out

def defClass(className):
    out = '    class_<' + className + '>("' + className + '")'
    return out

def defConstructor(params):
    out = '        .def(constructor<';
    l = len(params)
    for i in range(l):
        out += params[i]
        if i < l - 1:
            out += ', '
    out += '>())'
    return out

def defMethod(className, methodName):
    out = '        .def("' + methodName + '", '
    out += '&' + className + '::' + methodName + ')'
    return out
