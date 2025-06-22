from typing import Optional

import pygame

from lucyui.core.types import SizeLike
from lucyui.core import Size, SizeBehavior
from lucyui.widgets import Widget


class Layout:
    """
    Base layout class.

    Layouts are just containers that arranges widgets by managing their
    geometries to ensure they make good use of the space available.
    """

    def __init__(self,
            size: Optional[SizeLike] = None,
            position: Optional[pygame.Vector2 | tuple[float, float] | list[float, float]] = (0, 0)
            ) -> None:
        """
        Parameters
        ----------
        size
            Layout dimensions.
            Only needed if this layout is not handled by another layout.
        position
            Layout position.
            Only needed if this layout is not handled by another layout.
        """

        self.parent_layout: "Layout" = None

        self.size = Size(*size)
        self.relative_position = pygame.Vector2(position)

        self.children = []

        self.__need_realign = False

    @property
    def position(self) -> pygame.Vector2:
        """ Layout's absolute position. """
        if self.parent_layout is None:
            return self.relative_position
        else:
            return self.parent_layout.get_absolute_position(self.relative_position)

    def update(self, events: list[pygame.Event]):
        """
        Process the layout logic.

        If this is the root layout this method should be called manually.

        Parameters
        ----------
        events
            Event list returned by the `pygame.event.get()`
        """

        if self.__need_realign:
            self._realign()
            self.__need_realign = False

        for child in self.children:
            child.update(events)

    def render(self, surface: pygame.Surface) -> None:
        """
        Render the layout onto given surface.

        If this is the root layout this method should be called manually.

        Parameters
        ----------
        surface
            Surface to render the widget onto.
        """

        for child in self.children:
            child.render(surface)

    def realign(self) -> None:
        """ Request a realign. """
        self.__need_realign = True

    def _realign(self) -> None:
        """
        Realign wigets.
        
        This method can be implemented in a subclass to
        create a custom layout distribution.
        """

    def get_absolute_position(self, position: pygame.Vector2) -> pygame.Vector2:
        """ Get absolute position in screen space. """

        return self.position + position
    
    def add_widget(self, widget: Widget) -> None:
        """ Add a widget to the layout. """
        self.children.append(widget)
        widget.parent_layout = self
        self.realign()

    def remove_widget(self, widget: Widget) -> None:
        """ Remove a widget from the layout. """
        self.children.remove(widget)
        widget.parent_layout = None
        self.realign()

    def add_stretcher(self) -> Widget:
        """ Add a stretcher widget to the layout. """

        stretcher = Widget((0, 0))
        stretcher.size_behavior = (SizeBehavior.GROW, SizeBehavior.GROW)
        stretcher.maximum_size = Size(0, 0)
        self.add_widget(stretcher)

        return stretcher