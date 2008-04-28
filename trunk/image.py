
import pygame
from pygame.locals import *

from misc import careful_div


def change_color(surface, a, b):
    """changes all instances of a in surface to b"""
    for y in xrange(surface.get_height()):
        for x in xrange(surface.get_width()):
            c=surface.get_at((x, y))
            if len(a)==3:
                if c[0]==a[0] and c[1]==a[1] and c[2]==a[2]:
                    surface.set_at((x, y), b)
            else:
                if c[0]==a[0] and c[1]==a[1] and c[2]==a[2] and c[3]==a[3]:
                    surface.set_at((x, y), b)
    return surface


def colorize(surface, base_color, to_color, threshold=0):
    """will colorize an image so that a color that is within threshold of base_color,
       will be modified to fit to_color

       surface must be a pygame.surface, original surface is not modified
       base_color must be a tuple of at least len 3, this represents an RGB/RGBA color
       to_color must be a tuple of at least len 3, this represents an RGB/RGBA color
       threshold is the amount of variation(+ or -) that will be allowed,
           set to 0 makes it only match the exact base_color"""
    width, height = surface.get_size()
    surf=surface.copy()
    for x in xrange(width):
        for y in xrange(height):
            a = tuple(surf.get_at((x, y)))
            if a[0]>=base_color[0]-threshold and a[0]<=base_color[0]+threshold and\
               a[1]>=base_color[1]-threshold and a[1]<=base_color[1]+threshold and\
               a[2]>=base_color[2]-threshold and a[2]<=base_color[2]+threshold:
                amount=careful_div(float(a[0]), 255)
                r=to_color[0]*amount
                g=to_color[1]*amount
                b=to_color[2]*amount
                if len(a)==4:
                    surf.set_at((x, y), (r, g, b, a[3]))
                else:
                    surf.set_at((x, y), (r, g, b))
    return surf


def load_surface(name, colorkey=None, alpha=None):
    """loads and returns a pygame.Surface object
       colorkey can be None if you want to disable it,
        -1 for the color at the topleft corner of the image,
        a tuple/list of 2 ints for a color at a specific pixel of the image,
        a tuple/list of 3 or 4 ints for a specific color,
        or a tuple/list of the previous, to apply multiple colorkeys.
       alpha can be None/False/0 to disable(faster rendering),
        True to enable and use per-pixel alpha,
        or an int for a full-surface alpha."""
    image=pygame.image.load(name).convert_alpha()
    if isinstance(alpha, int):
        image.set_alpha(alpha)

    if colorkey:
        ccs=[]
        if colorkey==-1:
            ccs.append(colorkey)
        elif type(colorkey[0]) is type(list()) or\
           type(colorkey[1]) is type(tuple()):
            for i in colorkey:
                ccs.append(i)
        else:
            ccs.append(colorkey)

        ncs=[]
        try:
            for i in ccs:
                if i == -1:
                    ncs.append(image.get_at((0,0)))
                elif len(i)==2:
                    ncs.append(image.get_at(i))
                elif len(i)==3 or len(i)==4:
                    ncs.append(i)
                else:
                    raise AttributeError, "Invalid colorkey: %s"%i
        except:
            raise AttributeError, "Invalid colorkey: %s"%i

        reg=ncs[0]

        for i in ncs:
            if not i==reg:
                image=change_color(image, i, reg)

        image.set_colorkey(reg, RLEACCEL)

    return image

def is_empty(surface, st_color=None):
    """returns whether all pixels of the surface are the same color
       surface must be a pygame.Surface
       st_color must be None - for the topleft color of surface, or an RGB/RGBA tuple"""
    if not st_color:st_color=surface.get_at((0,0))
    st_color=tuple(st_color)
    for x in xrange(surface.get_width()):
        for y in xrange(surface.get_height()):
            if not surface.get_at((x, y))[0:3] == st_color[0:3]:
                return False
    return True

def blit_ignore(surf_a, surf_b, dest):
    """will blit surf_b to surf_a using dest to offset by x=dest[0], y=dest[1]
       surf_a and surf_b must be pygame.Surface's
       will ignore colorkeys and alpha(good for copying images...)"""
    width, height=surf_b.get_size()
    w2, h2 = surf_a.get_size()
    for x in xrange(width):
        for y in xrange(height):
            nx, ny = x+dest[0], y+dest[1]
            if nx <= w2 and ny <= h2:
                surf_a.set_at((nx, ny), surf_b.get_at((x, y)))
    return surf_a

