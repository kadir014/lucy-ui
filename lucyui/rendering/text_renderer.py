"""

    lucy-ui  -  Pygame UI & Layout Library

    This file is a part of the lucy-ui
    project and distributed under MIT license.
    https://github.com/kadir014/lucy-ui

"""

from dataclasses import dataclass

import pygame

from lucyui.core.types import SizeLike
from lucyui.core import Size, TextWrapMode


@dataclass
class TextRenderer:
    """
    Text renderer class.

    Attributes
    ----------
    font
        Font object to use to render the text.
    line_gap
        Line gap in pixels to use between multiline text.
    wrap_mode
        Text wrapping mode.
    antialiasing
        Whether to use antialiased rendering of font.
    """

    font: pygame.Font
    line_gap: int = 4
    wrap_mode: TextWrapMode = TextWrapMode.NONE
    antialiasing: bool = True

    def render(self, text: str, size: SizeLike) -> pygame.Surface:
        """
        Render text.

        Wrap modes wrap the text on horizontal dimension given, however, the
        final size can exceed the given size depending on few factors.

        Parameters
        ----------
        text
            String to be rendered.
        size
            Dimensions of the render area.
        """

        size = Size(*size)

        if self.wrap_mode == TextWrapMode.NONE:
            return self.font.render(text, self.antialiasing, (0, 0, 0))
        
        elif self.wrap_mode == TextWrapMode.WORD:
            if size.width == 0:
                max_width = float("inf")
            else:
                max_width = size.width

            words = text.split(" ")
            word_i = 0
            lines = []
            max_line_width = -float("inf")

            while word_i < len(words):
                line = ""
                line_future = words[word_i]

                looped = False
                while self.font.size(line_future)[0] <= max_width and word_i < len(words):
                    line += words[word_i] + " "
                    word_i += 1

                    if word_i < len(words):
                        line_future = line + words[word_i]

                    looped = True

                if not looped:
                    line = words[word_i]
                    word_i += 1

                line_surf = self.font.render(line[:-1], self.antialiasing, (0, 0, 0))
                if line_surf.width > max_line_width: max_line_width = line_surf.width
                lines.append(line_surf)

            height = 0
            for line in lines:
                height += line.height + self.line_gap
            height -= self.line_gap

            surf = pygame.Surface((max_line_width, height), pygame.SRCALPHA).convert_alpha()

            for i, line_surf in enumerate(lines):
                surf.blit(line_surf, (0, i * (line_surf.height + self.line_gap)))

            return surf
        
        elif self.wrap_mode == TextWrapMode.CHARACTER:
            ...