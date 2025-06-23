"""

    lucy-ui  -  Pygame UI & Layout Library

    This file is a part of the lucy-ui
    project and distributed under MIT license.
    https://github.com/kadir014/lucy-ui

"""

from typing import TYPE_CHECKING, Optional
from time import perf_counter

import pygame

from lucyui.core import SizeBehavior, Size
from lucyui.core.models import ConstrainedBoxModel
from lucyui.core.types import SizeLike

if TYPE_CHECKING:
    from lucyui.layouts import Layout


class Widget(ConstrainedBoxModel):
    """
    Base user interface element.

    Widget is the base component for all user interface elements that are
    displayed on the window and can be interacted with.
    """

    def __init__(self,
            preferred_size: Optional[SizeLike] = None,
            double_click_duration: float = 500.0
            ) -> None:
        """
        Parameters
        ----------
        preferred_size
            Preferred dimensions of the widget.
        double_click_duration
            Delay needed for a double click to register in milliseconds.
        """

        if preferred_size is None: preferred_size = Size(10, 10)
        else: preferred_size = Size(*preferred_size)

        super().__init__(
            preferred_size,
            pygame.Vector2(0, 0)
        )

        self.__horizontal_behavior = SizeBehavior.FIXED
        self.__vertical_behavior = SizeBehavior.FIXED

        self._hovered = False
        self._pressed = False

        self.on_focus = False

        self.double_click_duration = double_click_duration
        self._last_pressed = 0

        self.parent_layout: "Layout" = None

        self.update_surface()

    @property
    def position(self) -> pygame.Vector2:
        """ Widget's absolute position. """
        return self.parent_layout.get_absolute_position(self.relative_position)
    
    @property
    def absolute_rect(self) -> pygame.Rect:
        """ pygame.Rect object representing widget's absolute geometry. """
        return pygame.Rect(
            self.position.x,
            self.position.y,
            self.current_size.width,
            self.current_size.height
        )
    
    @property
    def absolute_frect(self) -> pygame.FRect:
        """ pygame.FRect object representing widget's absolute geometry. """
        return pygame.FRect(
            self.position.x,
            self.position.y,
            self.current_size.width,
            self.current_size.height
        )
    
    @property
    def size_behavior(self) -> tuple[SizeBehavior, SizeBehavior]:
        """ Horizontal and vertical size behavior of the widget. """
        return (self.__horizontal_behavior, self.__vertical_behavior)
    
    @size_behavior.setter
    def size_behavior(self, value: tuple[SizeBehavior, SizeBehavior]) -> None:
        self.__horizontal_behavior = value[0]
        self.__vertical_behavior = value[1]
        
        if self.parent_layout is not None:
            self.parent_layout.realign()

    @property
    def horizontal_behavior(self) -> SizeBehavior:
        """ Horizontal size behavior of the widget. """
        return self.__horizontal_behavior
    
    @horizontal_behavior.setter
    def horizontal_behavior(self, value: SizeBehavior) -> None:
        self.__horizontal_behavior = value
        
        if self.parent_layout is not None:
            self.parent_layout.realign()

    @property
    def vertical_behavior(self) -> SizeBehavior:
        """ Vertical size behavior of the widget. """
        return self.__vertical_behavior
    
    @vertical_behavior.setter
    def vertical_behavior(self, value: SizeBehavior) -> None:
        self.__vertical_behavior = value
        
        if self.parent_layout is not None:
            self.parent_layout.realign()

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

        if self.absolute_frect.collidepoint(mouse.x, mouse.y):
            if not self._hovered: self.mouse_enter_event(mouse)
            self._hovered = True
        else:
            if self._hovered: self.mouse_leave_event(mouse)
            self._hovered = False

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if (perf_counter() - self._last_pressed) * 1000 < self.double_click_duration:
                    self._last_pressed = 0
                    self.mouse_double_click_event(pygame.Vector2(*event.pos))
                    
                if event.button == 1:
                    if self._hovered:
                        self._pressed = True
                        self._last_pressed = perf_counter()
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

        if self.surface is not None:
            surface.blit(self.surface, self.position)

    def update_surface(self) -> None:
        """
        Update the widget surface and repaint.

        This method is usually called internally by layout management.
        """

        if not self.current_size.is_valid():
            self.surface = None
            return
        
        self.surface = pygame.Surface(self.current_size.to_tuple(), pygame.SRCALPHA).convert_alpha()
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

    def paint_event(self) -> None:
        """
        This event can be implemented in a subclass to repaint the widget surface.
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