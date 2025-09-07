"""

    lucy-ui  -  Pygame UI & Layout Library

    This file is a part of the lucy-ui
    project and distributed under MIT license.
    https://github.com/kadir014/lucy-ui

"""

from lucyui.widgets import Widget
from lucyui.core import SizeBehavior


# Allowed smallest float error
EPSILON = 0.001


def solve_size_constraints(
        widgets: list[Widget],
        size: float,
        axis: int
        ) -> int:
    """ Solve size constraints on one axis. """

    total_preferred = 0
    for widget in widgets:
        total_preferred += widget.preferred_size[axis]

    diff = size - total_preferred
    eligible: list[Widget] = []

    # Widgets already satisfy the constraints
    if diff == 0:
        return 0
    
    # There is space to be filled, grow
    elif diff > 0:
        behavior = SizeBehavior.GROW
        direction = +1

        for widget in widgets:
            if widget.size_behavior[axis] == SizeBehavior.GROW or widget.size_behavior[axis] == SizeBehavior.FLEX:
                eligible.append(widget)

    # There is not enough space, shrink
    else:
        behavior = SizeBehavior.SHRINK
        direction = -1

        for widget in widgets:
            if widget.size_behavior[axis] == SizeBehavior.SHRINK or widget.size_behavior[axis] == SizeBehavior.FLEX:
                eligible.append(widget)

    remaining = abs(diff)

    iterations = 0

    # Iteratively solve sizes
    while remaining > EPSILON and len(eligible) > 0:
        iterations += 1
        
        share = remaining / len(eligible)
        new_eligible = []

        for widget in eligible:
            proposed = widget.current_size[axis] + direction * share

            # Clamp to size limits
            if behavior == SizeBehavior.GROW and widget.maximum_size[axis] > 0:
                limit = widget.maximum_size[axis]
                proposed = min(proposed, limit)

            # Minimum size always has to have a lower limit of 0
            if behavior == SizeBehavior.SHRINK:
                limit = widget.minimum_size[axis]
                proposed = max(proposed, limit)

            used = abs(proposed - widget.current_size[axis])
            remaining -= used
            widget.current_size[axis] = proposed

            # If still capable of more growth/shrink, keep in eligible
            if direction == +1 and widget.current_size[axis] < widget.maximum_size[axis]:
                new_eligible.append(widget)
            elif direction == -1 and widget.current_size[axis] > widget.minimum_size[axis]:
                new_eligible.append(widget)
        
        eligible = new_eligible

    return iterations