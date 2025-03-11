from typing import Optional

import pygame

from src.core import Size


class Layout:
    """
    Base layout class.

    Layouts are just containers that arranges widgets by managing their
    geometries to ensure they make good use of the space available.
    """

    def __init__(self,
            parent_layout: "Layout" = None,
            size: Optional[Size | tuple[float, float] | list[float, float]] = None,
            position: Optional[pygame.Vector2 | tuple[float, float] | list[float, float]] = (0, 0)
            ) -> None:
        """
        Parameters
        ----------
        parent_layout
            The layout this layout belongs to.
            Leave empty if this is the root layout.
        size
            Layout dimensions.
            Only needed if this layout is not handled by another layout.
        position
            Layout position.
            Only needed if this layout is not handled by another layout.
        """

        self.parent_layout = parent_layout
        if self.parent_layout is not None: self.parent_layout.children.append(self)

        self.size = Size(*size)
        self.relative_position = pygame.Vector2(position)

        self.children = []

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
        """ Realign widgets. """
        raise NotImplementedError

    def get_absolute_position(self, position: pygame.Vector2) -> pygame.Vector2:
        """ Get absolute position in screen space. """

        return self.position + position