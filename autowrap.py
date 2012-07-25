from parse import *

if __name__ == '__main__':
    parse('include/OgreMath.h', ['Radian', 'Degree', 'Angle', 'Math'])
    parse('include/OgreVector2.h', ['Vector2'])
    parse('include/OgreVector3.h', ['Vector3'])
    parse('include/OgreVector4.h', ['Vector4'])
    parse('include/OgreMatrix3.h', ['Matrix3'])
    parse('include/OgreMatrix4.h', ['Matrix4'])
    parse('include/OgreQuaternion.h', ['Quaternion'])
