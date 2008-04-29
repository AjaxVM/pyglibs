import pygame
from pygame.locals import *

import image #from pyglibs!
import mask #from pyglibs!
import rect #again...
import theme as pygTheme#...
from misc import careful_div
import constants

class Cursor(object):
    def __init__(self):
        self.arrow = pygame.cursors.arrow
        self.mouse = self.load_cursor_from_image("mouse_cursor.bmp")

    def set_cursor(self, name):
        pygame.mouse.set_cursor(*getattr(self, name))

    def load_cursor_from_image(self, filename):
        i = pygame.image.load(constants.get_path(filename))
        i = pygame.transform.flip(i, True, False)
        i = pygame.transform.rotate(i, 90)
        size = i.get_size()
        cur = []
        for x in xrange(size[0]):
            n = ""
            for y in xrange(size[1]):
                val = i.get_at((x, y))[0:3]
                if val == (0, 0, 0):
                    n = n + "X"
                elif val == (255, 0, 0):
                    n = n + "."
                else:
                    n = n + " "
            cur.append(n)
        return (size, (0,0)) + pygame.cursors.compile(cur)

class App(object):
    def __init__(self, surface, bg_color=None,
                 theme=None):
        self.surface = surface
        self.widgets = []
        self.rev_widgets = []
        self.dirty_rects = []

        self.bg_color = bg_color

        self.cursor = Cursor()

        if theme:
            self.theme = theme
        else:
            self.theme = pygTheme.get_default_theme()

    def get_events(self):
        reset = True
        for i in self.widgets:
            if i.update():
                reset = False
                break
        if reset:
            self.set_mouse_hover(False)
        send = []
        for e in pygame.event.get():
            ret = e
            for i in self.widgets:
                ret = i.event(e)
                if not ret == e:
                    break
            send.append(ret)
        return send

    def get_mouse_pos(self):
        return pygame.mouse.get_pos()

    def add_widget(self, widg):
        self.widgets.insert(0, widg)
        self.rev_widgets.append(widg)

    def get_cursor(self):
        return self.cursor

    def set_mouse_hover(self, val=True):
        self.cursor.set_cursor(["arrow", "mouse"][int(val)])

    def bring_to_top(self, widg):
        try:
            self.widgets.remove(widg)
            self.rev_widgets.remove(widg)
        except:
            pass
        self.widgets.insert(0, widg)
        self.rev_widgets.append(widg)

    def update(self):
        #clear the screen where we want to render!
        if self.bg_color:
            for i in self.dirty_rects:
                new = self.surface.subsurface(i)
                new.fill(self.bg_color)
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

    def set_font(self, fontname, size):
        self.font = pygame.font.Font(fontname, size)

    def get_cursor(self):
        return self.parent.get_cursor()

    def set_mouse_hover(self, val=True):
        self.parent.set_mouse_hover(val)

    def make_rect(self):
        self.rect = self.surface.get_rect()
        self.move()
        if self.use_pp:
            self.hitmask = rect.RectMaskCombo(self.rect, mask.from_surface(self.surface))

    def update(self):
        pass

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
        return self.rect.collide_point(point)

    def colliderect(self, rect):
        if self.use_pp:
            return self.hitmask.colliderect(rect)
        return self.rect.collide_rect(rect)

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

        self.font = self.use_theme["font"]
        self.font_color = self.use_theme["font_color"]
        self.font_aa = self.use_theme["font_aa"]

        self.bg_image = self.use_theme["image"]

        self.make_image()
        self.set_render()

    def make_image(self):
        self.surface = self.font.render(self.text,
                                        self.font_aa,
                                        self.font_color)
        if self.bg_image and not self.bg_image == "noimage":
            new = image.resize_tile(self.bg_image, self.surface.get_size())
            a = self.surface
            new.blit(a, (int(careful_div(new.get_width() - a.get_width(), 2)),
                         int(careful_div(new.get_height() - a.get_height(), 2))))
            self.surface = new
        self.make_rect()
        self.move()