def clip_empty(surface, st_color=None):
    """returns a new surface that contains all data from surface or None if image is empty,
       but with the empty areas around the surface removed
       surface must be a pygame.Surface
       st_color must be None - for the topleft color of surface, or an RGB/RGBA tuple"""
    if is_empty(surface, st_color):
        return None
    minx=0
    miny=0
    maxx=0
    maxy=0
    if not st_color:st_color = surface.get_at((0,0))
    st_color=tuple(st_color)

    surf_width, surf_height = surface.get_size()

    for x in xrange(surf_width):
        empty=True
        for y in xrange(surf_height):
            if not surface.get_at((x, y))[0:3]==st_color[0:3]:
                empty=False
        if empty:
            minx+=1
        else:
            break
    for x in xrange(surf_width):
        empty=True
        for y in xrange(surf_height):
            if not surface.get_at((surf_width-x-1, y))[0:3]==st_color[0:3]:
                empty=False
        if empty:
            maxx-=1
        else:
            break

    for y in xrange(surf_height):
        empty=True
        for x in xrange(surf_width):
            if not surface.get_at((x, y))[0:3]==st_color[0:3]:
                empty=False
        if empty:
            miny+=1
        else:
            break
    for y in xrange(surf_height):
        empty=True
        for x in xrange(surf_width):
            if not surface.get_at((x, surf_height-y-1))[0:3]==st_color[0:3]:
                empty=False
        if empty:
            maxy-=1
        else:
            break

    a=pygame.transform.scale(surface.copy(), (surf_width+maxx-minx, surf_height+maxy-miny))
    a.fill((0,0,0))
    a=blit_ignore(a, surface, [-minx, -miny])
    return a

def get_size(surface, size, min_dimensions=True):
    """returns the size, no smaller than the image if min_dimensions is set to True"""
    if not min_dimensions:
        x, y = size
    else:
        x, y = size
        if x<surface.get_width():
            x=surface.get_width()
        if y<surface.get_height():
            y=surface.get_height()
    return x, y

def resize_scale(surface, size, min_dimensions=True):
    """will scale the surface using pygame.transform.scale.
       surface must be a pygame.Surface
       size must be a tuple or list of len 2, where it is (x size, y size)
       min_dimensions must be a bool
       when set to True, will not make any dimensions smaller
         than the current dimensions, when false it can be resized to anything"""
    return pygame.transform.scale(surface, get_size(surface, size, min_dimensions))

def resize_tile(surface, size, min_dimensions=True):
    """will scale a surface by cutting it into 9 pieces, placing the outer
       pieces along the outside and filling the center with the middle piece
       surface must be a pygame.Surface
       size must be a tuple or list of len 2, where it is (x size, y size)
       min_dimensions must be a bool
       when set to True, will not make any dimensions smaller
         than the current dimensions, when false it can be resized to anything"""
    surf=surface.copy()
    colorkey=surf.get_colorkey()#we need to store this and remove it for now,
                                #that way it will actually blit the colorkey values
                                #else it will change them all to black :(
    surf.set_colorkey(None)

    size=get_size(surface, size, min_dimensions)

    image=surf.copy()
    rect=image.get_rect()

    nw=int(rect.width/3)
    nh=int(rect.height/3)
    image=pygame.transform.scale(image, (nw*3, nh*3))

    topleft=image.subsurface([0,0], [nw, nh]).copy()
    midtop=image.subsurface([nw,0],[nw, nh]).copy()
    topright=image.subsurface([nw*2,0],[nw,nh]).copy()

    midleft=image.subsurface([0,nh], [nw, nh]).copy()
    center=image.subsurface([nw,nh], [nw,nh]).copy()
    midright=image.subsurface([nw*2,nh], [nw,nh]).copy()

    bottomleft=image.subsurface([0,nh*2], [nw, nh]).copy()
    midbottom=image.subsurface([nw,nh*2],[nw, nh]).copy()
    bottomright=image.subsurface([nw*2,nh*2],[nw,nh]).copy()

    width=(int(size[0]/nw)+1)*nw
    height=(int(size[1]/nh)+1)*nh

    num_x=(width/nw)-1
    num_y=(height/nh)-1

    surf=pygame.transform.scale(surf, (width, height))
    r=nsurf.get_rect()
    surf.fill((0,0,0,0))

    surf.blit(topleft, [0,0])
    surf.blit(topright, [num_x*nw, 0])
    surf.blit(bottomleft, [0, num_y*nh])
    surf.blit(bottomright, [num_x*nw, num_y*nh])

    for x in range(1, num_x):
        surf.blit(midtop, [x*nw, 0])
        surf.blit(midbottom, [x*nw, num_y*nh])

    for y in range(1, num_y):
        surf.blit(midleft, [0, y*nh])
        surf.blit(midright, [num_x*nw, y*nh])
    
    for y in range(1, num_y):
        for x in range(1, num_x):
            surf.blit(center, [x*nw, y*nh])

    return surf

