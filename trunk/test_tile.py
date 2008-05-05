import pygame
from pygame.locals import *

import tile_engine, image, grid

import random

def get_pos_text(obj, font):
    text = str(obj.tile_pos[0]) + ", " + str(obj.tile_pos[1])
    img = font.render(text, True, [0, 255, 0])
    return img

def update_text(obj, unit, font):
    unit.image.fill((0, 0, 0, 125))
    unit.image.blit(get_pos_text(obj, font), (0, 0))

def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    screen.fill((255,255,255))

    img = image.change_color(pygame.image.load("test_tile_img.bmp").convert_alpha(),
                             (255, 255, 255), (0,0,0,0))

    tiles = {"g":tile_engine.TileSet(img, [40, 20])}

    mapd = []
    for x in xrange(50):
        mapd.append([])
        for y in xrange(50):
            mapd[x].append(["g", 0])
    world = tile_engine.World(mapd, tiles, [40, 20, 20],
                              grid.Isometric)
    img = pygame.image.load("mouse_cursor.bmp").convert_alpha()

    a = tile_engine.Unit(world, img, [5.5, 0.5])
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 25)

    base_image = pygame.Surface((100, 20)).convert_alpha()
    text_unit = tile_engine.Unit(world, base_image, [4, -1])
    update_text(a, text_unit, font)
    while 1:
        clock.tick(999)
        for event in pygame.event.get():
            if event.type == QUIT:
                print clock.get_fps()
                pygame.quit()
                raw_input()
                return
            if event.type == KEYDOWN:
                if event.key == K_LEFT:
                    a.move(-0.1, 0.1)
                    text_unit.move(-0.1, 0.1)
                    update_text(a, text_unit, font)
                if event.key == K_RIGHT:
                    a.move(0.1, -0.1)
                    text_unit.move(0.1, -0.1)
                    update_text(a, text_unit, font)
                if event.key == K_UP:
                    a.move(-0.1, -0.1)
                    text_unit.move(-0.1, -0.1)
                    update_text(a, text_unit, font)
                if event.key == K_DOWN:
                    a.move(0.1, 0.1)
                    text_unit.move(0.1, 0.1)
                    update_text(a, text_unit, font)

        world.render(screen)

        pygame.display.flip()
main()
##import profile
##profile.run('main()')