class Button(Widget):
    def __init__(self, parent, name, text, pos=(-1,-1), widget_pos="topleft"):
        Widget.__init__(self, parent, name, "Button", pos, widget_pos, True)

        self.text = text

        self.font = self.use_theme["font"]
        self.font_color_regular = self.use_theme["font_color_regular"]
        self.font_color_hover = self.use_theme["font_color_hover"]
        self.font_color_click = self.use_theme["font_color_click"]
        self.font_aa = self.use_theme["font_aa"]

        self.bg_regular = self.use_theme["image_regular"]
        self.bg_hover = self.use_theme["image_hover"]
        self.bg_click = self.use_theme["image_click"]

        self.make_image()
        self.set_render()

        self.clicked = False
        self.hover = False

    def make_image(self):
        self.surf_regular = self.font.render(self.text,
                                             self.font_aa,
                                             self.font_color_regular)
        if self.bg_regular and not self.bg_regular == "noimage":
            new = image.resize_tile(self.bg_regular, self.surf_regular.get_size())
            a = self.surf_regular
            new.blit(a, (int(careful_div(new.get_width() - a.get_width(), 2)),
                         int(careful_div(new.get_height() - a.get_height(), 2))))
            self.surf_regular = new
        self.surf_hover = self.font.render(self.text,
                                           self.font_aa,
                                           self.font_color_hover)
        if self.bg_hover and not self.bg_hover == "noimage":
            new = image.resize_tile(self.bg_hover, self.surf_hover.get_size())
            a = self.surf_hover
            new.blit(a, (int(careful_div(new.get_width() - a.get_width(), 2)),
                         int(careful_div(new.get_height() - a.get_height(), 2))))
            self.surf_hover = new
        self.surf_click = self.font.render(self.text,
                                           self.font_aa,
                                           self.font_color_click)
        if self.bg_click  and not self.bg_click  == "noimage":
            new = image.resize_tile(self.bg_click , self.surf_click .get_size())
            a = self.surf_click
            new.blit(a, (int(careful_div(new.get_width() - a.get_width(), 2)),
                         int(careful_div(new.get_height() - a.get_height(), 2))))
            self.surf_click  = new

        self.surface = self.surf_regular
        self.make_rect()
        self.move()

    def swap_surface(self, image):
        if not self.surface == image:
            self.surface = image
            self.set_render()

    def update(self):
        if self.hover:
            self.set_mouse_hover()
            return True

    def event(self, event):
        if not self.clicked:
            self.swap_surface(self.surf_regular)
        else:
            self.swap_surface(self.surf_click)
        if self.collidepoint(self.get_mouse_pos()):
            self.hover = True
            self.set_mouse_hover()
            if not self.clicked:
                self.swap_surface(self.surf_hover)
            if event.type == MOUSEBUTTONDOWN:
                self.clicked = True
                self.swap_surface(self.surf_click)
            if event.type == MOUSEBUTTONUP:
                ret = Event(Button, self.name)
                self.clicked = False
                self.swap_surface(self.surf_hover)
                return ret
        else:
            self.hover = False
            if event.type == MOUSEBUTTONUP:
                self.clicked = False
                self.swap_surface(self.surf_regular)
        return event

class IconButton(Button):
    def __init__(self, parent, name,
                 image_regular, image_hover, image_click,
                 pos=(-1,-1), widget_pos="topleft"):
        Button.__init__(self, parent, name, "", pos, widget_pos)
        for i in [self.text, self.font, self.font_color_regular, self.font_color_hover,
                  self.font_color_click, self.bg_regular, self.bg_hover, self.bg_click]:
            del i

        self.description = "IconButton"
        self.use_theme = self.theme[self.description]

        self.surf_regular = image_regular
        self.surf_hover = image_hover
        self.surf_click = image_click
        self.surface = self.surf_regular
        self.make_rect()
        self.move()

        self.set_render()

    def make_image(self):
        pass

    def event(self, event):
        ret = Button.event(self, event)
        if ret.type == GUI_EVENT:
            ret.widget = IconButton
        return ret
                
GUI_EVENT = "This is a string so we don't confuse Pygame ;)"
GUI_EVENT_CLICK = 0
GUI_EVENT_INPUT = 1
GUI_SCROLL_EVENT = 2

class Event(object):
    def __init__(self, widg=Widget, name="Name",
                 action=GUI_EVENT_CLICK):
        self.type = GUI_EVENT

        self.widget = widg
        self.name = name

        self.action = action