def resize_enlarge(surface, size, min_dimensions=True):
    """like resize_tile except scales center tile to fit
       surface must be a pygame.Surface
       size must be a tuple or list of len 2, where it is (x size, y size)
       min_dimensions must be a bool
       when set to True, will not make any dimensions smaller
         than the current dimensions, when false it can be resized to anything"""
    surf=surface.copy()
    colorkey=surf.get_colorkey()#we need to store this and remove it for now,
                                #that way it will actually blit the colorkey values
                                #else it will change them all to black :(
    surf.set_colorkey(None)

    image=surf.copy()
    rect=image.get_rect()

    size=get_size(surface, size, min_dimensions)

    nw=int(rect.width/3)
    nh=int(rect.height/3)
    image=pygame.transform.scale(image, (nw*3, nh*3))

    topleft=image.subsurface([0,0], [nw, nh]).copy()
    midtop=image.subsurface([nw,0],[nw, nh]).copy()
    topright=image.subsurface([nw*2,0],[nw,nh]).copy()

    midleft=image.subsurface([0,nh], [nw, nh]).copy()
    center=image.subsurface([nw,nh], [nw,nh]).copy()
    midright=image.subsurface([nw*2,nh], [nw,nh]).copy()

    bottomleft=image.subsurface([0,nh*2], [nw, nh]).copy()
    midbottom=image.subsurface([nw,nh*2],[nw, nh]).copy()
    bottomright=image.subsurface([nw*2,nh*2],[nw,nh]).copy()

    width=(int(size[0]/nw)+1)*nw
    height=(int(size[1]/nh)+1)*nh

    num_x=(width/nw)-1
    num_y=(height/nh)-1

    surf=pygame.transform.scale(surf, (width, height))
    r=nsurf.get_rect()
    surf.fill((0,0,0,0))

    surf.blit(topleft, [0,0])
    surf.blit(topright, [num_x*nw, 0])
    surf.blit(bottomleft, [0, num_y*nh])
    surf.blit(bottomright, [num_x*nw, num_y*nh])

    for x in range(1, num_x):
        surf.blit(midtop, [x*nw, 0])
        surf.blit(midbottom, [x*nw, num_y*nh])

    for y in range(1, num_y):
        surf.blit(midleft, [0, y*nh])
        surf.blit(midright, [num_x*nw, y*nh])
    
    center=pygame.transform.scale(center, [nw*(num_x-1), nh*(num_y-1)])
    surf.blit(center, [nw, nh])

    return surf

def resize_multiply(surface, size, min_dimensions=True):
    """resizes an image to size or larger by placing the iimage multiple times
       together to fit the size or larger
       surface must be a pygame.Surface
       size must be a tuple or list of len 2, where it is (x size, y size)
       min_dimensions must be a bool
       when set to True, will not make any dimensions smaller
         than the current dimensions, when false it can be resized to anything"""
    surf=surface.copy()
    image=surf.copy()

    size=get_size(surface, size, min_dimensions)

    ns=[0,0]
    while ns[0] < size[0]:
        ns[0]+=image.get_width()
    while ns[1] < size[1]:
        ns[1]+=image.get_height()

    surf=pygame.transform.scale(image, ns)
    surf.fill([0,0,0,0])

    for y in range(ns[1]/image.get_height()):
        for x in range(ns[0]/image.get_width()):
            surf.blit(image, [x*image.get_width(),
                              y*image.get_height()])
    return surf

