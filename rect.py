import pygame
from pygame import Rect

from misc import rotate_point2 as rotate_point#from pyglibs!
from mask import Mask#from pyglibs!

class RRect(Rect):
    """A rotatable version of the Pygame Rect object."""
    def __init__(self, l, t=0, w=0, h=0, angle=0):
        self.angle = angle #yay - angles :D

        #now we need to init Rect - this just makes sure that is done right...
        if type(l) is type(()) or type(l) is type([]):
            Rect.__init__(self, l, t)
        elif type(l) is type(1) or type(l) is type(1.0):
            Rect.__init__(self, l, t, w, h)
        else:
            Rect.__init__(self, l)

    def collidepoint(self, other):
        other = rotate_point(other, -self.angle, self.center)
        return Rect.collidepoint(self, other)

    def colliderect(self, other):
        a = self
        b = other
        w, h = self.size
        tl = a.topleft
        tr = a.topright
        bl = a.bottomleft
        br = a.bottomright
        tl = rotate_point(tl, a.angle, a.center)
        tr = rotate_point(tr, a.angle, a.center)
        bl = rotate_point(bl, a.angle, a.center)
        br = rotate_point(br, a.angle, a.center)
        for i in [tl, tr, bl, br]:
            if b.collidepoint(i):
                return True

        #only test this if the other fails!
        w, h = b.size
        tl = b.topleft
        tr = b.topright
        bl = b.bottomleft
        br = b.bottomright
        tl = rotate_point(tl, b.angle, b.center)
        tr = rotate_point(tr, b.angle, b.center)
        bl = rotate_point(bl, b.angle, b.center)
        br = rotate_point(br, b.angle, b.center)

        for i in [tl, tr, bl, br]:
            if a.collidepoint(i):
                return True
        return False


class RectMaskCombo(Mask):
    def __init__(self, rect, mask):
        self.rect = rect
        if not self.rect.size == mask.get_size():
            self.rect.size = mask.get_size()
        Mask.__init__(self, mask.get_size())

        self.from_array(mask.get_array())

    def from_array(self, array):
        if use_pygame:
            if not size == self.get_size():
                self = RectMaskCombo(self.rect, Mask((len(array), len(array[0]))))
        Mask.from_array(self, array)

    def colliderectmask(self, other):
        return self.overlap(other,
                            (other.rect.left-self.rect.right,
                             other.rect.top-self.rect.bottom))

    def colliderect(self, other):
        return Mask.colliderect(other,
                                (other.left-self.rect.right,
                                 other.top-self.rect.bottom))

    def collidepoint(self, point):
        return Mask.collidepoint((self.rect.right-point[0],
                                  self.rect.bottom-point[1]),
                                 (0,0))
