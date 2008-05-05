from misc import careful_mod as spc_mod

class BaseTileMethod(object):
    def __init__(self, tile_size):
        """tile_size should be the tile_size from tile_engine.Grid"""
        self.tx, self.ty, self.tz = tile_size

    def convert_map_pos(self, x, y, z):
        """returns the map coordinates converted to pixels"""
        return x, y

    def convert_tile_pos(self, x, y):
        """returns the tile coordinates(from 0.0-for least to 1.0-for most) converted to pixels"""
        return x, y

    def convert_unit_pos(self, x, y):
        return x, y

    def get_tile_left(self, x, y, z):
        return x-1, y, z

    def get_tile_right(self, x, y, z):
        return x+1, y, z

    def get_tile_top(self, x, y, z):
        return x, y-1, z

    def get_tile_bottom(self, x, y, z):
        return x, y+1, z

    def get_tile_topleft(self, x, y, z):
        return x-1, y-1, z

    def get_tile_topright(self, x, y, z):
        return x+1, y-1, z

    def get_tile_bottomleft(self, x, y, z):
        return x-1, y+1, z

    def get_tile_bottomright(self, x, y, z):
        return x+1, y+1, z

class Square(BaseTileMethod):
    def __init__(self, tile_size):
        """creates a square tile grid, useful for 'flat' maps"""
        BaseTileMethod.__init__(self, tile_size)

    def convert_map_pos(self, x, y, z):
        """takes 3 map coordinates, and converts them to pixels to be displayed on the screen.
           aligns pixels to fit flat square tiles.
           z is defaulted to 0 because often you wont use that for this kind of map."""
        s1, s2, s3 = self.tx, self.ty, self.tz
        return int(x*s1), int(y*s2-z*s3)

    def convert_tile_pos(self, x, y):
        """used to place/move a unit on a tile, both args must be >=0.0 and <= 1.0,
           where x==0.0 and y==0.0 would be the topleft corner of the tile"""
        s1, s2 = self.tx, self.ty
        return int(x*s1), int(y*s2)

    def convert_unit_pos(self, x, y):
        return int(self.tx * x), int(self.ty * y)

class Isometric(BaseTileMethod):
    def __init__(self, tile_size):
        """creates an isometric tile, diamond shaped grid"""
        BaseTileMethod.__init__(self, tile_size)

    def convert_map_pos(self, x, y, z):
        """takes 3 coordinates, and converts them to pixels to be displayed on the screen.
           aligns pixels to fit diamond shaped tiles, aligns to a diamond shaped grid."""
        s1, s2, s3 = self.tx, self.ty, self.tz
        cx = (s1*x/2) - (s1*y/2)
        cy = (s2*x/2) + (s2*y/2) - (s3 * z)
        return int(cx), int(cy)

    def convert_tile_pos(self, x, y):
        """used to place/move a unit on a tile, both args must be >=0.0 and <= 1.0,
           where x==0.0 and y==0.0 would be the topleft corner of the tile"""
        s1, s2 = self.tx, self.ty
        cx = (s1*x/2) - (s1*y/2)
        cy = (s2*x/2) + (s2*y/2)
        return int(cx), int(cy)

    def convert_unit_pos(self, x, y):
        s1, s2 = self.tx, self.ty
        cx = (s1*x/2) - (s1*y/2)
        cy = (s2*x/2) + (s2*y/2)
        return int(cx), int(cy)

class Isometric2(Isometric):
    def __init__(self, tile_size):
        """creates an isometric grid, but not diamond shaped, to help remove black corners"""
        Isometric.__init__(self, tile_size)

    def convert_map_pos(self, x, y, z):
        """takes 3 coordinates, and converts them to pixels to be displayed on the screen.
           aligns pixels to fit diamond shaped tiles, aligns to "square" grid,
           ie(the corners for the corners of the screen, easier to take out black areas around
           edges of screen - just lock a camera left/right to tile_size[0]/2
           and top/bottom to tile_size[1]/2"""
        s1, s2, s3 = self.tx, self.ty, self.tz
        odd=spc_mod(y, 2)
        cx=x*s1
        cy=y*s2/2
        if odd:cx+=s2
        return int(cx), int(cy)

    def convert_unit_pos(self, x, y):
        x, y = self.convert_map_pos(int(x), int(y))
        nx, ny = Isometric.convert_unit_pos(x - int(x), y - int(y))
        return int(x + nx), int(y + ny)

    def get_tile_left(self, x, y, z):
        odd=spc_mod(y, 2)
        if odd:
            return x, y-1, z
        return x-1, y-1, z

    def get_tile_right(self, x, y, z):
        odd=spc_mod(y, 2)
        if odd:return x+1, y+1, z
        else:return x, y+1, z

    def get_tile_top(self, x, y, z):
        odd=spc_mod(y, 2)
        if odd:return x+1, y-1, z
        else:return x, y-1, z

    def get_tile_bottom(self, x, y, z):
        odd=spc_mod(y, 2)
        if odd:return x, y+1, z
        return x-1, y+1, z

    def get_tile_topleft(self, x, y, z):
        odd=spc_mod(y, 2)
        return x, y-2, z

    def get_tile_topright(self, x, y, z):
        odd=spc_mod(y, 2)
        return x+1, y, z

    def get_tile_bottomleft(self, x, y, z):
        odd=spc_mod(y, 2)
        return x-1, y, z

    def get_tile_bottomright(self, x, y, z):
        odd=spc_mod(y, 2)
        return x, y+2, z

class Grid(object):
    def __init__(self, tile_size=(50, 50, 25),
                 tile_method=Square):
        """tile_size = width, height, depth of image, meaning: width is the set width of the image
                     |-> height is the height of the "flat" or "top" part of the image
                     |-> depth is the cliff height of the image, used for layering tiles upwards
           tile_method is a function to be used to place a unit"""

        self.tile_size=tile_size
        self.tile_method=tile_method(self.tile_size)

    def convert_map_pos(self, x, y, z):
        return self.tile_method.convert_map_pos(x, y, z)

    def convert_tile_pos(self, x, y):
        return self.tile_method.convert_tile_pos(x, y)

    def convert_unit_pos(self, x, y):
        return self.tile_method.convert_unit_pos(x, y)

    def get_tile_left(self, x, y, z):
        return self.tile_method.get_tile_left(x, y, z)

    def get_tile_right(self, x, y, z):
        return self.tile_method.get_tile_right(x, y, z)

    def get_tile_top(self, x, y, z):
        return self.tile_method.get_tile_top(x, y, z)

    def get_tile_bottom(self, x, y, z):
        return self.tile_method.get_tile_bottom(x, y, z)

    def get_tile_topleft(self, x, y, z):
        return self.tile_method.get_tile_topleft(x, y, z)

    def get_tile_topright(self, x, y, z):
        return self.tile_method.get_tile_topright(x, y, z)

    def get_tile_bottomleft(self, x, y, z):
        return self.tile_method.get_tile_bottomleft(x, y, z)

    def get_tile_bottomright(self, x, y, z):
        return self.tile_method.get_tile_bottomright(x, y, z)
