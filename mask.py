import pygame
from pygame.locals import *

try:
    from pygame import mask
    use_pygame = True
except:
    use_pygame = False

class Mask(object):
    def __init__(self, size):
        if use_pygame:
            pygame.mesh.Mask.__init__(self, size)
        else:
            mask = []
            for x in xrange(size[0]):
                mask.append([])
                for y in xrange(size[1]):
                    mask[x].append(0)

            self.data = mask
            self.size = size

    def get_size(self):
        if use_pygame:
            return pygame.mesh.Mesh.get_size(self)
        return self.size

    def get_width(self):
        if use_pygame:
            return pygame.mesh.Mesh.get_size(self)[0]
        return self.size[0]

    def get_height(self):
        if use_pygame:
            return pygame.mesh.Mesh.get_size(self)[1]
        return self.size[1]

    def get_at(self, pos):
        if use_pygame:
            return pygame.mesh.Mesh.get_at(pos)
        return self.data[pos[0]][pos[1]]

    def set_at(self, pos, value):
        if use_pygame:
            return pygame.mesh.Mesh.set_at(pos, value)
        self.data[pos[0]][pos[1]] = value

    def overlap(self, other, offset):
        if use_pygame:
            return pygame.mesh.Mesh.overlap(self, other, offset)
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

    def collidemask(self, other, offset):
        return self.overlap(other, offset)

    def colliderect(self, rect, offset):
        new = Mesh(rect.size)
        new.fill(1)
        return self.collidemask(new, offset)

    def collidepoint(self, point, offset):
        return self.colliderect(pygame.Rect(point, (1,1)), offset)

    def overlap_area(self, other, offset):
        if use_pygame:
            return pygame.mesh.Mesh.overlap_area(self, other, offset)
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
        if use_pygame:
            return pygame.mesh.Mesh.get_bounding_rects(self)
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
        if use_pygame:
            new = []
            for x in xrange(self.get_width()):
                new.append([])
                for y in xrange(self.get_height()):
                    new[x].append(self.get_at((x, y)))
            return new
        return self.data

    def from_array(self, array):
        size = len(array), len(array[0])
        if use_pygame:
            if not size == self.get_size():
                self = Mask(size)
            for x in xrange(len(array)):
                for y in xrange(len(array[0])):
                    self.set_at((x, y), array[x][y])
            return
        self.size = size
        self.data = array

def from_surface(surface, threshold=127):
    if use_pygame:
        key = surface.get_colorkey()
        if key:
            new = Mesh(surface.get_size())
            for x in xrange(surface.get_width()):
                for y in xrange(surface.get_height()):
                    new.set_at((x, y), surface.get_at((x, y)) != key)
            return new
    mask = Mask(surface.get_size())
    for x in xrange(surface.get_width()):
        for y in xrange(surface.get_height()):
            a = surface.get_at((x,y))
            if len(a) == 4:
                mask.set_at((x, y), int(a[3] > alpha))
            else:
                mask.set_at((x, y), 1)
    return mask

def from_array(array):
    new = Mask((1,1))
    new.from_array(array)
    return new
