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
