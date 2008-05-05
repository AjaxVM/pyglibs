import grid, image, mask, rect

import pygame
from pygame.locals import *


class QuadLeaf(object):
    def __init__(self, pos, size):
        self.pos = pos[0] * size[0], pos[1] * size[1]
        self.size = size

        self.rect = pygame.Rect(self.pos, self.size)

        self.obj = []

    def mysort(self, a, b):
        if a.tile_depth < b.tile_depth:
            return 1
        elif a.tile_depth > b.tile_depth:
            return -1
        elif int(a.tile_pos[1])<int(b.tile_pos[1]):
            return -1
        elif int(a.tile_pos[1])>int(b.tile_pos[1]):
            return 1

        elif int(a.tile_pos[0])<int(b.tile_pos[0]):
            return -1
        elif int(a.tile_pos[0])>int(b.tile_pos[0]):
            return 1

        elif a.render_priority < b.render_priority:
            return -1
        return 1

    def update_list(self):
        self.obj.sort(self.mysort)

    def update_item(self, obj):
        if self.rect.colliderect(obj.rect):
            if not obj in self.obj:
                self.obj.append(obj)
            self.update_list()
        else:
            if obj in self.obj:
                if self in obj.quads_in:
                    obj.quads_in.remove(self)
                self.obj.remove(obj)

class QuadTree(object):
    def __init__(self, size, leaf_size=(10, 10)):
        self.size = size
        self.leaf_size = leaf_size

        self.make_grid()

    def make_grid(self):
        cur = []
        for x in xrange(self.size[0]):
            cur.append([])
            for y in xrange(self.size[1]):
                cur[x].append(QuadLeaf((x, y), self.leaf_size))
        self.leaves = cur

    def add_item(self, item):
        mx = int(item.rect.left / self.leaf_size[0])
        my = int(item.rect.top / self.leaf_size[1])
        x = int(item.rect.right / self.leaf_size[0])
        y = int(item.rect.bottom / self.leaf_size[1])
        inside = []
        for _x in xrange(x - mx + 1):
            for _y in xrange(y - my + 1):
                nx = mx + _x
                ny = my + _y
                if nx >= 0 and nx < self.size[0] and\
                   ny >= 0 and ny < self.size[1]:
                    inside.append(self.leaves[mx + _x][my + _y])

        for i in inside:
            i.update_item(item)
        item.quads_in = inside

    def update_item(self, item):
        mx = int(item.rect.left / self.leaf_size[0])
        my = int(item.rect.top / self.leaf_size[1])
        x = int(item.rect.right / self.leaf_size[0])
        y = int(item.rect.bottom / self.leaf_size[1])
        inside = []
        for _x in xrange(x - mx + 1):
            for _y in xrange(y - my + 1):
                nx = mx + _x
                ny = my + _y
                if nx >= 0 and nx < self.size[0] and\
                   ny >= 0 and ny < self.size[1]:
                    l = self.leaves[mx + _x][my + _y]
                    if not l in item.quads_in:
                        inside.append(self.leaves[mx + _x][my + _y])
        item.quads_in.extend(inside)

        for i in inside:
            i.update_item(item)


class QuadNode(object):
    def __init__(self, rect, tree):
        self.rect = rect
        self.tree = tree

        self.quads_in = []
        self.tree.add_item(self)

    def update_quads(self):
        self.tree.update_item(self)

    def get_objects_in_quads(self):
        cur = []
        for i in self.quads_in:
            for x in i.obj:
                if not x in cur:
                    cur.append(x)
        return cur


