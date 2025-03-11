from collections.abc import Iterator

from enum import Enum
from dataclasses import dataclass


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

    def to_tuple(self) -> tuple[float, float]:
        """ Get tuple representation. """
        return (self.width, self.height)
    

class SizeBehavior(Enum):
    """
    Size behavior.

    Fields
    ------
    FIXED
        The widget will always stay at its preferred size.
    GROW
        The widget can grow beyond its preferred size if necessary.
    SHRINK
        The widget can shrink below its preferred size if necessary.
    FLEXIBLE
        The widget can either grow or shrink below its preferred size if necessary.
    """

    FIXED = 0
    GROW = 1
    SHRINK = 2
    FLEXIBLE = 3


class LayoutAlignment(Enum):
    """
    Layout alignment directions.

    Fields
    ------
    TOP
        The widget is aligned starting from top in a vertical layout.
    BOTTOM
        The widget is aligned starting from bottom in a vertical layout.
    LEFT
        The widget is aligned starting from left in a horizontal layout.
    RIGHT
        The widget is aligned starting from right in a horizontal layout.
    X_CENTER
        The widget is centered horizontally
    Y_CENTER
        The widget is centered vertically.
    CENTER
        The widget is centered.
    """

    TOP = 0
    BOTTOM = 1
    LEFT = 1
    RIGHT = 2
    X_CENTER = 3
    Y_CENTER = 4
    CENTER = 5