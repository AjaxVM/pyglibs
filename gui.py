import pygame
from pygame.locals import *

import image #from pyglibs!
import mask #from pyglibs!
import rect #again...
import theme as pygTheme#...

class App(object):
    def __init__(self, surface, theme=None):
        self.surface = surface
        self.widgets = []
        self.rev_widgets = []
        self.dirty_rects = []

        if theme:
            self.theme = theme
        else:
            self.theme = pygTheme.get_default_theme()

    def get_events(self):
        return pygame.event.get()

    def get_mouse_pos(self):
        return pygame.mouse.get_pos()

    def add_widget(self, widg):
        self.widgets.insert(0, widg)
        self.rev_widgets.append(widg)

    def bring_to_top(self, widg):
        try:
            self.widgets.remove(widg)
            self.rev_widgets.remove(widg)
        except:
            pass
        self.widgets.insert(0, widg)
        self.rev_widgets.append(widg)

    def update(self):
        for i in self.rev_widgets:
            #only render the widgets at the dirty spots!
            i.render(self.surface, self.dirty_rects)
        self.dirty_rects = []

    def set_render(self, widg):
        self.dirty_rects.append(widg.rect)

class Widget(object):
    def __init__(self, parent, name, theme_val="Widget",
                 pos=(-1,-1), widget_pos="topleft",
                 use_pp=False):
        self.parent = parent
        self.parent.add_widget(self)

        self.name = name

        self.description = "Widget"

        self.theme_val = theme_val
        self.theme = self.parent.theme

        self.use_theme = self.theme[self.theme_val]

        x, y = pos
        if x == -1:
            x = int(self.parent.surface.get_width() / 2)
        if y == -1:
            y = int(self.parent.surface.get_height() / 2)
        self.pos = [x, y]

        self.widget_pos = widget_pos

        self.use_pp = use_pp

        self.__orig_surface = pygame.Surface((1,1))
        self.__orig_surface.fill((0,0,0))
        self.surface = self.__orig_surface.copy()

        self.over_width = self.surface.get_width()
        self.over_height = self.surface.get_height()

        self.make_rect()

        self.visible = True
        self.active = True

    def make_rect(self):
        self.rect = self.surface.get_rect()
        self.move()
        if self.use_pp:
            self.hitmask = rect.RectMaskCombo(self.rect, mask.from_surface(self.surface))

    def scale_surface(self):
        if not self.surface.get_size() == (self.over_width, self.over_height):
            self.surface = image.resize_tile(self.__orig_surface, (self.over_width,
                                                                   self.over_height),
                                             True)
            self.rect.size = self.over_width, self.over_height
            if self.use_pp:
                self.hitmask = rect.RectMaskCombo(self.rect, mask.from_surface(self.surface))

    def move(self, d=(0,0)):
        x, y = self.pos
        x += d[0]
        y += d[1]
        self.pos = [x, y]
        setattr(self.rect, self.widget_pos, self.pos)

    def event(self, e):
        return e

    def get_mouse_pos(self):
        return self.parent.get_mouse_pos()

    def set_render(self, widg=None):
        if widg == None:
            widg = self
        self.parent.set_render(widg)

    def render(self, surface, rects=None):
        if not self.visible and rects:
            return
        for i in rects:
            if self.rect.colliderect(i):
                image.push_clip(surface, self.rect.clip(i))
                surface.blit(self.surface, self.rect)
                image.pop_clip(surface)

    def collidepoint(self, point):
        if self.use_pp:
            return self.hitmask.collidepoint(point)
        return self.rect.collidepoint(point)

    def colliderect(self, rect):
        if self.use_pp:
            return self.hitmask.colliderect(rect)
        return self.rect.colliderect(rect)

    def collidemask(self, mask):
        if self.use_pp:
            return self.hitmask.collidemask(mask)
        return False

    def checkcollision(self, other):
        if isinstance(other, ()) or isinstance(other, []):
            return self.collidepoint(other)
        if isinstance(other, pygame.Rect):
            return self.colliderect(other)
        return self.collidemask(other)

    def make_image(self):
        pass

class Label(Widget):
    def __init__(self, parent, name, text, pos=(-1,-1), widget_pos="topleft"):
        Widget.__init__(self, parent, name, "Label", pos, widget_pos, False)

        self.text = text

        self.font = pygame.font.Font(self.use_theme["font"]["name"],
                                     self.use_theme["font"]["size"])
        self.font_color = self.use_theme["font"]["color"]
        self.font_aa = self.use_theme["font"]["aa"]

        self.make_image()
        self.set_render()

    def make_image(self):
        self.surface = self.font.render(self.text,
                                        self.font_aa,
                                        self.font_color)
        self.make_rect()
        self.move()
