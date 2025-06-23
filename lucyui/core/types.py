"""

    lucy-ui  -  Pygame UI & Layout Library

    This file is a part of the lucy-ui
    project and distributed under MIT license.
    https://github.com/kadir014/lucy-ui

"""
from collections.abc import Sequence

import pygame

from lucyui.core import Size


SizeLike = Size | tuple[float, float] | Sequence[float]

Coordinate = pygame.Vector2 | tuple[float, float] | Sequence[float]