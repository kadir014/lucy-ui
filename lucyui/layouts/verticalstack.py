from typing import Optional

import pygame

from lucyui.core import SizeBehavior, LayoutAlignment, LayoutDistribution
from lucyui.core.types import SizeLike
from lucyui.layouts import Layout
from lucyui.layouts.solver import solve_size_constraints
from lucyui.widgets import Widget


class VerticalStack(Layout):
    """
    Vertical stack layout.

    This layout arranges widgets on a vertical axis.
    """

    def __init__(self,
            size: Optional[SizeLike] = None,
            position: Optional[pygame.Vector2 | tuple[int, int]] = None,
            main_alignment: LayoutAlignment = LayoutAlignment.CENTER,
            cross_alignment: LayoutAlignment = LayoutAlignment.CENTER,
            distribution: LayoutDistribution = LayoutDistribution.SPACE_BETWEEN
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
        main_alignment
            Alignment on the main (vertical) axis of the layout.
        cross_alignment
            Alignment on the cross (horizontal) axis of the layout.
        distribution
            Widget distribution strategy on the main axis.
        """
        self.__main_alignment = main_alignment
        self.__cross_alignment = cross_alignment
        self.__distribution = distribution

        super().__init__(size=size, position=position)

    @property
    def main_alignment(self) -> LayoutAlignment:
        return self.__main_alignment
    
    @main_alignment.setter
    def main_alignment(self, value: LayoutAlignment) -> None:
        self.__main_alignment = value
        self.realign()

    @property
    def cross_alignment(self) -> LayoutAlignment:
        return self.__cross_alignment
    
    @cross_alignment.setter
    def cross_alignment(self, value: LayoutAlignment) -> None:
        self.__cross_alignment = value
        self.realign()
        
    @property
    def distribution(self) -> LayoutDistribution:
        return self.__distribution
    
    @distribution.setter
    def distribution(self, value: LayoutDistribution) -> None:
        self.__distribution = value
        self.realign()

    def _realign(self) -> None:
        widgets = []
        for child in self.children:
            if isinstance(child, Widget):
                child.current_size.height = child.preferred_size.height
                widgets.append(child)

        solve_size_constraints(widgets, self.size.height, 1)

        # Sizings are done, update all affected children surfaces
        for widget in widgets:
            if widget.vertical_behavior != SizeBehavior.FIXED:
                widget.update_surface()

        if self.__main_alignment == LayoutAlignment.END:
            y = 0
            for child in self.children[::-1]:
                if isinstance(child, Widget):
                    y += child.current_size.height
                    child.relative_position.y = self.size.height - y

        elif self.__main_alignment == LayoutAlignment.START:
            y = 0
            for child in self.children:
                if isinstance(child, Widget):
                    child.relative_position.y = y
                    y += child.current_size.height

        elif self.__main_alignment == LayoutAlignment.CENTER:
            total_space = 0
            for child in self.children:
                if isinstance(child, Widget):
                    total_space += child.current_size.height

            remaining = self.size.height - total_space

            if self.__distribution == LayoutDistribution.SPACE_BETWEEN:
                n = len(self.children) - 1
            elif self.__distribution == LayoutDistribution.SPACE_AROUND:
                n = len(self.children) + 1

            gap = remaining / n

            # TODO: Remove this or not?
            if remaining <= 0: gap = 0

            if self.__distribution == LayoutDistribution.SPACE_BETWEEN:
                y = 0
            elif self.__distribution == LayoutDistribution.SPACE_AROUND:
                y = gap

            for child in self.children:
                if isinstance(child, Widget):
                    child.relative_position.y = y
                    y += child.current_size.height + gap
        
        for child in self.children:
            if isinstance(child, Widget):
                if self.__cross_alignment == LayoutAlignment.START:
                    child.relative_position.x = 0

                elif self.__cross_alignment == LayoutAlignment.END:
                    child.relative_position.x = self.size.width - child.current_size.width

                elif self.__cross_alignment == LayoutAlignment.CENTER:
                    child.relative_position.x = self.size.width / 2 - child.current_size.width / 2