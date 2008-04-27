import pygame
from pygame.locals import *

import image #from pyglibs!
import mask #from pyglibs!

class App(object):
    def __init__(self, surface):
        self.surface = surface
        self.widgets = []
        self.dirty_rects = []

        self.theme = None

    def get_events(self):
        return pygame.event.get()

    def get_mouse_pos(self):
        return pygame.mouse.get_pos()

    def add_widget(self, widg):
        self.widgets.insert(0, widg)

    def update(self):
        for i in self.widgets:
            #only render the widgets at the dirty spots!
            i.render(self.surface, self.dirty_rects)

class Widget(object):
    def __init__(self, parent, theme_val="Widget",
                 pos=(-1, -1), widget_pos="topleft",
                 use_pp=False):
        self.parent = parent

        self.theme_val = theme_val
        self.theme = self.parent.theme

        self.use_theme = self.theme[self.theme_val]

        self.dirty = False

        x, y = pos
        if x == -1:
            x = int(self.parent.surface.get_width() / 2)
        if y == -1:
            y = int(self.parent.surface.get_height() / 2)
        self.pos = x, y

        self.widget_pos = widget_pos

        self.use_pp = use_pp

        self.__make_rect__()

    def __make_rect__(self):
        if not "surface" in self.__dict__:
            self.surface = pygame.Surface((1, 1)).convert()
        if not "rect" in self.__dict__:
            self.rect = pygame.Rect(0,0,1,1)
        else:
            self.rect = self.surface.get_rect()

        if self.use_pp:
            #make sure this pygame 1.8
            self.hitmask = mask.from_surface(self.surface)
