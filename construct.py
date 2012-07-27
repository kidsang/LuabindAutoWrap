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

def defMethod(className, methodName, ret, params):
    out = '        .def("' + methodName + '", '
    out += '(' + ret
    out += '(' + className + '::*)('
    l = len(params)
    for i in range(l):
        out += params[i]
        if i < l - 1:
            out += ', '
    out += '))'
    out += '&' + className + '::' + methodName + ')'
    return out

def defOperator(op, params):
    out = '        .def(self '
    out += op + ' '
    out += 'other<' + params[0] + '>())'
    return out

def defProperty(className, propertyName):
    out = '        .def_readonly("' + propertyName + '", '
    out += '&' + className + '::' + propertyName + ')'
    return out

def defEnum(name, value):
    out = '        value("' + name + '", ' + str(value) + '),'
    return out
