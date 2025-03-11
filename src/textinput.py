from typing import Optional

import time

import pygame

from .hook import Hook
from .layout import Layout
from .widget import Widget
from .models import Size


class TextInput(Widget):
    """
    Single line text editing widget.

    Hooks
    -----
    enter_pressed
        Emitted when the Enter key is pressed.
    """

    def __init__(self,
            parent_layout: Layout,
            font: pygame.Font,
            preferred_size: Optional[Size | tuple[float, float] | list[float, float]] = (130, 40),
            antialiasing: bool = True,
            placeholder: str = "",
            padding: int = 4
            ) -> None:
        """
        Parameters
        ----------
        parent_layout
            The layout that this widget belongs to.
        font
            Font object to be used to render text.
        size
            Dimensions of the widget.
        antialiasing
            Whether to use anti-aliasing while rendering text.
        placeholder
            Text to show when the input area is empty.
        """

        self.text = ""
        self.placeholder = placeholder
        self.font = font
        self.antialiasing = antialiasing
        self.padding = padding
        self.cursor_pos = 0

        self.cursor_blink_duration = 500
        self._cursor_blink_last = time.time()
        self._cursor_blink = False

        self.text_color = pygame.Color(0, 0, 0)
        self.placeholder_color = pygame.Color(145, 145, 145)
        self.selection_color = pygame.Color(51, 153, 255)
        self.hover_border_color = pygame.Color(86, 157, 229)
        self.border_color = pygame.Color(10, 10, 16)

        self.allow_copying = True
        self.allow_pasting = True

        self._scroll = 0
        self._sel_on = False
        self._ssel_on = False
        self._sel_done = False
        self._sel_start = -1
        self._sel_end = -1
        self._prev_cursor = None

        self.enter_pressed = Hook()

        super().__init__(parent_layout, preferred_size=preferred_size)

    def _get_text_size(self) -> tuple[int, int]:
        text_surf = self.font.render(self.text, self.antialiasing, (0, 0, 0))
        return text_surf.get_size()
    
    def _get_partial_text_size(self, index: int) -> tuple[int, int]:
        if len(self.text) == 0: return (0, 0)
        text_surf = self.font.render(self.text[:index], self.antialiasing, (0, 0, 0))
        return text_surf.get_size()
    
    def _get_char_size(self, index: int) -> tuple[int, int]:
        if len(self.text) == 0: return (0, 0)
        text_surf = self.font.render(self.text[index], self.antialiasing, (0, 0, 0))
        return text_surf.get_size()
    
    def _coords_to_text_index(self, coord: int) -> int:
        # TODO: Find a better approach, currently it renders the text many
        #       times and the performance gets affected heavily.

        if len(self.text) == 0: return -1

        for i in range(len(self.text)):
            t0 = self._get_partial_text_size(i)[0] + self.padding
            chr0 = self._get_char_size(i)[0] + self.padding
            t1 = self._get_partial_text_size(i + 1)[0] + self.padding
            c = coord + self._scroll

            if t0 < c + chr0 / 2 < t1:
                return i
            
        if t0 < c:
            return i + 1
            
        return -1
    
    def _reset_cursor_blink(self) -> None:
        self._cursor_blink_last = time.time()
        self._cursor_blink = False

    def _get_first_non_space(self, string: str) -> int:
        fi = string.find(" ")
                                
        for i in range(fi + 1, len(string)):
            if string[i] != " ":
                return i
            
        return -1

    def update(self, events: list[pygame.Event]) -> None:
        super().update(events)

        now = time.time()
        if (now - self._cursor_blink_last) * 1000 > self.cursor_blink_duration:
            self._cursor_blink_last = now

            self._cursor_blink = not self._cursor_blink
            self.paint_event() 

        if not self.on_focus: return

        for event in events:
            if event.type == pygame.TEXTINPUT:
                if self._sel_done:
                    if self._sel_start > self._sel_end:
                        sel_start = self._sel_end
                        sel_end = self._sel_start
                    else:
                        sel_start = self._sel_start
                        sel_end = self._sel_end

                    sel_start += 1

                    if self._sel_start > self._sel_end:
                        old_cursor_x = self._get_partial_text_size(self._sel_start)[0]
                    else:
                        old_cursor_x = self._get_partial_text_size(self._sel_end)[0]

                    first_slice = self.text[:sel_start]
                    second_slice = self.text[sel_end:]
                    self.text = first_slice[:-1] + event.text + second_slice

                    self.cursor_pos = sel_start
                    if self.cursor_pos < 0: self.cursor_pos = 0

                    cursor_x = self._get_partial_text_size(self.cursor_pos)[0]

                    self.unselect()

                    if self._scroll > 0:
                        self._scroll -= old_cursor_x - cursor_x

                    if self._scroll < 0: self._scroll = 0

                elif not self._sel_on:
                    self._reset_cursor_blink()

                    if self.cursor_pos == len(self.text):
                        self.text += event.text

                    else:
                        first_slice = self.text[:self.cursor_pos]
                        second_slice = self.text[self.cursor_pos:]
                        self.text = first_slice + event.text + second_slice

                    self.cursor_pos += 1

                    cursor_x = self._get_partial_text_size(self.cursor_pos)[0]
                    input_width = self.current_size.width - self.padding * 2

                    if cursor_x - self._scroll > input_width:
                        self._scroll += cursor_x - self._scroll - input_width

                self.paint_event()

            elif event.type == pygame.KEYDOWN:
                if not (self._sel_on and not self._sel_done):

                    # Delete the character before the cursor
                    # or the selected text
                    if event.key == pygame.K_BACKSPACE:
                        self._reset_cursor_blink()

                        if len(self.text) > 0:
                            if self._sel_done:
                                if self._sel_start > self._sel_end:
                                    sel_start = self._sel_end
                                    sel_end = self._sel_start
                                else:
                                    sel_start = self._sel_start
                                    sel_end = self._sel_end

                                sel_start += 1

                                if self._sel_start > self._sel_end:
                                    old_cursor_x = self._get_partial_text_size(self._sel_start)[0]
                                else:
                                    old_cursor_x = self._get_partial_text_size(self._sel_end)[0]

                                first_slice = self.text[:sel_start]
                                second_slice = self.text[sel_end:]
                                self.text = first_slice[:-1] + second_slice

                                self.cursor_pos = sel_start - 1
                                if self.cursor_pos < 0: self.cursor_pos = 0

                                cursor_x = self._get_partial_text_size(self.cursor_pos)[0]

                                self.unselect()
                            
                            elif event.mod == pygame.KMOD_LCTRL:
                                first_space = self.text[:self.cursor_pos].rstrip().rfind(" ") + 1
                                old_cursor_x = self._get_partial_text_size(self.cursor_pos)[0]

                                first_slice = self.text[:first_space]
                                second_slice = self.text[self.cursor_pos:]
                                self.text = first_slice + second_slice

                                self.cursor_pos = first_space
                                if self.cursor_pos < 0: self.cursor_pos = 0

                                cursor_x = self._get_partial_text_size(self.cursor_pos)[0]

                            else:
                                old_cursor_x = self._get_partial_text_size(self.cursor_pos)[0]

                                first_slice = self.text[:self.cursor_pos]
                                second_slice = self.text[self.cursor_pos:]
                                self.text = first_slice[:-1] + second_slice

                                self.cursor_pos -= 1
                                if self.cursor_pos < 0: self.cursor_pos = 0

                                cursor_x = self._get_partial_text_size(self.cursor_pos)[0]

                            if self._scroll > 0:
                                self._scroll -= old_cursor_x - cursor_x

                                if self._scroll < 0: self._scroll = 0

                    # Copy selection to clipboard
                    elif self.allow_copying and event.key == pygame.K_c and event.mod == pygame.KMOD_LCTRL:
                        sel_text = self.get_selection()
                        pygame.scrap.put_text(sel_text)

                    # Paste clipboard
                    elif self.allow_pasting and event.key == pygame.K_v and event.mod == pygame.KMOD_LCTRL:
                        clipboard = pygame.scrap.get_text().replace("\n", "")
                        if len(clipboard) == 0: return

                        if self._sel_done:
                            if self._sel_start > self._sel_end:
                                sel_start = self._sel_end
                                sel_end = self._sel_start
                            else:
                                sel_start = self._sel_start
                                sel_end = self._sel_end

                            sel_start += 1

                            if self._sel_start > self._sel_end:
                                old_cursor_x = self._get_partial_text_size(self._sel_start)[0]
                            else:
                                old_cursor_x = self._get_partial_text_size(self._sel_end)[0]

                            first_slice = self.text[:sel_start]
                            second_slice = self.text[sel_end:]
                            self.text = first_slice[:-1] + clipboard + second_slice

                            self.cursor_pos = sel_start + len(clipboard) - 1
                            if self.cursor_pos < 0: self.cursor_pos = 0

                            cursor_x = self._get_partial_text_size(self.cursor_pos)[0]

                            self.unselect()

                            if self._scroll > 0:
                                self._scroll -= old_cursor_x - cursor_x

                            if self._scroll < 0: self._scroll = 0
                        
                        else:
                            if self.cursor_pos == len(self.text):
                                self.text += clipboard

                            else:
                                first_slice = self.text[:self.cursor_pos]
                                second_slice = self.text[self.cursor_pos:]
                                self.text = first_slice + clipboard + second_slice

                            self.cursor_pos += len(clipboard)

                            cursor_x = self._get_partial_text_size(self.cursor_pos)[0]
                            input_width = self.current_size.width - self.padding * 2

                            if cursor_x - self._scroll > input_width:
                                self._scroll += cursor_x - self._scroll - input_width

                    # Move cursor right
                    elif event.key == pygame.K_LEFT:
                        self._reset_cursor_blink()

                        if self._sel_done:
                            self.unselect()

                        else:
                            if event.mod == pygame.KMOD_LSHIFT:
                                if not self._ssel_on:
                                    self._ssel_on = True
                                    self._sel_start = self.cursor_pos

                            if event.mod == pygame.KMOD_LCTRL:
                                first_space = self.text[:self.cursor_pos].rstrip().rfind(" ")
                                self.cursor_pos = first_space + 1
                            
                            else:
                                self.cursor_pos -= 1

                            if self.cursor_pos < 0: self.cursor_pos = 0

                            if event.mod == pygame.KMOD_LSHIFT:
                                if self._ssel_on:
                                    self._sel_end = self.cursor_pos

                            cursor_x = self._get_partial_text_size(self.cursor_pos)[0]

                            if cursor_x < self._scroll:
                                self._scroll -= self._scroll - cursor_x

                    # Move cursor left
                    elif event.key == pygame.K_RIGHT:
                        self._reset_cursor_blink()

                        if self._sel_done:
                            self.unselect()

                        else:
                            if event.mod == pygame.KMOD_LSHIFT:
                                if not self._ssel_on:
                                    self._ssel_on = True
                                    self._sel_start = self.cursor_pos

                            if event.mod == pygame.KMOD_LCTRL:
                                t = self.text[self.cursor_pos:]
                                # Adding ' .' at the end as a hacky solution
                                # for jumping the cursor to the end
                                i = self._get_first_non_space(t + " .")
                                self.cursor_pos += i
                            
                            else:
                                self.cursor_pos += 1

                            if self.cursor_pos > len(self.text):
                                self.cursor_pos -= 1

                            if event.mod == pygame.KMOD_LSHIFT:
                                if self._ssel_on:
                                    self._sel_end = self.cursor_pos

                            cursor_x = self._get_partial_text_size(self.cursor_pos)[0]
                            input_width = self.current_size.width - self.padding * 2

                            if cursor_x - self._scroll > input_width:
                                self._scroll += cursor_x - self._scroll - input_width

                    # Select all
                    elif event.key == pygame.K_a and event.mod == pygame.KMOD_LCTRL:
                        self._sel_start = 0
                        self._sel_end = len(self.text)
                        self._sel_on = True
                        self._sel_done = True

                    elif event.key == pygame.K_RETURN:
                        self.unselect()
                        self.enter_pressed.emit()

                    # Jump cursor to the beginning
                    elif event.key == pygame.K_HOME and len(self.text) > 0:
                        self._reset_cursor_blink()
                        self.unselect()

                        self.cursor_pos = 0

                        cursor_x = self._get_partial_text_size(self.cursor_pos)[0]

                        if cursor_x < self._scroll:
                            self._scroll -= self._scroll - cursor_x

                    # Jump cursor to the end
                    elif event.key == pygame.K_END and len(self.text) > 0:
                        self._reset_cursor_blink()
                        self.unselect()

                        self.cursor_pos = len(self.text)

                        cursor_x = self._get_partial_text_size(self.cursor_pos)[0]
                        input_width = self.current_size.width - self.padding * 2

                        if cursor_x - self._scroll > input_width:
                            self._scroll += cursor_x - self._scroll - input_width

                    self.paint_event()

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LSHIFT:
                    if self._ssel_on:
                        self._sel_done = True

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self._hovered:
                    mx = event.pos[0] - self.position.x
                    mi = self._coords_to_text_index(mx)

                    if mi != -1:
                        self.cursor_pos = mi
                        self._sel_on = True
                        self._sel_done = False
                        self._sel_start = self.cursor_pos
                        self.paint_event()

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self._sel_start == self._sel_end:
                    self.unselect()

                elif self._sel_on:
                    self._sel_done = True
                    self.paint_event()

        if self._sel_on and not self._sel_done:
            mx = pygame.mouse.get_pos()[0] - self.position.x

            mi = self._coords_to_text_index(mx)

            if mi != -1:
                self.cursor_pos = mi
                self._sel_end = self.cursor_pos

                self.paint_event()

    def update_surface(self):
        self._padded_surf = pygame.Surface(
            (self.current_size.width - self.padding * 2, self.current_size.height - self.padding * 2),
            pygame.SRCALPHA
        ).convert_alpha()

        super().update_surface()

    def unselect(self) -> None:
        """ Remove the text selection. """

        self._sel_on = False
        self._ssel_on = False
        self._sel_done = False
        self._sel_start = -1
        self._sel_end = -1

    def get_selection(self) -> str:
        """ Return the text in the selected area. """

        if not self._sel_done: return ""

        if self._sel_start > self._sel_end:
            sel_start = self._sel_end
            sel_end = self._sel_start
        else:
            sel_start = self._sel_start
            sel_end = self._sel_end

        return self.text[sel_start:sel_end]
    
    def clear(self) -> None:
        """ Clear the contents of text input. """

        self.text = ""
        self._reset_cursor_blink()
        self.unselect()

        self.cursor_pos = 0

        cursor_x = self._get_partial_text_size(self.cursor_pos)[0]

        if cursor_x < self._scroll:
            self._scroll -= self._scroll - cursor_x

        self.paint_event()

    def paint_event(self) -> None:
        self._padded_surf.fill((0, 0, 0, 0))
        self.surface.fill((0, 0, 0, 0))

        # selection color is also inverted because of text
        sel_color = (
            255 - self.selection_color.r,
            255 - self.selection_color.g,
            255 - self.selection_color.b
        )

        # Draw selection
        sel_rect = None

        if (self._sel_on or self._ssel_on) and self._sel_start != -1 and self._sel_end != -1:
            if self._sel_start > self._sel_end:
                sel_start = self._sel_end
                sel_end = self._sel_start
            else:
                sel_start = self._sel_start
                sel_end = self._sel_end

            sel_x = self._get_partial_text_size(sel_start)[0]
            sel_w = self._get_partial_text_size(sel_end)[0] - sel_x

            sel_rect = pygame.Rect(
                sel_x + self.padding - self._scroll,
                self.padding,
                sel_w,
                self.current_size.height - self.padding * 2
            )

            pygame.draw.rect(
                self.surface,
                sel_color,
                sel_rect
            )

        # Draw placeholder text
        if len(self.text) == 0:
            ph_surf = self.font.render(
                self.placeholder,
                self.antialiasing,
                self.placeholder_color
            )

            height = ph_surf.get_height()

            self.surface.blit(ph_surf, (self.padding, self.current_size.height / 2 - height / 2))

        # Draw text
        else:
            text_surf = self.font.render(self.text, self.antialiasing, self.text_color)
            height = text_surf.get_height()

            self._padded_surf.blit(
                text_surf, (-self._scroll, self._padded_surf.get_height() / 2 - height / 2)
            )

            self.surface.blit(self._padded_surf, (self.padding, self.padding))

            # Invert the selection area
            if sel_rect is not None:
                subsurf = pygame.Surface(sel_rect.size, pygame.SRCALPHA).convert_alpha()
                subsurf.blit(self.surface, (-sel_rect.x, -sel_rect.y))
                subsurf = pygame.transform.invert(subsurf)
                self.surface.blit(subsurf, sel_rect)

        # Draw cursor
        if self.on_focus and not self._cursor_blink:
            cursor_x = self._get_partial_text_size(self.cursor_pos)[0]

            pygame.draw.line(
                self.surface,
                self.text_color,
                (
                    self.padding + cursor_x - self._scroll,
                    self.padding
                ),
                (
                    self.padding + cursor_x - self._scroll,
                    self.current_size.height - self.padding
                ),
                1
            )

        if self.on_focus:
            border_color = self.hover_border_color
        else:
            border_color = self.border_color

        pygame.draw.rect(
            self.surface, border_color, (0, 0, self.current_size.width, self.current_size.height), 1
        )
    
    def focus_event(self) -> None:
        self._reset_cursor_blink()
        self.paint_event()

    def unfocus_event(self) -> None:
        self.unselect()
        self.paint_event()

    def mouse_enter_event(self, position: pygame.Vector2) -> None:
        self._prev_cursor = pygame.mouse.get_cursor()
        pygame.mouse.set_cursor(pygame.Cursor(pygame.SYSTEM_CURSOR_IBEAM))

    def mouse_leave_event(self, position: pygame.Vector2) -> None:
        pygame.mouse.set_cursor(self._prev_cursor)