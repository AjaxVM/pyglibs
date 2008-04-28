import math

def rotate_point2(p, angle, center=[0,0]):
    p = [p[0] - center[0], p[1] - center[1]]
    radians = math.radians(-angle)
    cos = math.cos(radians)
    sin = math.sin(radians)
    op = [p[0],p[1]]
    p[0] = (cos * op[0]) - (sin * op[1])
    p[1] = (sin * op[0]) + (cos * op[1])
    return p[0] + center[0], p[1] + center[1]

def careful_div(x, y):
    """will divide by zero without error"""
    if x and y:
        return x/y
    return 0

def careful_mod(x, y):
    """will perform modulo without error"""
    if x and y:
        return x%y
    return 0
