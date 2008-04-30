import pygame
from pygame.locals import *

import tile_engine, image, grid

def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    screen.fill((255,255,255))

    img = image.change_color(pygame.image.load("test_tile_img.bmp").convert_alpha(),
                             (255, 255, 255), (0,0,0,0))

    tiles = {"g":tile_engine.TileSet(img, [40, 20])}
##    mapd = [[["g", 0], ["g", 0]],
##            [["g", 0], ["g", 0]]]
    mapd = []
    for x in xrange(50):
        mapd.append([])
        for y in xrange(50):
            mapd[x].append(["g", 0])
    world = tile_engine.World(mapd, tiles, [40, 20, 20],
                              grid.Isometric)
    world.render(screen)

    pygame.display.flip()
main()
##import profile
##profile.run('main()')


