"""

    lucy-ui  -  Pygame UI & Layout Library

    This file is a part of the lucy-ui
    project and distributed under MIT license.
    https://github.com/kadir014/lucy-ui

"""

from enum import Enum
from math import pi, sin, cos


class Easing(Enum):
    """
    Various easing functions.

    Functions are taken from https://easings.net/
    """

    LINEAR = lambda x: x

    EASE_IN_SINE = lambda x: 1.0 - cos((x * pi) * 0.5)
    EASE_OUT_SINE = lambda x: sin((x * pi) * 0.5)
    EASE_IN_OUT_SINE = lambda x: -(cos(x * pi) - 1.0) * 0.5

    EASE_IN_CUBIC = lambda x: x * x * x
    EASE_OUT_CUBIC = lambda x: 1.0 - pow(1.0 - x, 3.0)
    EASE_IN_OUT_CUBIC = lambda x: 4.0 * x * x * x if x < 0.5 else 1.0 - pow(-2.0 * x + 2.0, 3.0) * 0.5