from typing import Optional

import pygame

from .layout import Layout
from .widget import Widget
from .enums import SizeBehavior, LayoutAlignment


class VerticalStack(Layout):
    """
    Vertical stack layout.

    This layout arranges widgets in a vertical axis.
    """

    def __init__(self,
            parent_layout: Layout = None,
            size: Optional[list[int, int]] = None,
            position: Optional[pygame.Vector2 | tuple[int, int]] = None,
            alignment: LayoutAlignment = LayoutAlignment.TOP
            ) -> None:
        super().__init__(parent_layout=parent_layout, size=size, position=position)
        self.alignment = alignment

    def realign(self) -> None:
        h_fixed = 0
        growables: list[Widget] = []
        for child in self.children:
            if isinstance(child, Widget):
                if child.vertical_behavior == SizeBehavior.FIXED:
                    h_fixed += child.current_size[1]

                elif child.vertical_behavior == SizeBehavior.GROW:
                    h_fixed += child.preferred_size[1]
                    growables.append(child)

        n_growables = len(growables)
        if n_growables == 0: return

        # h_fixed    -> Fixed amount of area allocated
        # h_growable -> Empty area that can be used to grow widgets
        # h_each     -> Expandable size allocated for each widget

        h_growable = self.size[1] - h_fixed
        h_each = h_growable / len(growables)
        if h_each < 0: h_each = 0

        # Solve growable heights with maximum height in consideration
        # Iterate at least N growable widget times so each widget can be evaluated
        # after each redistribution
        for _ in range(n_growables):
            new_growables = []
            for child in growables:
                new_h = child.preferred_size[1] + h_each
                if child.maximum_size[1] is not None and new_h > child.maximum_size[1]:
                    h_growable -= child.maximum_size[1]
                    child.current_size[1] = child.maximum_size[1]
                    child.update_surface()
                    continue

                child.current_size[1] = new_h
                new_growables.append(child)

            growables = new_growables

            # All growable widgets has reached maximum size, terminate
            if len(growables) == 0: break

            h_each = h_growable / len(growables)
            if h_each < 0: h_each = 0

            is_satisfied = True
            for child in growables:
                if child.maximum_size[1] is not None:
                    is_satisfied = False
                    break

            # All growable widgets are satisfied, terminate
            if is_satisfied: break

        # Grow growable widgets that are not satisfied yet
        for child in growables:
            new_h = child.preferred_size[1] + h_each
            if child.maximum_size[1] is not None and new_h > child.maximum_size[1]:
                raise Exception(f"Impossible, there has to be a bug in the redistribution code. {new_h}, {child.maximum_size[1]}")
            
            child.current_size[1] = new_h
            child.update_surface()

        children_space = 0
        for child in self.children:
            if isinstance(child, Widget):
                children_space += child.current_size[1]
        remaining_space = self.size[1] - children_space

        y = 0
        if self.alignment == LayoutAlignment.BOTTOM:
            for i, child in enumerate(self.children[::-1]):
                if isinstance(child, Widget):
                    y += child.current_size[1]
                    child.relative_position.y = self.size[1] - y

        elif self.alignment == LayoutAlignment.TOP:
            for i, child in enumerate(self.children):
                if isinstance(child, Widget):
                    child.relative_position.y = y
                    y += child.current_size[1]

        elif self.alignment == LayoutAlignment.X_CENTER:
            gap = remaining_space / (len(self.children) - 1)
            if remaining_space <= 0: gap = 0

            for i, child in enumerate(self.children):
                if isinstance(child, Widget):
                    child.relative_position.y = y
                    y += child.current_size[1] + gap