class TileSet(object):
    def __init__(self, surf, split_size):
        self.sheet = image.split_image_by_cells(surf, split_size).frames
        #we only use the first level of frames right now
        #other frames can be used for animations :)

        self.tile = self.sheet[0][0]
        if len(self.sheet) > 1:
            self.trans_left = self.sheet[0][1]
        else:
            self.trans_left = None
        if len(self.sheet) > 2:
            self.trans_right = self.sheet[0][2]
        else:
            self.trans_right = None
        if len(self.sheet) > 3:
            self.trans_top = self.sheet[0][3]
        else:
            self.trans_top = None
        if len(self.sheet) > 4:
            self.trans_bottom = self.sheet[0][4]
        else:
            self.trans_bottom = None

        if len(self.sheet) > 5:
            self.cliff = self.sheet[0][5]
        else:
            self.cliff = None

class Tile(QuadNode):
    def __init__(self, world, pos, tile_sheet,
                 type, tile_pos):
        self.world = world

        self.pos = pos
        self.tile_pos = tile_pos

        self.get_tile_depth()

        self.type = type

        self.tile_sheet = tile_sheet
        self.image = self.tile_sheet.tile
        self.comp_image = self.image.copy()

        self.rect = self.image.get_rect()
        self.rect.midtop = self.pos

        self.render_priority = 0

        QuadNode.__init__(self, self.rect, self.world.quad)
        self.dirty_rect = pygame.Rect(self.rect)

    def get_tile_depth(self):
        self.tile_depth = self.world.map[int(self.tile_pos[0])]\
                          [int(self.tile_pos[1])][1]

    def get_transitions(self):
        tl1, tl2, z=self.world.grid.get_tile_left(*self.tile_pos)
        tr1, tr2, z=self.world.grid.get_tile_right(*self.tile_pos)
        tt1, tt2, z=self.world.grid.get_tile_top(*self.tile_pos)
        tb1, tb2, z=self.world.grid.get_tile_bottom(*self.tile_pos)

        check = {}
        c2 = []

        check["main"] = self.type
        c2.append(self.image)
        

        if tl1>=0 and tl1<self.world.map_width and\
           tl2>=0 and tl2<self.world.map_height:
            a=self.world.tile_grid[tl1][tl2]
            if not a.type == self.type:
                check["left"] = a.type
                c2.append(a.trans_right)
            else:
                check["left"] = None
                c2.append(None)

        if tr1>=0 and tr1<self.world.map_width and\
           tr2>=0 and tr2<self.world.map_height:
            a=self.world.tile_grid[tr1][tr2]
            if not a.type == self.type:
                check["right"] = a.type
                c2.append(a.trans_left)
            else:
                check["right"] = None
                c2.append(None)

        if tb1>=0 and tb1<self.world.map_width and\
           tb2>=0 and tb2<self.world.map_height:
            a=self.world.tile_grid[tb1][tb2]
            if not a.type == self.type:
                check["bottom"] = a.type
                c2.append(a.trans_top)
            else:
                check["bottom"] = None
                c2.append(None)

        if tt1>=0 and tt1<self.world.map_width and\
           tt2>=0 and tt2<self.world.map_height:
            a=self.world.tile_grid[tt1][tt2]
            if not a.type == self.type:
                check["top"] = a.type
                c2.append(a.trans_bottom)
            else:
                check["top"] = None
                c2.append(None)

        check = str(check)

        if check in self.world.compiled_tile_images:
            self.comp_image = self.world.compiled_tile_images[check]
        else:
            self.comp_image = pygame.Surface(self.rect.size).convert_alpha()
            self.comp_image.fill((0,0,0,0))
            for i in c2:
                if i:
                    self.comp_image.blit(i, (0,0))
            self.world.compiled_tile_images[check] = self.comp_image

    def render(self, surface, rects, camera_pos=(0,0)):
        #only render on the dirty rects!
        x, y = self.rect.topleft
        x -= camera_pos[0]
        y -= camera_pos[1]
        for i in rects:
            image.push_clip(surface, i)
            surface.blit(self.comp_image, (x, y))
            image.pop_clip(surface)

    def collidepoint(self, x, y):
        if self.rect.collidepoint((x, y)):
            x = self.rect.right - x - 1
            y = self.rect.bottom - y - 1
            if self.comp_image.get_at((x, y)) != (0,0,0,0):
                return True
        return False

    def dirty(self):
        self.dirty_rect = pygame.Rect(self.rect)
        self.world.dirty_rects.append(self)