def combine_images(self, images, sep=0):
    flags = images[-1].get_flags()
    width = 0
    height = 0
    for i in images:
        width += i.get_width() + sep
        if i.get_height() > height:
            height = i.get_height()

    new = pygame.Surface((width, height), flags).convert_alpha()
    new.fill((0,0,0,0))
    lx = 0
    for i in images:
        new.blit(i, (lx, 0))
        lx += i.get_width() + sep
    return new



global_surface_clip_histories={}

def push_clip(surface, clip):
    """will apply a new clip to a surface that fits inside an old one"""
    cur=surface.get_clip()

    new=clip.clip(cur)
    if surface in global_surface_clip_histories:
        global_surface_clip_histories[surface].append(cur)
    else:
        global_surface_clip_histories[surface]=[cur]
    surface.set_clip(new)

def pop_clip(surface):
    """will revert a clip change, if there is one..."""
    if surface in global_surface_clip_histories:
        surface.set_clip(global_surface_clip_histories[surface][-1])
        global_surface_clip_histories[surface].pop(-1)
        if global_surface_clip_histories[surface]==[]:
            del global_surface_clip_histories[surface]
    else:
        pass

class ImageSheet(object):
    """An object that contains a single-nested list of images from a sprite-sheet"""
    def __init__(self, frames):
        """frames must be a value returned from split_image_by_cells,
               split_image_by_space, or a list of lists that contains images"""

        self.frames=frames

    def execute(self, func, *args, **kwargs):
        """will execture func(frame, *args, **kwargs) on all frames in the image sheet"""
        for y in xrange(len(self.frames)):
            for x in xrange(len(self.frames[y])):
                self.frames[y][x] = func(self.frames[y][x], *args, **kwargs)

def find_cell_size_by_color(surface, cell_color=(0,0,0)):
    """finds the cell size of surface based on rows and colomns of 'cell_color'
       basically:
           00100100100
           00100100100
           11111111111
           00100100100
           00100100100
       would yield a cell_size of 3, but each cell in that should be 2...
       surface must be a pygame.Surface
       cell_color must be an RGB color, not RGBA!"""
       
    width=0
    height=0

    cell_color=tuple(cell_color)

    #get width
    for x in range(surface.get_width()):
        ok=True
        for y in range(surface.get_height()):
            if not surface.get_at((x,y))[0:3] == cell_color[0:3]:
                ok=False
            else:
                continue
        if ok:
            width=x
            break

    #get height
    for y in range(surface.get_height()):
        ok=True
        for x in range(width):
            if not surface.get_at((x,y))[0:3] == cell_color:
                ok=False
            else:
                continue
        if ok:
            height=y
            break

    if width==0:width = surface.get_width()
    if height==0:height = surface.get_height()
    return width, height

def split_image_by_cells(surface, cell_size=(10,10)):
    """returns an ImageSheet based on surface using cell_size
       surface must be a pygame.Surface
       cell_size must be a tuple or list of len 2, the size of each area"""
    new_images=[]
    for y in xrange((surface.get_height())/cell_size[1]):
        new_images.append([])
        for x in xrange((surface.get_width())/cell_size[0]):
            new_image=pygame.transform.scale(surface, cell_size)
            if surface.get_colorkey():
                new_image.fill(surface.get_colorkey())
            else:
                new_image.fill(surface.get_at((0,0)))
            r=pygame.Rect(x+x*cell_size[0], y+y*cell_size[1],
                          cell_size[0], cell_size[1])
            new_image.blit(surface.subsurface(r), [0,0])
            new_images[y].append(new_image)
    return ImageSheet(new_images)

