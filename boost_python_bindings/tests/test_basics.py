#!/usr/bin/python3

# to be called via nose, for example
# nosetests-3.4 -v path_to/tests/test_basics.py

from halide import *

def test_types():

    t0 = Int(32)
    t1 = Int(16)

    assert t0 != t1
    assert t0.is_float() == False
    assert t1.is_float() == False

    print("Int(32) type:", Int(32))
    print("Int(16) type:", Int(16))

    return

def test_basics():

    input = ImageParam(UInt(16), 2, 'input')
    x, y = Var('x'), Var('y')

    blur_x = Func('blur_x')
    blur_xx = Func('blur_xx')
    blur_y = Func('blur_y')

    yy = cast(Int(32), 1)
    assert yy.type() == Int(32)
    print("yy type:", yy.type())

    z = x + 1
    input[x,y]
    input[0,0]
    input[z,y]
    input[x+1,y]
    print("ping 0.2")
    input[x,y]+input[x+1,y]

    if False:
        aa = blur_x[x,y]
        bb = blur_x[x,y+1]
        aa + bb
        blur_x[x,y]+blur_x[x,y+1]

    print("ping 0.3")
    (input[x,y]+input[x+1,y]) / 2
    print("ping 0.4")
    blur_x[x,y]
    print("ping 0.4.1")
    blur_xx[x,y] = input[x,y]



    print("ping 0.5")
    blur_x[x,y] = (input[x,y]+input[x+1,y]+input[x+2,y])/3
    print("ping 1")
    blur_y[x,y] = (blur_x[x,y]+blur_x[x,y+1]+blur_x[x,y+2])/3

    xi, yi = Var('xi'), Var('yi')
    print("ping 2")
    blur_y.tile(x, y, xi, yi, 8, 4).parallel(y).vectorize(xi, 8)
    blur_x.compute_at(blur_y, x).vectorize(x, 8)


    blur_y.compile_jit()
    print("Compiled to jit")

    return


def test_basics2():

    input = ImageParam(Float(32), 3, 'input')
    r_sigma = Param(Float(32), 'r_sigma', 0.1) # Value needed if not generating an executable
    s_sigma = 8 # This is passed during code generation in the C++ version

    x = Var('x')
    y = Var('y')
    z = Var('z')
    c = Var('c')

    # Add a boundary condition
    clamped = Func('clamped')
    clamped[x, y] = input[clamp(x, 0, input.width()-1),
                          clamp(y, 0, input.height()-1),0]

    if True:
        print("s_sigma", s_sigma)
        print("s_sigma/2", s_sigma/2)
        print("s_sigma//2", s_sigma//2)
        print()
        print("x * s_sigma", x * s_sigma)
        print("x * 8", x * 8)
        print("x * 8 + 4", x * 8 + 4)
        print("x * 8 * 4", x * 8  * 4)
        print()
        print("x", x)
        print("(x * s_sigma).type()", )
        print("(x * 8).type()", (x * 8).type())
        print("(x * 8 + 4).type()", (x * 8 + 4).type())
        print("(x * 8 * 4).type()", (x * 8 * 4).type())
        print("(x * 8 / 4).type()", (x * 8 / 4).type())
        print("((x * 8) * 4).type()", ((x * 8) * 4).type())
        print("(x * (8 * 4)).type()", (x * (8 * 4)).type())


    assert (x * 8).type() == Int(32)
    assert (x * 8 * 4).type() == Int(32) # yes this did fail at some point
    assert ((x * 8) / 4).type() == Int(32)
    assert (x * (8 / 4)).type() == Float(32) # under python3 division rules
    assert (x * (8 // 4)).type() == Int(32)
    #assert (x * 8 // 4).type() == Int(32) # not yet implemented


    # Construct the bilateral grid
    r = RDom(0, s_sigma, 0, s_sigma, 'r')
    val0 = clamped[x * s_sigma, y * s_sigma]
    val00 = clamped[x * s_sigma * cast(Int(32), 1), y * s_sigma * cast(Int(32), 1)]
    #val1 = clamped[x * s_sigma - s_sigma/2, y * s_sigma - s_sigma/2] # should fail
    val22 = clamped[x * s_sigma - cast(Int(32), s_sigma//2),
                    y * s_sigma - cast(Int(32), s_sigma//2)]
    val2 = clamped[x * s_sigma - s_sigma//2, y * s_sigma - s_sigma//2]
    val3 = clamped[x * s_sigma + r.x - s_sigma//2, y * s_sigma + r.y - s_sigma//2]

    return


def test_ndarray_to_image():

    if "ndarray_to_image" not in globals():
        print("Skipping test_ndarray_to_image")
        return

    import numpy

    a0 = numpy.ones((200, 300), dtype=numpy.float32)
    i0 = ndarray_to_image(a0, "float32_test_image")
    print("i0", i0)

    a1 = numpy.ones((640, 480), dtype=numpy.uint8)
    i1 = ndarray_to_image(a1, "uint8_test_image")
    print("i1", i1)


    return

if __name__ == "__main__":
    test_types()
    test_basics()
    test_basics2()
    test_ndarray_to_image()