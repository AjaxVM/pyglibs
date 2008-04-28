import pygame
import gui
reload(gui)

def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    screen.fill((255,0,0))

    root = gui.App(screen.subsurface(0,0,640,480))
    label = gui.Label(root, "L1", "Label Test!!!",
                      widget_pos="center")
    root.update()
    l2 = gui.Label(root, "L1", "222!!!",
                      widget_pos="midtop")
    l2.font_color = [0, 255, 0]
    l2.make_image()

    root.update()
    pygame.display.flip()
main()
