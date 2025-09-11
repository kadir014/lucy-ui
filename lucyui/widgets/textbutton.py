"""

    lucy-ui  -  Pygame UI & Layout Library

    This file is a part of the lucy-ui
    project and distributed under MIT license.
    https://github.com/kadir014/lucy-ui

"""

from typing import Optional

import pygame

from lucyui.core.types import SizeLike
from lucyui.widgets.abstractbutton import AbstractButton
from lucyui.rendering import TextRenderer


class TextButton(AbstractButton):
    """
    Basic push button widget with text.

    Attributes
    ----------
    renderer
        Text renderer this widget uses.

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
            font: pygame.Font,
            preferred_size: Optional[SizeLike] = (130, 40),
            text: str = "",
            antialiasing: bool = True
            ) -> None:
        """
        Parameters
        ----------
        font
            Font object to be used to render text.
        preferred_size
            Preferred dimensions of the widget.
        text
            Text content of the button.
        antialiasing
            Whether to use anti-aliasing while rendering text.
        """
        self.__text = text

        self.__cached_text_surf = None

        self.renderer = TextRenderer(font, antialiasing)

        super().__init__(preferred_size=preferred_size)

        self.repaint_on_mouse_interaction = True

    @property
    def text(self) -> str:
        """
        Text content of the button.
        """
        return self.__text
    
    @text.setter
    def text(self, value: str) -> None:
        # New text is different, request rerender
        if self.__text != value:
            self.__cached_text_surf = None

        self.__text = value
        self.repaint()

    def paint_event(self) -> None:
        self.surface.fill((0, 0, 0, 0))

        border_color = (132, 134, 140)
        if self._hovered:
            border_color = (159, 176, 227)
        if any(self._pressed):
            border_color = (97, 129, 255)

        pygame.draw.rect(
            self.surface,
            border_color,
            (0, 0, self.current_size.width, self.current_size.height),
            2
        )

        if self.__cached_text_surf is None:
            self.__cached_text_surf = self.renderer.render(self.text, self.current_size)

        text_surf = self.__cached_text_surf
        surf_rect = self.surface.get_rect()
        text_rect = text_surf.get_rect(center=surf_rect.center)

        self.surface.blit(text_surf, text_rect)