class Camera(object):
    def __init__(self, world, camera_pos=[0,0],
                 view_rect=None,
                 lock_to_map=True):
        self.camera_pos=camera_pos

        self.rect=view_rect

        self.lock_to_map=lock_to_map

        self.world=world
        self.dirty = True

    def to_tile_pos(self, pos=[0,0]):
        x, y = pos
        if self.lock_to_map:
            if x<0:
                x=0
            if x>=self.world.map_width:
                x=self.world.map_width
            if y<0:
                y=0
            if y>=self.world.map_height:
                y=self.world.map_height

        x, y = -x, -y

        self.camera_pos=self.world.get_pos(x, y)
        self.dirty = True

    def center_at(self, pos=[0,0]):
        if isinstance(self.rect, pygame.Rect):
            w, h, = self.rect.width/2, self.rect.height/2

            self.camera_pos[0]=-pos[0]+w
            self.camera_pos[1]=-pos[1]+h
            self.dirty = True
        else:
            raise "Camera.rect must be a python.Rect object",AttributeError()

    def mysort(self, a, b):
        if a.tile_depth < b.tile_depth:
            return -1
        elif a.tile_depth > b.tile_depth:
            return 1
        elif int(a.tile_pos[1])<int(b.tile_pos[1]):
            return -1
        elif int(a.tile_pos[1])>int(b.tile_pos[1]):
            return 1

        elif int(a.tile_pos[0])<int(b.tile_pos[0]):
            return -1
        elif int(a.tile_pos[0])>int(b.tile_pos[0]):
            return 1

        elif a.render_priority < b.render_priority:
            return -1
        return 1

    def mysort2(self, a, b):
        return -self.mysort(a, b)

    def get_mouse_pos(self, mouse_pos=None):
        if not mouse_pos:
            mx, my=pygame.mouse.get_pos()
        else:
            mx, my=mouse_pos

        cpos=self.camera_pos
        mx += cpos[0]
        my += cpos[1]
        r = pygame.Rect(self.camera_pos, self.rect.size)
        big = self.world.get_tiles_in_area(r)
        big.extend(self.world.get_units_in_area(r))

        big.sort(self.mysort2)

        for i in big:
            if i.collidepoint(mx, my):
                if isinstance(i, Unit):
                    return i.pos, i
                else:
                    return i.tile_pos[0:2], i

    def render(self, surface):
        image.push_clip(surface, self.rect)

        r=pygame.Rect(self.camera_pos,
                      self.rect.size)

        if self.dirty:
            image.push_clip(surface, r)
            surface.fill((255,255,255))
            image.pop_clip(surface)
            self.dirty = False
            for i in self.world.dirty_rects:
                i.dirty_rect = None
            self.world.dirty_rects = []
            for i in self.world.get_tiles_in_area(r) +\
                self.world.get_units_in_area(r):
                i.render(surface, [r], self.camera_pos)
        elif self.world.dirty_rects:
            big = []
            rects = []

            for i in self.world.dirty_rects: #get objects, tiles + units
                rects.append(i.dirty_rect)
                image.push_clip(surface, i.dirty_rect)
                surface.fill((255,255,255))
                image.pop_clip(surface)
                for x in i.get_objects_in_quads():
                    if not x in big:
                        big.append(x)

            big.sort(self.mysort)

            for obj in big:
                obj.render(surface, rects, self.camera_pos)
            for i in self.world.dirty_rects:
                i.dirty_rect = None
            self.world.dirty_rects = []

        image.pop_clip(surface)

