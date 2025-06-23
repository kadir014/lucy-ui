"""

    lucy-ui  -  Pygame UI & Layout Library

    This file is a part of the lucy-ui
    project and distributed under MIT license.
    https://github.com/kadir014/lucy-ui

"""

from collections.abc import Iterator

from enum import Enum, auto
from dataclasses import dataclass

import pygame


class ConstrainedBoxModel:
    """
    This class is the smallest building block for a UI element, describing a
    transformable and constrainable box geometry.
    """

    def __init__(self,
            preferred_size: "Size",
            relative_position: pygame.Vector2,
            ) -> None:
        """
        Parameters
        ----------
        preferred_size
            Preferred size of the box model.
        relative_position
            Position of the box model relative to world or its parent.
        """
        self.preferred_size = preferred_size
        self.current_size = self.preferred_size.copy()
        
        self.relative_position = relative_position

        self.maximum_size = Size(0, 0)
        self.minimum_size = Size(0, 0)

    @property
    def rect(self) -> pygame.Rect:
        """ pygame.Rect object representing relative geometry. """
        return pygame.Rect(
            self.relative_position.x,
            self.relative_position.y,
            self.current_size.width,
            self.current_size.height
        )
    
    @property
    def frect(self) -> pygame.FRect:
        """ pygame.FRect object representing relative geometry. """
        return pygame.FRect(
            self.relative_position.x,
            self.relative_position.y,
            self.current_size.width,
            self.current_size.height
        )

@dataclass
class Size:
    """
    A dataclass representing 2D dimensions.
    """

    width: float
    height: float

    def __iter__(self) -> Iterator[float]:
        yield self.width
        yield self.height

    def __getitem__(self, index: int) -> float:
        if index == 0: return self.width
        elif index == 1: return self.height
        raise IndexError(f"Invalid index: {index}. Valid indices are 0 (width) and 1 (height).")

    def __setitem__(self, index: int, value: float) -> None:
        if index == 0: self.width = value
        elif index == 1: self.height = value
        else: raise IndexError(f"Invalid index: {index}. Valid indices are 0 (width) and 1 (height).")

    def copy(self) -> "Size":
        """ Get a copy of size. """
        return Size(*self)

    def to_tuple(self) -> tuple[float, float]:
        """ Get tuple representation. """
        return (self.width, self.height)
    
    def is_valid(self) -> bool:
        """ Is this a valid size (dimension bigger than 0.) """
        return self.width > 0 and self.height > 0
    

class SizeBehavior(Enum):
    """
    Size behavior.

    Fields
    ------
    FIXED
        The widget will always stay at its preferred size.
    GROW
        The widget can grow beyond its preferred size if necessary, but not shrink below it.
        The widget cannot grow beyond its maximum size if above 0.
    SHRINK
        The widget can shrink below its preferred size if necessary, but not grow beyond it.
        The widget cannot shrink below its minimum size if above 0.
    FLEX
        The widget can either grow or shrink outside its preferred size if necessary.
        The widget cannot go outside its maximum and minimum sizes if above 0.
    """

    FIXED = auto()
    GROW = auto()
    SHRINK = auto()
    FLEX = auto()


class LayoutAlignment(Enum):
    """
    Layout alignment directions.

    Fields
    ------
    START
        The widgets are aligned to top in vertical axis
        and to left in horizontal axis.
    END
        The widgets are aligned to bottom in vertical axis
        and to right in horizontal axis.
    CENTER
        The widgets are aligned to center.
    """

    START = auto()
    END = auto()
    CENTER = auto()


class LayoutDistribution(Enum):
    """
    Layout widget distribution strategies used when center-aligned.

    Fields
    ------
    SPACE_BETWEEN
        All widgets are placed with even spacing between.
    SPACE_ROUND
        All widgets are placed with even spacing, including edges.
    """

    SPACE_BETWEEN = auto()
    SPACE_AROUND = auto()


class StackDirection(Enum):
    """
    Stack layout main axis direction.

    Fields
    ------
    HORIZONTAL
        Main axis is horizontal (on X).
    VERTICAL
        Main axis is vertical (on Y).
    """

    HORIZONTAL = 0
    VERTICAL = 1