def split_image_by_space(surface, st_color=None):
    """returns an ImageSheet based on surface
       function assumes any pixel or group of pixels that is surrounded by st_color
       to be an image, otherwise the same as split_image_by_cells
       surface must be a pygame.Surface
       st_color must be None - for the topleft color of surface, or an RGB/RGBA tuple"""

    new_images=[]

    if not st_color:st_color=surface.get_at((0,0))
    st_color=tuple(st_color)

    #first we'll break the image along its height
    cur=0
    spans=[]
    have_image=False
    for y in xrange(surface.get_height()):
        empty=True
        for x in xrange(surface.get_width()):
            if not surface.get_at((x, y))[0:3]==st_color[0:3]:
                empty=False
                break
        if empty:
            if have_image:
                spans.append([cur, y-1])
                cur=y
                have_image=False
            else:
                pass
        else:
            have_image=True
    spans.append([cur, surface.get_height()-1])

    y_images=[]
    for y in spans:
        new_image=pygame.transform.scale(surface, [surface.get_width(), y[1]-y[0]])
        if surface.get_colorkey():
            new_image.fill(surface.get_colorkey())
        else:
            new_image.fill(surface.get_at((0,0)))
        r=pygame.Rect(0, y[0],
                      surface.get_width(), y[1]-y[0])
        new_image.blit(surface.subsurface(r), [0,0])
        y_images.append(new_image)

    for col in y_images:#lets do the same thing to the x colomn...
        cur=0
        spans=[]
        have_image=False
        for x in xrange(col.get_width()):
            empty=True
            for y in xrange(col.get_height()):
                if not col.get_at((x, y))[0:3]==st_color[0:3]:
                    empty=False
                    break
            if empty:
                if have_image:
                    spans.append([cur, x])
                    cur=x+1
                    have_image=False
                else:
                    pass
            else:
                have_image=True
        spans.append([cur, col.get_width()])
        cur=[]
        for x in spans:
            new_image=pygame.transform.scale(col, [x[1]-x[0], col.get_height()])
            if col.get_colorkey():
                new_image.fill(col.get_colorkey())
            else:
                new_image.fill(col.get_at((0,0)))
            r=pygame.Rect(x[0], 0,
                          x[1]-x[0], col.get_height())
            new_image.blit(col.subsurface(r), [0,0])
            cur.append(new_image)
        new_images.append(cur)

    return ImageSheet(new_images)

import time
class SimpleAnimatedImage(object):
    """An simple animated image object, simply keeps track of and renders the correct frame"""
    def __init__(self, frames=ImageSheet([[None]]), frame_delay=0.25,
                 cycle_rows=False, start_frame=[0,0]):
        """frames must be an ImageSheet
            
           frame_delay is the number of seconds each frame should show before going to the next frame
           
           cycle_rows determines whether the frames should go left to right, top to bottom,
            OR just left to right and then start over again - this is useful if you have different animations,
            say one for fighting and one for moving, and you dont want the image to automatically set
            the frames to use both animations every cycle, if you use this method you can change the y by simply
            doing AnimatedImage.y=0, etc.

           start_frame is the [x, y] frame that the animation playback will begin on"""

        self.frames=frames

        self.frame_delay=frame_delay
        self.last_time=time.time()

        self.cycle_rows=False

        self.x, self.y = start_frame

        self.cur_frame=self.frames.frames[self.y][self.x]

    def update_frame(self):
        """will change the frame to be the correct one based on the elapsed time"""
        if time.time()-self.last_time>self.frame_delay:
            self.last_time=time.time()
            self.x+=1
            if self.cycle_rows:
                if self.x>=len(self.frames.frames[self.y]):
                    self.x=0
                    self.y+=1
                    if self.y>=len(self.frames.frames):
                        self.y=0
            else:
                if self.x>=len(self.frames.frames[self.y]):
                    self.x=0
            self.cur_frame=self.frames.frames[self.y][self.x]

    def render(self, surface, pos=(0,0)):
        self.update_frame()
        surface.blit(self.cur_frame, pos)
        return None


