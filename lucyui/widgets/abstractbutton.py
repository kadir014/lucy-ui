"""

    lucy-ui  -  Pygame UI & Layout Library

    This file is a part of the lucy-ui
    project and distributed under MIT license.
    https://github.com/kadir014/lucy-ui

"""

from typing import Optional

import pygame

from lucyui.core import Hook
from lucyui.core.types import SizeLike
from lucyui.widgets import Widget


class AbstractButton(Widget):
    """
    Abstract push button widget.

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
            preferred_size: Optional[SizeLike] = (100, 40),
            ) -> None:
        """
        Parameters
        ----------
        preferred_size
            Preferred dimensions of the widget.
        """
        self.clicked = Hook()
        self.pressed = Hook()
        self.released = Hook()

        super().__init__(preferred_size=preferred_size)

    def mouse_press_event(self, position: pygame.Vector2) -> None:
        self.pressed.emit()

    def mouse_release_event(self, position: pygame.Vector2) -> None:
        self.released.emit()
        self.clicked.emit()