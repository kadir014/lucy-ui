import pygame

from src import VerticalStack, Widget, TextInput
from src.models import Size, SizeBehavior, LayoutAlignment


WINDOW_WIDTH = 600
WINDOW_HEIGHT = 720
MAX_FPS = 165


pygame.init()
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Yet Another Pygame UI Library")
clock = pygame.Clock()
is_running = True

font = pygame.Font("assets/FiraCode-Regular.ttf", 14)
font = pygame.font.SysFont("Arial", 16)


class PaintedWidget(Widget):
    def __init__(self, parent_layout, color, preferred_size = None):
        self.color = color

        super().__init__(parent_layout, preferred_size)

    def paint_event(self):
        self.surface.fill(self.color)
        pygame.draw.rect(self.surface, (0, 0, 0), ((5, 5), (self.current_size[0]-10, self.current_size[1]-10)), 2)

w = 200

root_lyt0 = VerticalStack(None, [WINDOW_WIDTH, WINDOW_HEIGHT], (0, 0))
root_lyt0.alignment = LayoutAlignment.TOP

fixed_wgt = PaintedWidget(root_lyt0, (255, 0, 0), [w, 70])

growing_wgt = PaintedWidget(root_lyt0, (0, 255, 0), [w, 115])
growing_wgt.set_size_behavior(SizeBehavior.FIXED, SizeBehavior.GROW)
growing_wgt.maximum_size.height = 200

fixed_wgt2 = PaintedWidget(root_lyt0, (255, 0, 0), [w, 70])

#growing_wgt2 = PaintedWidget(root_lyt0, (0, 160, 255), [w, 0])
growing_wgt2 = TextInput(root_lyt0, font, placeholder="Type here!", preferred_size=(w, 30))
growing_wgt2.set_size_behavior(SizeBehavior.FIXED, SizeBehavior.GROW)
growing_wgt2.maximum_sizeheight = 150


root_lyt1 = VerticalStack(None, [WINDOW_WIDTH, WINDOW_HEIGHT], (w, 0))
root_lyt1.alignment = LayoutAlignment.TOP

fixed_wgt = PaintedWidget(root_lyt1, (255, 0, 0), [w, 70])

growing_wgt = PaintedWidget(root_lyt1, (0, 255, 0), [w, 115])
growing_wgt.set_size_behavior(SizeBehavior.FIXED, SizeBehavior.GROW)
growing_wgt.maximum_size.height = 200

fixed_wgt2 = PaintedWidget(root_lyt1, (255, 0, 0), [w, 70])

growing_wgt2 = PaintedWidget(root_lyt1, (0, 160, 255), [w, 50])
growing_wgt2.set_size_behavior(SizeBehavior.FIXED, SizeBehavior.GROW)
growing_wgt2.maximum_size.height = 90

growing_wgt2 = PaintedWidget(root_lyt1, (0, 160, 255), [w, 40])
growing_wgt2.set_size_behavior(SizeBehavior.FIXED, SizeBehavior.GROW)
growing_wgt2.maximum_size.height = 0


root_lyt2 = VerticalStack(None, [WINDOW_WIDTH, WINDOW_HEIGHT], (w*2, 0))
root_lyt2.alignment = LayoutAlignment.X_CENTER

fixed_wgt = PaintedWidget(root_lyt2, (255, 0, 0), [w, 70])

growing_wgt = PaintedWidget(root_lyt2, (0, 255, 0), [w, 115])
growing_wgt.set_size_behavior(SizeBehavior.FIXED, SizeBehavior.GROW)
growing_wgt.maximum_size.height = 200


while is_running:
    dt = clock.tick(MAX_FPS) * 0.001

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            is_running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                is_running = False

        #elif event.type == pygame.WINDOWRESIZED:
        #    root_lyt0.size = [event.x, event.y]
        #    root_lyt0.realign()

    mouse = pygame.Vector2(*pygame.mouse.get_pos())

    root_lyt0.size = Size(mouse.x, mouse.y)
    root_lyt0.realign()
    root_lyt1.size = Size(mouse.x, mouse.y)
    root_lyt1.realign()
    root_lyt2.size = Size(mouse.x, mouse.y)
    root_lyt2.realign()

    window.fill((255, 255, 255))

    #pygame.draw.rect(window, (243, 243, 243), ((root_lyt.position, root_lyt.size)))

    root_lyt0.update(events)
    root_lyt0.render(window)
    root_lyt1.update(events)
    root_lyt1.render(window)
    root_lyt2.update(events)
    root_lyt2.render(window)

    pygame.display.flip()

pygame.quit()