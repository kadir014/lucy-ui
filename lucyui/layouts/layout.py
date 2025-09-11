"""

    lucy-ui  -  Pygame UI & Layout Library

    This file is a part of the lucy-ui
    project and distributed under MIT license.
    https://github.com/kadir014/lucy-ui

"""

from typing import Optional
from collections.abc import Iterator

import pygame

from lucyui.core.types import SizeLike, Coordinate
from lucyui.core import Size, SizeBehavior
from lucyui.core.models import ConstrainedBoxModel
from lucyui.widgets import Widget


class Layout(ConstrainedBoxModel):
    """
    Base layout class.

    Layouts are just containers that arranges widgets by managing their
    geometries to ensure they make good use of the space available.

    Attributes
    ----------
    parent_layout
        Parent layout that manages this layout.
    """

    def __init__(self,
            preferred_size: Optional[SizeLike] = None,
            relative_position: Coordinate = (0.0, 0.0)
            ) -> None:
        """
        Parameters
        ----------
        preferred_size
            Preferred layout dimensions.
            Only needed if this layout is not handled by another layout.
        relative_position
            Position relative to parent.
            Only needed if this layout is not handled by another layout.
        """

        if preferred_size is None: preferred_size = Size(10, 10)
        else: preferred_size = Size(*preferred_size)
        
        super().__init__(preferred_size, pygame.Vector2(relative_position))

        self.__horizontal_behavior = SizeBehavior.FLEX
        self.__vertical_behavior = SizeBehavior.FLEX

        self.parent_layout: "Layout" = None

        self._children: list[Widget | Layout] = []

        self.__need_realign = False
        self.iterations = 0

    @property
    def position(self) -> pygame.Vector2:
        """ Layout's absolute position. """
        if self.parent_layout is None:
            return self.relative_position
        else:
            return self.parent_layout.get_absolute_position(self.relative_position)
        
    @property
    def absolute_rect(self) -> pygame.Rect:
        """ pygame.Rect object representing layout's absolute geometry. """
        return pygame.Rect(
            self.position.x,
            self.position.y,
            self.current_size.width,
            self.current_size.height
        )
    
    @property
    def absolute_frect(self) -> pygame.FRect:
        """ pygame.FRect object representing layout's absolute geometry. """
        return pygame.FRect(
            self.position.x,
            self.position.y,
            self.current_size.width,
            self.current_size.height
        )
        
    @property
    def size_behavior(self) -> tuple[SizeBehavior, SizeBehavior]:
        """ Horizontal and vertical size behavior of the layout. """
        return (self.__horizontal_behavior, self.__vertical_behavior)
    
    @size_behavior.setter
    def size_behavior(self, value: tuple[SizeBehavior, SizeBehavior]) -> None:
        self.__horizontal_behavior = value[0]
        self.__vertical_behavior = value[1]
        
        if self.parent_layout is not None:
            self.parent_layout.realign()

    @property
    def horizontal_behavior(self) -> SizeBehavior:
        """ Horizontal size behavior of the layout. """
        return self.__horizontal_behavior
    
    @horizontal_behavior.setter
    def horizontal_behavior(self, value: SizeBehavior) -> None:
        self.__horizontal_behavior = value
        
        if self.parent_layout is not None:
            self.parent_layout.realign()

    @property
    def vertical_behavior(self) -> SizeBehavior:
        """ Vertical size behavior of the layout. """
        return self.__vertical_behavior
    
    @vertical_behavior.setter
    def vertical_behavior(self, value: SizeBehavior) -> None:
        self.__vertical_behavior = value
        
        if self.parent_layout is not None:
            self.parent_layout.realign()

    def update(self, events: list[pygame.Event]):
        """
        Process the layout logic.

        If this is the root layout this method should be called manually.

        Parameters
        ----------
        events
            Event list returned by the `pygame.event.get()`
        """

        # Realign children layouts bottom-up.
        for child in self._children:
            if isinstance(child, Layout):
                child.realign()
                child.update(events)

        # Once all the layouts are aligned recursively bottom-up, realign this one.
        if self.__need_realign:
            self._realign()
            self.__need_realign = False

        for child in self._children:
            if isinstance(child, Widget):
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

        for child in self._children:
            child.render(surface)

    def realign(self) -> None:
        """ Request a realign. """
        self.__need_realign = True

    def _realign(self) -> None:
        """
        Realign widgets.
        
        This method can be implemented in a subclass to
        create a custom layout solver.
        """

    def get_absolute_position(self, position: pygame.Vector2) -> pygame.Vector2:
        """ Get absolute position in screen space. """

        return self.position + position
    
    def add_widget(self, widget: Widget) -> None:
        """
        Add a widget to this layout.
        
        Parameters
        ----------
        widget
            Child widget to add to this layout.
        """

        self._children.append(widget)
        widget.parent_layout = self
        self.realign()

    def remove_widget(self, widget: Widget) -> None:
        """
        Remove a widget from this layout.
        
        Parameters
        ----------
        widget
            Child widget to remove from this layout.
        """

        self._children.remove(widget)
        widget.parent_layout = None
        self.realign()

    def add_layout(self, layout: "Layout") -> None:
        """
        Add a layout to this layout.

        Parameters
        ----------
        layout
            Child layout to add to this layout.
        """

        self._children.append(layout)
        layout.parent_layout = self
        self.realign()

    def remove_layout(self, layout: "Layout") -> None:
        """
        Remove a layout from this layout.
        
        Parameters
        ----------
        layout
            Child layout to remove from this layout.
        """

        self._children.remove(layout)
        layout.parent_layout = None
        self.realign()

    def add_stretcher(self) -> Widget:
        """ Add a stretcher to this layout. """

        stretcher = Widget((0, 0))
        stretcher.size_behavior = (SizeBehavior.GROW, SizeBehavior.GROW)
        stretcher.maximum_size = Size(0, 0)
        self.add_widget(stretcher)

        return stretcher
    
    def iter_children(self) -> Iterator[tuple[int, "Widget | Layout"]]:
        """ Iterate over this layout's children. """

        for i, child in self._children:
            yield (i, child)

    def iter_widgets(self) -> Iterator[tuple[int, Widget]]:
        """ Iterate over this layout's child widgets. """

        for i, child in self._children:
            if isinstance(child, Widget):
                yield (i, child)

    def iter_widgets(self) -> Iterator[tuple[int, "Layout"]]:
        """ Iterate over this layout's child layouts. """

        for i, child in self._children:
            if isinstance(child, Layout):
                yield (i, child)