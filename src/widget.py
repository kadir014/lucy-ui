from typing import Optional
from time import time

import pygame

from .layout import Layout
from .enums import SizeBehavior


class Widget:
    """
    Base user interface element.

    Widget is the base component for all user interface elements that are
    displayed on the window and can be interacted with.
    """

    def __init__(self,
            parent_layout: Layout,
            preferred_size: Optional[list[int, int]] = None
            ) -> None:
        """
        Parameters
        ----------
        parent_layout
            The layout that this widget belongs to.
        preferred_size
            Preferred dimensions of the widget.
        """

        self.parent_layout = parent_layout
        self.parent_layout.children.append(self)

        self.relative_position = pygame.Vector2(0, 0)

        if preferred_size is None: preferred_size = [50, 25]
        self.preferred_size = preferred_size
        self.current_size = [*preferred_size]
        self.minimum_size = [None, None]
        self.maximum_size = [None, None]
        self.horizontal_behavior = SizeBehavior.FIXED
        self.vertical_behavior = SizeBehavior.FIXED

        self.update_surface()

        # Mouse states
        self._hovered = False
        self._pressed = False
        self.on_focus = False

        self.double_click_duration = 500
        self._last_pressed = 0

        self.parent_layout.realign()

    @property
    def position(self) -> pygame.Vector2:
        """ Widget's absolute position. """
        return self.parent_layout.get_absolute_position(self.relative_position)

    @property
    def rect(self) -> pygame.Rect:
        """ pygame.Rect object representing widget's geometry. """
        return pygame.Rect(self.position, self.current_size)
    
    @property
    def frect(self) -> pygame.FRect:
        """ pygame.FRect object representing widget's geometry. """
        return pygame.FRect(self.position, self.current_size)

    def update(self, events: list[pygame.Event]) -> None:
        """
        Process the widget logic.

        This method is called every frame by the layout that manages this
        widget.

        Parameters
        ----------
        events
            Event list returned by `pygame.event.get()`
        """

        mouse = pygame.Vector2(*pygame.mouse.get_pos())

        if self.rect.collidepoint(mouse.x, mouse.y):
            if not self._hovered: self.mouse_enter_event(mouse)
            self._hovered = True
        else:
            if self._hovered: self.mouse_leave_event(mouse)
            self._hovered = False

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if (time() - self._last_pressed) * 1000 < self.double_click_duration:
                    self._last_pressed = 0
                    self.mouse_double_click_event(pygame.Vector2(*event.pos))
                    
                if event.button == 1:
                    if self._hovered:
                        self._pressed = True
                        self._last_pressed = time()
                        self.mouse_press_event(pygame.Vector2(*event.pos))

                    else:
                        self.unfocus()

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if self._pressed:
                        self._pressed = False
                        self.mouse_release_event(pygame.Vector2(*event.pos))
                        self.focus()

    def render(self, surface: pygame.Surface) -> None:
        """
        Render the widget onto given surface.

        This method is called every frame by the layout that manages this
        widget. Usually there is no reason to override this function.

        Parameters
        ----------
        surface
            Surface to render the widget onto.
        """

        surface.blit(self.surface, self.position)

    def update_surface(self) -> None:
        """
        Update the widget surface and repaint.

        This method is usually called internally by layout management.
        """

        self.surface = pygame.Surface(self.current_size, pygame.SRCALPHA).convert_alpha()
        self.paint_event()
    
    def focus(self) -> None:
        """ Get the widget in focus. """

        if not self.on_focus:
            self.on_focus = True
            self.focus_event()
        else: self.on_focus = True

    def unfocus(self) -> None:
        """ Get the widget out of focus. """

        if self.on_focus:
            self.on_focus = False
            self.unfocus_event()
        else: self.on_focus = False

    def set_size_behavior(self,
            horizontal_behavior: SizeBehavior,
            vertical_behavior: SizeBehavior
            ) -> None:
        """
        Set the size behavior of the widget.

        Parameters
        ----------
        horizontal_behavior
            Size behavior for widget's width
        vertical_behavior
            Size behavior for widget's height
        """
        self.horizontal_behavior = horizontal_behavior
        self.vertical_behavior = vertical_behavior
        self.parent_layout.realign()

    def paint_event(self) -> None:
        """
        This event can be implemented in a subclass to repaint he widget surface.
        """
    
    def focus_event(self) -> None:
        """ 
        This event can be implemented in a subclass to
        receive when this widgets gets focused on.
        """

    def unfocus_event(self) -> None:
        """ 
        This event can be implemented in a subclass to
        receive when the focus of this widget is lost.
        """

    def mouse_enter_event(self, position: pygame.Vector2) -> None:
        """ 
        This event can be implemented in a subclass to
        receive when the mouse cursor enters the widget.

        Parameters
        ----------
        position
            Mouse position where this event occured.
        """

    def mouse_leave_event(self, position: pygame.Vector2) -> None:
        """ 
        This event can be implemented in a subclass to
        receive when the mouse cursor leaves the widget.

        Parameters
        ----------
        position
            Mouse position where this event occured.
        """

    def mouse_press_event(self, position: pygame.Vector2) -> None:
        """ 
        This event can be implemented in a subclass to
        receive when the mouse button is pressed.

        Parameters
        ----------
        position
            Mouse position where this event occured.
        """

    def mouse_release_event(self, position: pygame.Vector2) -> None:
        """
        This event can be implemented in a subclass to
        receive when the mouse button is released.

        Parameters
        ----------
        position
            Mouse position where this event occured.
        """

    def mouse_double_click_event(self, position: pygame.Vector2) -> None:
        """
        This event can be implemented in a subclass to
        receive when the mouse is double clicked.

        Parameters
        ----------
        position
            Mouse position where this event occured.
        """