import grid, image, mask, rect

import pygame
from pygame.locals import *


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

class Tile(object):
    def __init__(self, world, pos, tile_sheet,
                 type, tile_pos):
        self.world = world

        self.pos = pos
        self.tile_pos = tile_pos

        self.type = type

        self.tile_sheet = tile_sheet
        self.image = self.tile_sheet.tile
        self.comp_image = self.image.copy()

        self.blank_color = self.image.get_at((0,0))

        self.rect = self.image.get_rect()
        self.rect.midtop = self.pos

    def get_transitions(self):
        tl1, tl2, z=self.world.grid.get_tile_left(*self.tile_pos)
        tr1, tr2, z=self.world.grid.get_tile_right(*self.tile_pos)
        tt1, tt2, z=self.world.grid.get_tile_top(*self.tile_pos)
        tb1, tb2, z=self.world.grid.get_tile_bottom(*self.tile_pos)

        c_image = pygame.Surface((self.rect.width,
                    self.rect.height+self.world.grid.tile_size[2]*self.tile_pos[2])).convert_alpha()
        c_image.fill((0,0,0,0))
        c_image.blit(self.image, (0,0))

        if tl1>=0 and tl1<self.world.map_width and\
           tl2>=0 and tl2<self.world.map_height:
            a=self.world.tile_grid[tl1][tl2]
            if not a.type == self.type:
                a=a.tile_sheet.trans_left
                if a: c_image.blit(a, (0,0))

        if tr1>=0 and tr1<self.world.map_width and\
           tr2>=0 and tr2<self.world.map_height:
            a=self.world.tile_grid[tr1][tr2]
            if not a.type == self.type:
                a=a.tile_sheet.trans_right
                if a: c_image.blit(a, (0,0))

        if tt1>=0 and tt1<self.world.map_width and\
           tt2>=0 and tt2<self.world.map_height:
            a=self.world.tile_grid[tt1][tt2]
            if not a.type == self.type:
                a=a.tile_sheet.trans_top
                if a: c_image.blit(a, (0,0))

        if tb1>=0 and tb1<self.world.map_width and\
           tb2>=0 and tb2<self.world.map_height:
            a=self.world.tile_grid[tb1][tb2]
            if not a.type == self.type:
                a=a.tile_sheet.trans_bottom
                if a: c_image.blit(a, (0,0))

        if self.tile_sheet.cliff:
            off = int(self.world.tile_size[1] / 2)
            z = self.world.tile_size[2]
            for i in xrange(self.tile_pos[2]):
                c_image.blit(self.tile_sheet.cliff,
                             (0, off + z * i))
        self.comp_image = c_image
        self.rect = self.comp_image.get_rect()
        self.rect.midtop = self.pos
        self.blank_color = self.comp_image.get_at((0,0))

    def render(self, surface, rects, camera_pos=(0,0)):
        #only render on the dirty rects!
        x, y = self.rect.topleft
        x -= camera_pos[0]
        y -= camera_pos[1]
        for i in rects:
            image.push_clip(surface, i)
            surface.blit(self.image, (x, y))
            image.pop_clip(surface)

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
        if int(a.tile_pos[1])<int(b.tile_pos[1]):
            return -1
        elif int(a.tile_pos[1])>int(b.tile_pos[1]):
            return 1

        elif int(a.tile_pos[0])<int(b.tile_pos[0]):
            return -1
        elif int(a.tile_pos[0])>int(b.tile_pos[0]):
            return 1

        elif a.render_priority>b.render_priority:
            return 1
        elif a.render_priority<b.render_priority:
            return -1
        return 0

    def get_mouse_pos(self, mouse_pos=None):
        if not mouse_pos:
            mx, my=pygame.mouse.get_pos()
        else:
            mx, my=mouse_pos

        cpos=self.camera_pos
        mx -= cpos[0]
        my -= cpos[1]

        d=self.world.comp_tiles

        for x in range(len(d)):
            c=d[x]
            if c.rect.collidepoint((mx, my)):
                nmx, nmy = mx-c.rect.left, my-c.rect.top

                if not c.image.get_at((nmx, nmy)) == c.blank_color:
                    return c.tile_pos
        return None

    def render(self, surface):
        image.push_clip(surface, self.rect)

        r=pygame.Rect(self.camera_pos,
                      self.rect.size)

        big=[]
        big.extend(self.world.get_tiles_in_area(r))
        units = self.world.get_units_in_area(r)
        dirty_rects = []
        for i in units:
            if i.dirty and not self.dirty:
                i.dirty = False
                dirty_rects.append(i.rect)
        big.extend(units)

        big.sort(self.mysort)

        if self.dirty:
            self.dirty = False
            dirty_rects.append(surface.get_rect())

        for i in big:
            i.render(surface, dirty_rects, self.camera_pos)

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

        self.grid = grid.Grid(tile_size, grid_mode)

        self.tiles = tiles
        self.comp_tiles = []
        self.tile_grid = []

        self.build_map()

        self.units = []

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

    def render(self, surface):
        self.camera.render(surface)
