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
    l2 = gui.Label(root, "L1", "222!!!",
                      widget_pos="midtop")
    l2.font_color = [0, 255, 0]
    l2.make_image()

    button1 = gui.Button(root, "B1", "Button!",
                         pos=(-1, l2.rect.bottom),
                         widget_pos="midtop")

    while 1:
        for event in root.get_events():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == gui.GUI_EVENT:
                print event.name
        root.update()
        pygame.display.flip()
main()