class FancyAnimatedImage(SimpleAnimatedImage):
    """A more complex animated image that will allow you to have your frames be more personalized"""
    def __init__(self, frames=ImageSheet([[None]]), frame_delay=0.25,

                 start_frame=["Default","Default"],
                 animation_cols={"Default":[0,1]},
                 animation_rows={"Default":[0,1]}):
        """frames must be an ImageSheet
            
           frame_delay is the number of seconds each frame should show before going to the next frame

           start_frame is a list of [name1, name2] that determine which
               frame to start playback on

           animation_cols must be a dict with each value being a list,
               used to name different animations, and order them uniquely,
               animation_cols determines which "colomn" the animation is on, ie the numbers other than 0:
                   100
                   200
                   300
           animation_rows must be a dict with each value being a list,
               used to name and order different "sub-frames" of animation,
               animation_rows determines which "row" the animation uses, ie the 0'2:
                   100
                   200
                   300"""
        SimpleAnimatedImage.__init__(self, frames, frame_delay, cycle_rows=False)

        self.animation_cols=animation_cols
        self.animation_rows=animation_rows

        self.ac, self.ar = start_frame
        self.xc, self.xr = 0, 0

        self.cur_frame=self.__get_frame()

    def __get_frame(self):
        """returns the current frame based on self.xc and self.xr + self.ac and self.ar"""
        return self.frames.frames[self.animation_cols[self.ac][self.xc]]\
               [self.animation_rows[self.ar][self.xr]]

    def update_frame(self):
        """will change the frame to be the correct one based on the elapsed time,
           unlike with a SimpleAnimatedImage, cycle_rows is ignored, instead the
           animation will only follow the rules oyu place..."""
        if time.time()-self.last_time>self.frame_delay:
            self.last_time=time.time()
            self.xc += 1
            self.xr += 1

            if self.xc >= len(self.animation_cols[self.ac]):
                self.xc=0
            if self.xr >= len(self.animation_rows[self.ar]):
                self.xr=0

            self.cur_frame=self.__get_frame()

def load_simple_animated_image(name, colorkey=None, alpha=None,
                               frame_delay=0.25, cycle_rows=False,
                               method=split_image_by_space,
                               start_frame=[0,0]):
    """uses load_surface(name, colorkey, alpha) to load the image
       then uses method(loaded_surface, method_arg) to split that image into frames
       returns an AnimatedImage(loaded_surface, frame_delay, cycle_rows, start_frame)

       colorkey can be None if you want to disable it,
        -1 for the color at the topleft corner of the image,
        a tuple/list of 2 ints for a color at a specific pixel of the image,
        a tuple/list of 3 or 4 ints for a specific color,
        or a tuple/list of the previous, to apply multiple colorkeys.
        
       alpha can be None/False/0 to disable(faster rendering),
        True to enable and use per-pixel alpha,
        or an int for a full-surface alpha

        frames must be a list returned from split_image_by_space or split_image_by_cells,
         OR, frames must be a list such that [y][x] yields a surface.
         
        frame_delay is the number of seconds each frame should show before going to the next frame

        cycle_rows determines whether the frames should go left to right, top to bottom,
         OR just left to right and then start over again

        start_frame is the [x, y] frame that the animation playback will begin on"""
    a=load_surface(name, colorkey, alpha)
    a=method(a)
    return SimpleAnimatedImage(a, frame_delay, cycle_rows, start_frame)

def load_fancy_animated_image(name, colorkey=None, alpha=None,
                              frame_delay=0.25,
                              method=split_image_by_space,
                              start_frame=["Default","Default"],
                              animation_cols={"Default":[0,1]},
                              animation_rows={"Default":[0,1]}):
    """uses load_surface(name, colorkey, alpha) to load the image
       then uses method(loaded_surface, method_arg) to split that image into frames
       returns an AnimatedImage(loaded_surface, frame_delay, cycle_rows, start_frame)

       colorkey can be None if you want to disable it,
        -1 for the color at the topleft corner of the image,
        a tuple/list of 2 ints for a color at a specific pixel of the image,
        a tuple/list of 3 or 4 ints for a specific color,
        or a tuple/list of the previous, to apply multiple colorkeys.
        
       alpha can be None/False/0 to disable(faster rendering),
        True to enable and use per-pixel alpha,
        or an int for a full-surface alpha

       frame_delay is the number of seconds each frame should show before going to the next frame

       start_frame is a list of [name1, name2] that determine which
           frame to start playback on

       animation_cols must be a dict with each value being a list,
           used to name different animations, and order them uniquely,
           animation_cols determines which "colomn" the animation is on, ie the numbers other than 0:
               100
               200
               300
       animation_rows must be a dict with each value being a list,
           used to name and order different "sub-frames" of animation,
           animation_rows determines which "row" the animation uses, ie the 0'2:
               100
               200
               300"""

    a=load_surface(name, colorkey, alpha)
    a=method(a)
    return FancyAnimatedImage(a, frame_delay, start_frame, animation_cols, animation_rows)
