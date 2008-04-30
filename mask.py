import pygame
from pygame.locals import *

from misc import sub_vector2 as sub_vector

try:
    from pygame import mask
    use_pygame = True
    class Mask(pygame.mask.Mask):

        def __init__(self, size, pos=(0,0)):
            Mask.__init__(self, size)

            self.pos = pos

        def get_width(self):
            return pygame.mask.Mask.get_size(self)[0]

        def get_height(self):
            return pygame.mask.Mask.get_size(self)[1]

        def fill(self, value):
            for x in xrange(self.get_width()):
                for y in xrange(self.get_height()):
                    self.set_at((x, y), value)

        def overlap(self, other):
            return Mask.overlap(self, other, sub_vector(other.pos, self.pos))

        def collidemask(self, other):
            return self.overlap(other)

        def colliderect(self, rect):
            new = Mask(rect.size, rect.topleft)
            new.fill(1)
            return self.collidemask(new)

        def collidepoint(self, point):
            new = pygame.Rect(point, (1,1))
            new.topleft = point
            return self.colliderect(new)

        def get_color_coded_image(self, col_0=[255,0,0], col_1=[0,255,0]):
            c = [col_0, col_1]
            new = pygame.Surface(self.get_size()).convert()
            for x in xrange(self.get_width()):
                for y in xrange(self.get_height()):
                    new.set_at((x, y), c[self.get_at((x, y))])
            return new

        def get_array(self):
            new = []
            for x in xrange(self.get_width()):
                new.append([])
                for y in xrange(self.get_height()):
                    new[x].append(self.get_at((x, y)))
            return new

        def from_array(self, array):
            size = len(array), len(array[0])
            if not size == self.get_size():
                self = Mask(size)
            for x in xrange(len(array)):
                for y in xrange(len(array[0])):
                    self.set_at((x, y), array[x][y])
except:
    use_pygame = False
    class Mask(object):
        def __init__(self, size, pos=(0,0)):
            mask = []
            for x in xrange(size[0]):
                mask.append([])
                for y in xrange(size[1]):
                    mask[x].append(0)

            self.data = mask
            self.size = size

            self.pos = pos

        def get_size(self):
            return self.size

        def get_width(self):
            return self.size[0]

        def get_height(self):
            return self.size[1]

        def get_at(self, pos):
            return self.data[pos[0]][pos[1]]

        def set_at(self, pos, value):
            self.data[pos[0]][pos[1]] = value

        def overlap(self, other):
            offset = sub_vector(other.pos, self.pos)
            overlap = sub_vector(other.pos, self.pos)
            rect1 = pygame.Rect((0,0), self.get_size())
            rect2 = pygame.Rect(offset, other.get_size())
            rect=rect1.clip(rect2)
            if rect.width==0 or rect.height==0:
                return False
            x1,y1,x2,y2 = rect.x-rect1.x,rect.y-rect1.y,rect.x-rect2.x,rect.y-rect2.y
            hm1 = self.data
            hm2 = other.data
            for x in xrange(rect.width):
                for y in xrange(rect.height):
                    if hm1[x1+x][y1+y] and hm2[x2+x][y2+y]:return True
                    else:continue
            return False

        def fill(self, value):
            for x in xrange(self.get_width()):
                for y in xrange(self.get_height()):
                    self.set_at((x, y), value)

        def collidemask(self, other):
            return self.overlap(other)

        def colliderect(self, rect):
            new = Mask(rect.size, rect.topleft)
            new.fill(1)
            return self.collidemask(new)

        def collidepoint(self, point):
            new = pygame.Rect(point, (1,1))
            new.topleft = point
            return self.colliderect(new)

        def overlap_area(self, other):
            offset = sub_vector(other.pos, self.pos)
            rect1 = pygame.Rect((0,0), self.get_size())
            rect2 = pygame.Rect(offset, other.get_size())
            rect=rect1.clip(rect2)
            if rect.width==0 or rect.height==0:
                return 0
            x1,y1,x2,y2 = rect.x-rect1.x,rect.y-rect1.y,rect.x-rect2.x,rect.y-rect2.y
            hm1 = self.data
            hm2 = other.data
            num = 0
            for x in xrange(rect.width):
                for y in xrange(rect.height):
                    if hm1[x1+x][y1+y] and hm2[x2+x][y2+y]:
                        num += 1
            return num

        def get_bounding_rects(self):
            cur = []
            d = self.data
            for x in xrange(self.get_width()):
                for y in xrange(self.get_height()):
                    if d[x][y]:
                        cur.append(pygame.Rect(x, y, 1, 1))
            #first check collisions moving left...
            new = []
            for i in cur:
                used = False
                for x in new:
                    if i.top == x.top and i.left == x.right:
                        new.remove(x)
                        x = x.union(i)
                        new.append(x)
                        used = True
                        break
                if not used:
                    new.append(i)
            cur = new
            new = []
            for i in cur:
                used = False
                for x in new:
                    if i.left == x.left and i.right == x.right and\
                       i.top == x.bottom:
                        new.remove(x)
                        x = x.union(i)
                        new.append(x)
                        used = True
                        break
                if not used:
                    new.append(i)
            return new

        def get_color_coded_image(self, col_0=[255,0,0], col_1=[0,255,0]):
            c = [col_0, col_1]
            new = pygame.Surface(self.get_size()).convert()
            for x in xrange(self.get_width()):
                for y in xrange(self.get_height()):
                    new.set_at((x, y), c[self.get_at((x, y))])
            return new

        def get_array(self):
            return self.data

        def from_array(self, array):
            size = len(array), len(array[0])
            self.size = size
            self.data = array

def from_surface(surface, threshold=127):
    key = surface.get_colorkey()
    if key:
        new = Mask(surface.get_size())
        for x in xrange(surface.get_width()):
            for y in xrange(surface.get_height()):
                new.set_at((x, y), surface.get_at((x, y)) != key)
        return new
    mask = Mask(surface.get_size())
    for x in xrange(surface.get_width()):
        for y in xrange(surface.get_height()):
            a = surface.get_at((x,y))
            if len(a) == 4:
                mask.set_at((x, y), int(a[3] > threshold))
            else:
                mask.set_at((x, y), 1)
    return mask

def from_array(array):
    new = Mask((1,1))
    new.from_array(array)
    return new

def quick_check(surf1, rect1, surf2, rect2, blk1=None, blk2=None):
    r = rect1.clip(rect2)
    if 0 in r.size:
        return False
##    r.left = rect1.right - r.width
##    r.top = rect1.bottom - r.height
    x1 = r.left - rect1.left
    x2 = r.left - rect2.left
    y1 = r.top - rect1.top
    y2 = r.top - rect2.top
    if not blk1:
        blk1 = surf1.get_at((0,0))
    if not blk2:
        blk2 = surf2.get_at((0,0))
    for x in xrange(r.width):
        for y in xrange(r.height):
            if surf1.get_at((x+x1, y+y1)) != blk1 and\
               surf2.get_at((x+x2, y+y2)) != blk2:
                return True
    return False