class World(object):
    def __init__(self, map=None, tiles={},
                 tile_size=[32, 16, 16],
                 grid_mode=grid.Square,
                 camera_pos=[0,0],
                 camera_view_rect=pygame.Rect(0,0,640,480),
                 camera_lock_to_map=True):
        self.camera = Camera(self, camera_pos, camera_view_rect,
                             camera_lock_to_map)
        self.map = map
        if not map:
            self.map = [[]]
        self.map_width = len(self.map)
        self.map_height = len(self.map[0])

        self.quad = QuadTree((self.map_width, self.map_height),
                             tile_size[0:2])

        self.grid = grid.Grid(tile_size, grid_mode)

        self.tiles = tiles
        self.comp_tiles = []
        self.tile_grid = []
        self.compiled_tile_images = {}

        self.build_map()

        self.units = []

        self.dirty_rects = []

    def build_map(self):
        g = []
        map = self.map
        w, h = self.map_width, self.map_height
        for x in xrange(w):
            cur = []
            for y in xrange(h):
                mp = self.map[x][y]
                n = Tile(self, self.grid.convert_map_pos(x, y, mp[1]),
                         self.tiles[mp[0]], mp[0],
                         (x, y, mp[1]))
                self.comp_tiles.append(n)
                cur.append(n)
            g.append(cur)
        self.tile_grid = g
        for i in self.comp_tiles:
            i.get_transitions()

    def get_tiles_in_area(self, rect):
        cur = []
        for i in self.comp_tiles:
            if i.rect.colliderect(rect):
                cur.append(i)
        return cur

    def get_units_in_area(self, rect):
        cur = []
        for i in self.units:
            if i.rect.colliderect(rect):
                cur.append(i)
        return cur

    def get_mouse_pos(self, pos=None):
        return self.camera.get_mouse_pos(pos)

    def render(self, surface):
        self.camera.render(surface)


class Unit(QuadNode):
    def __init__(self, world, image, pos=(0,0),
                 lock_to_map=True, mask=None,
                 render_priority=1):
        self.world = world
        self.world.units.append(self)

        self.image = image
        self.tile_pos = pos
        self.get_tile_depth()
        self.rect = self.image.get_rect()
        self.rect.midbottom = self.world.grid.convert_unit_pos(*self.tile_pos)
        self.mask = mask
        if self.mask:
            self.hitmask = rect.RectMaskCombo(self.rect, self.mask)
        else:
            self.hitmask = None

        self.render_priority = render_priority

        QuadNode.__init__(self, self.rect, self.world.quad)
        self.dirty_rect = pygame.Rect(self.rect)

    def get_tile_depth(self):
        self.tile_depth = self.world.map[int(self.tile_pos[0])]\
                          [int(self.tile_pos[1])][1] + 0.5

    def move(self, x, y):
        self.dirty()
        px, py = self.tile_pos
        px += x
        py += y
        self.tile_pos = (px, py)
        olr = pygame.Rect(self.rect)
        self.rect.midbottom = self.world.grid.convert_unit_pos(*self.tile_pos)
        olr.union_ip(self.rect)
        if self.dirty_rect:
            olr.union_ip(self.dirty_rect)
        self.dirty_rect = olr
        self.get_tile_depth()
        if self.mask:
            self.hitmask.rect = self.rect

        self.update_quads()

    def collidepoint(self, x, y):
        if self.hitmask:
            return self.hitmask.collidepoint((x, y))
        return self.rect.collidepoint((x, y))

    def render(self, surface, rects, camera_pos=[0,0]):
        x, y = self.rect.topleft
        x -= camera_pos[0]
        y -= camera_pos[1]
        for i in rects:
            image.push_clip(surface, i)
            surface.blit(self.image, (x, y))
            image.pop_clip(surface)

    def dirty(self):
        if not self.dirty_rect:
            self.dirty_rect = pygame.Rect(self.rect)
        self.world.dirty_rects.append(self)
