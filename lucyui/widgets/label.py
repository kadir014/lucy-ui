"""

    lucy-ui  -  Pygame UI & Layout Library

    This file is a part of the lucy-ui
    project and distributed under MIT license.
    https://github.com/kadir014/lucy-ui

"""

from typing import Optional

import pygame

from lucyui.core import Size, SizeBehavior
from lucyui.core.types import SizeLike
from lucyui.widgets import Widget
from lucyui.rendering import TextRenderer


class Label(Widget):
    """
    Text label class.
    """

    def __init__(self,
            font,
            text: str = "",
            preferred_size: Optional[SizeLike] = (100, 40),
            ) -> None:
        """
        Parameters
        ----------
        preferred_size
            Preferred dimensions of the widget.
        """

        self.__text = text
        self.__text_surf = pygame.Surface((0, 0))
        self.__initial_preferred_size = Size(*preferred_size)

        self.renderer = TextRenderer(font)

        super().__init__(preferred_size=preferred_size)

        self.__render_text_surf()

    @property
    def text(self) -> str:
        """
        Text content of the label.
        
        Changing this property might alter the widget dimensions.
        """
        return self.__text
    
    @text.setter
    def text(self, value: str) -> None:
        self.__text = value

        # Why all this fuss below?
        # The text rendering has to be done separately from the paint_event
        # because the current_size changes DURING the layout realignment,
        # which we can't update the label surface with our new preferred_size
        # after the text is rendered and it stretches the widget dimensions.

        self.__render_text_surf()

        if self.parent_layout:
            self.parent_layout.realign()

        self.update_surface(repaint=False)
        self.paint_event(rerender_text=False)

    def __render_text_surf(self) -> None:
        """ Render the text and stretch the preferred dimensions if needed. """

        # TODO: Refine logic...

        # Shrink -> CAN change preferred width if the new added text is bigger
        # Grow -> Doesn't change preferred width

        if self.horizontal_behavior == SizeBehavior.FIXED:
            max_width = self.preferred_size.width
        elif self.horizontal_behavior == SizeBehavior.SHRINK:
            max_width = self.current_size.width
        else:
            max_width = self.current_size.width

        if self.vertical_behavior in (SizeBehavior.FIXED, SizeBehavior.SHRINK):
            max_height = self.preferred_size.height
        else:
            max_height = self.maximum_size.height

        self.__text_surf = self.renderer.render(self.__text, Size(max_width, max_height))

        size = Size(*self.__text_surf.size)
        if self.horizontal_behavior not in (SizeBehavior.FIXED, SizeBehavior.GROW) and size.width > max_width:
            self.preferred_size.width = size.width
        if self.vertical_behavior != SizeBehavior.FIXED and size.height > max_height:
            self.preferred_size.height = size.height
        #self.preferred_size.height = size.height
        
    def paint_event(self, rerender_text: bool = True) -> None:
        if rerender_text:
            self.__render_text_surf()
            #print("lol")

        #self.surface.fill((100, 255, 100))

        y = self.current_size.height * 0.5 - self.__text_surf.height * 0.5

        self.surface.blit(self.__text_surf, (0, y))