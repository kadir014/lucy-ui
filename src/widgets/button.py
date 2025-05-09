from typing import Optional

import pygame

from src.core import Hook, Size
from src.layouts import Layout
from src.widgets import Widget


class Button(Widget):
    """
    Basic push button widget.

    Hooks
    -----
    clicked
        Emitted when the button is clicked.
    pressed
        Emitted when the button is pressed.
    released
        Emitted when the button is released.
    """
    def __init__(self,
            parent_layout: Layout,
            font: pygame.Font,
            preferred_size: Optional[Size | tuple[float, float] | list[float, float]] = (130, 40),
            text: str = "",
            antialiasing: bool = True
            ) -> None:
        """
        Parameters
        ----------
        parent_layout
            The layout that this widget belongs to.
        font
            Font object to be used to render text.
        preferred_size
            Preferred dimensions of the widget.
        text
            Text label of the button.
        antialiasing
            Whether to use anti-aliasing while rendering text.
        """
        self.font = font
        self.text = text
        self.antialiasing = antialiasing

        self.clicked = Hook()
        self.pressed = Hook()
        self.released = Hook()

        super().__init__(parent_layout, preferred_size=preferred_size)

    def paint_event(self) -> None:
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