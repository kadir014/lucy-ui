import pygame

from .hook import Hook
from .layout import Layout
from .widget import Widget


class Button(Widget):
    def __init__(self,
            parent_layout: Layout,
            font: pygame.Font,
            text: str = "",
            size: tuple[int, int] = (130, 40),
            antialiasing: bool = True
            ) -> None:
        super().__init__(parent_layout, size=size)

        self.font = font
        self.text = text
        self.antialiasing = antialiasing

        self.clicked = Hook()
        self.pressed = Hook()
        self.released = Hook()

        self.paint()

    def paint(self) -> None:
        self.surface.fill((0, 0, 0, 0))

        pygame.draw.rect(self.surface, (0, 0, 0), (0, 0, self.size[0], self.size[1]), 1)
        textsurf = self.font.render(self.text, self.antialiasing, (0, 0, 0))
        surfrect = self.surface.get_rect()
        textrect = textsurf.get_rect()
        self.surface.blit(
            textsurf, (
                surfrect.centerx - textrect.centerx,
                surfrect.centery - textrect.centery
            )
        )

    def mouse_press_event(self, position: pygame.Vector2) -> None:
        self.pressed.emit()

    def mouse_release_event(self, position: pygame.Vector2) -> None:
        self.released.emit()
        self.clicked.emit()