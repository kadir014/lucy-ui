"""

    lucy-ui  -  Pygame UI & Layout Library

    This file is a part of the lucy-ui
    project and distributed under MIT license.
    https://github.com/kadir014/lucy-ui

"""

from typing import Optional

import pygame

from lucyui.core import (
    SizeBehavior,
    LayoutAlignment,
    LayoutDistribution,
    StackDirection
)
from lucyui.core.types import SizeLike, Coordinate
from lucyui.layouts import Layout
from lucyui.layouts.solver import solve_size_constraints
from lucyui.widgets import Widget


class Stack(Layout):
    """
    Stack layout.

    This layout arranges widgets stacked on an axis.
    """

    def __init__(self,
            direction: StackDirection,
            preferred_size: Optional[SizeLike] = None,
            relative_position: Coordinate = (0, 0),
            main_alignment: LayoutAlignment = LayoutAlignment.CENTER,
            cross_alignment: LayoutAlignment = LayoutAlignment.CENTER,
            distribution: LayoutDistribution = LayoutDistribution.SPACE_AROUND,
            ) -> None:
        """
        Parameters
        ----------
        direction
            Direction of the main axis.
        preferred_size
            Preferred layout dimensions.
            Only needed if this layout is not handled by another layout.
        position
            Layout position relative to world.
            Only needed if this layout is not handled by another layout.
        main_alignment
            Alignment on the main axis of the layout.
        cross_alignment
            Alignment on the cross axis of the layout.
        distribution
            Widget distribution strategy on the main axis.
        """
        self.__direction = direction
        self.__main_alignment = main_alignment
        self.__cross_alignment = cross_alignment
        self.__distribution = distribution

        super().__init__(
            preferred_size=preferred_size,
            relative_position=relative_position
        )

    @property
    def direction(self) -> StackDirection:
        """ Direction of the main layout axis. """
        return self.__direction
    
    @direction.setter
    def direction(self, value: StackDirection) -> None:
        self.__direction = value
        self.realign()

    @property
    def main_alignment(self) -> LayoutAlignment:
        """ Alignment on the main axis of the layout. """
        return self.__main_alignment
    
    @main_alignment.setter
    def main_alignment(self, value: LayoutAlignment) -> None:
        self.__main_alignment = value
        self.realign()

    @property
    def cross_alignment(self) -> LayoutAlignment:
        """ Alignment on the cross axis of the layout. """
        return self.__cross_alignment
    
    @cross_alignment.setter
    def cross_alignment(self, value: LayoutAlignment) -> None:
        self.__cross_alignment = value
        self.realign()
        
    @property
    def distribution(self) -> LayoutDistribution:
        """ Widget distribution strategy on the main axis. """
        return self.__distribution
    
    @distribution.setter
    def distribution(self, value: LayoutDistribution) -> None:
        self.__distribution = value
        self.realign()

    def update(self, events: list[pygame.Event]) -> None:
        visible_children = [child for child in self._children if child.is_visible]
        children_layouts = sum([1 for child in visible_children if isinstance(child, Layout)])

        if children_layouts > 0:
            main_axis = self.direction.value
            cross_axis = 1 - main_axis

            for child in visible_children:
                if isinstance(child, Stack):
                    # If the child stack has the same direction, its smallest fit is sum of its children
                    # If not, it's smallest fit is the biggest child
                    smallest_fit = [c.preferred_size[main_axis] for c in child._children]

                    if self.__direction == child.direction:
                        layout_preferred_size = sum(smallest_fit)
                    else:
                        layout_preferred_size = max(smallest_fit)

                    child.preferred_size[main_axis] = layout_preferred_size
                    child.minimum_size[main_axis] = layout_preferred_size
                    child.preferred_size[cross_axis] = self.current_size[cross_axis]

        super().update(events)

    def _realign(self) -> None:
        # Realignment route:
        # 1. Solve size constraints on the main axis
        # 2. Place widgets on the main axis
        # 3. Adjust sizes on the cross axis
        # 4. Place widgets on the cross axis

        main_axis = self.direction.value
        cross_axis = 1 - main_axis

        visible_children = [child for child in self._children if child.is_visible]

        for child in visible_children:
            child.current_size = child.preferred_size.copy()

        self.iterations = solve_size_constraints(visible_children, self.current_size[main_axis], main_axis)

        if self.__main_alignment == LayoutAlignment.END:
            y = 0
            for child in visible_children[::-1]:
                y += child.current_size[main_axis]
                child.relative_position[main_axis] = self.current_size[main_axis] - y

        elif self.__main_alignment == LayoutAlignment.START:
            y = 0
            for child in visible_children:
                child.relative_position[main_axis] = y
                y += child.current_size[main_axis]

        elif self.__main_alignment == LayoutAlignment.CENTER:
            total_space = 0
            for child in visible_children:
                total_space += child.current_size[main_axis]

            remaining = self.current_size[main_axis] - total_space

            if self.__distribution == LayoutDistribution.SPACE_BETWEEN:
                n = len(visible_children) - 1
            elif self.__distribution == LayoutDistribution.SPACE_AROUND:
                n = len(visible_children) + 1

            gap = remaining / n

            # TODO: Remove this or not?
            if remaining <= 0: gap = 0

            if self.__distribution == LayoutDistribution.SPACE_BETWEEN:
                y = 0
            elif self.__distribution == LayoutDistribution.SPACE_AROUND:
                y = gap

            for child in visible_children:
                child.relative_position[main_axis] = y
                y += child.current_size[main_axis] + gap
        
        # Constraint solving on the main axis is done.
        # Now adjust the alignment on the cross axis.
        for child in visible_children:
            if child.size_behavior[cross_axis] == SizeBehavior.GROW:
                if child.maximum_size[cross_axis] == 0:
                    child.current_size[cross_axis] = self.current_size[cross_axis]
                else:
                    child.current_size[cross_axis] = min(child.maximum_size[cross_axis], self.current_size[cross_axis])

            elif child.size_behavior[cross_axis] == SizeBehavior.SHRINK:
                if self.current_size[cross_axis] < child.current_size[cross_axis]:
                    if child.minimum_size[cross_axis] > -1:
                        child.current_size[cross_axis] = max(child.minimum_size[cross_axis], self.current_size[cross_axis])
                    else:
                        child.current_size[cross_axis] = self.current_size[cross_axis]

            # TODO: Find a way to avoid duplication and combine all size behavior checks
            if child.size_behavior[cross_axis] == SizeBehavior.FLEX:
                if self.current_size[cross_axis] < child.current_size[cross_axis]:
                    if child.minimum_size[cross_axis] > -1:
                        child.current_size[cross_axis] = max(child.minimum_size[cross_axis], self.current_size[cross_axis])
                    else:
                        child.current_size[cross_axis] = self.current_size[cross_axis]

                else:
                    if child.maximum_size[cross_axis] == 0:
                        child.current_size[cross_axis] = self.current_size[cross_axis]
                    else:
                        child.current_size[cross_axis] = min(child.maximum_size[cross_axis], self.current_size[cross_axis])

            if self.__cross_alignment == LayoutAlignment.START:
                child.relative_position[cross_axis] = 0

            elif self.__cross_alignment == LayoutAlignment.END:
                child.relative_position[cross_axis] = self.current_size[cross_axis] - child.current_size[cross_axis]

            elif self.__cross_alignment == LayoutAlignment.CENTER:
                child.relative_position[cross_axis] = self.current_size[cross_axis] / 2 - child.current_size[cross_axis] / 2

            # Sizings are done.
            # If at least one size behavior on one axis is not FIXED, it HAS TO be changed 
            if isinstance(child, Widget) and not (child.size_behavior[0] == SizeBehavior.FIXED and child.size_behavior[1] == SizeBehavior.FIXED):
                child.update_surface()