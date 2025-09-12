"""

    lucy-ui  -  Pygame UI & Layout Library

    This file is a part of the lucy-ui
    project and distributed under MIT license.
    https://github.com/kadir014/lucy-ui

"""

from time import perf_counter

import pygame

from lucyui.core.models import TweenRepeatMode
from lucyui.core.hook import Hook
from lucyui.animation.easings import Easing


class Tween:
    """
    Animation interpolation handler.

    Attributes
    ----------
    start_value
        Minimum value.
    end_value
        Maximum value.
    value
        Current value in range [start, end].
    value_normalized
        Current value normalized in range [0, 1].
    is_started
        Whether the animation has started playing or not.

    Hooks
    -----
    changed
        Emitted whenever the value is changed when the animation is playing.
    """

    def __init__(
            self,
            start_value: float = 0.0,
            end_value: float = 1.0,
            value: float = 0.0
        ) -> None:
        """
        Parameters
        ----------
        start_value
            Minimum value.
        end_value
            Maximum value.
        value
            Initial value.
        """
        self.start_value, self.end_value = start_value, end_value
        self.value = pygame.math.clamp(value, self.start_value, self.end_value)
        self.value_normalized = (self.value - self.start_value) / (self.end_value - self.start_value)

        self.is_started = False

        self._alpha = self.value_normalized
        self._last_time = 0.0
        self._duration = 0.0
        self._easing = Easing.LINEAR
        self._reverse = False
        self._repeat = TweenRepeatMode.NONE

        self.changed = Hook()

    def play(self,
            duration: float,
            reverse: bool = False,
            easing: Easing = Easing.LINEAR,
            repeat: TweenRepeatMode = TweenRepeatMode.NONE
            ) -> None:
        """
        Start playing the animation.
        
        Parameters
        ----------
        duration
            Duration of the animation in seconds.
        reverse
            Whether to play the animation reversed or not.
        easing
            Easing function to use.
        repeat
            Repeating mode.
        """
        self.is_started = True
        self._last_time = perf_counter()
        self._duration = duration
        self._easing = easing
        self._repeat = repeat
        self._reverse = reverse

    def stop(self) -> None:
        """ Stop playing the animation. """
        self.is_started = False

    def update(self) -> None:
        """ Process animation logic. """

        if not self.is_started:
            return

        now = perf_counter()
        elapsed = now - self._last_time
        self._last_time = now

        t = (elapsed / self._duration) * (-1.0 if self._reverse else 1.0)

        self._alpha += t

        if self._alpha > 1.0 or self._alpha < 0.0:
            self._alpha = pygame.math.clamp(self._alpha, 0.0, 1.0)

            if self._repeat == TweenRepeatMode.NONE:
                self.stop()

            elif self._repeat == TweenRepeatMode.LOOP:
                self.update()

            elif self._repeat == TweenRepeatMode.BOUNCE:
                self._reverse = not self._reverse
                self.update()

            return

        self.value_normalized = self._easing(self._alpha)
        self.value = self.start_value + self.value_normalized * (self.end_value - self.start_value)

        self.changed.emit()