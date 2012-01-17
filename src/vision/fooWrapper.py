from ctypes import cdll
lib = cdll.LoadLibrary('./libfoo.so')

class Foo(object):
    def __init__(self):
        self.obj = lib.Foo_new()

    def bar(self):
        lib.Foo_bar(self.obj)
    def getNumBalls(self):
        return lib.Foo_getNumBalls(self.obj)
    def getR( self, index):
        return lib.Foo_getR(self.obj, index);
    def getTheta( self, index):
        return lib.Foo_getTheta(self.obj, index);



f = Foo()
f.bar()
print f.getNumBalls()
print f.getR(0);
print f.getTheta(0);
