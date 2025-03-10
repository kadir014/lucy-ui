from enum import Enum


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
        The widget is centered along the X axis.
    Y_CENTER
        The widget is centered along the Y axis.
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