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


class TextButton(AbstractButton):
    """
    Basic push button widget with text.

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
        self.font = font
        self.__text = text
        self.antialiasing = antialiasing

        super().__init__(preferred_size=preferred_size)

    @property
    def text(self) -> str:
        """
        Text content of the button.
        """
        return self.__text
    
    @text.setter
    def text(self, value: str) -> None:
        self.__text = value
        self.paint_event()

    def paint_event(self) -> None:
        self.surface.fill((0, 0, 0, 0))

        pygame.draw.rect(self.surface, (0, 0, 0), (0, 0, self.current_size.width, self.current_size.height), 1)
        textsurf = self.font.render(self.text, self.antialiasing, (0, 0, 0))
        surfrect = self.surface.get_rect()
        textrect = textsurf.get_rect()
        self.surface.blit(
            textsurf, (
                surfrect.centerx - textrect.centerx,
                surfrect.centery - textrect.centery
            )
        )