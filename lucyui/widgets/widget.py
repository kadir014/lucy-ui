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
from lucyui.core.models import ConstrainedBoxModel, MouseButton
from lucyui.core.types import SizeLike, Coordinate

if TYPE_CHECKING:
    from lucyui.layouts import Layout


class Widget(ConstrainedBoxModel):
    """
    Base user interface element.

    Widgets are the base building block for all user interface elements that are
    displayed on the window and can be interacted with.

    Their geometry is usually controlled and adjusted by parent layouts.

    Attributes
    ----------
    on_focus
        Boolean indicating if the widget is currently on focus or not.
    parent_layout
        Parenting layout of this widget, can be None.
    doube_click_duration
        Delay needed for a double click to register in milliseconds.
    repaint_on_mouse_interaction
        Whether to repaint the widget on mouse events like pressing or hovering.
    """

    def __init__(self,
            preferred_size: Optional[SizeLike] = None,
            relative_position: Coordinate = (0.0, 0.0)
            ) -> None:
        """
        Parameters
        ----------
        preferred_size
            Preferred dimensions of the widget.
        relative_position
            Position relative to parent.
            Only needed if this widget is not handled by a layout.
        """

        if preferred_size is None: preferred_size = Size(10, 10)
        else: preferred_size = Size(*preferred_size)

        super().__init__(preferred_size, pygame.Vector2(relative_position))

        self.__need_repaint = False

        self.__is_visible = True

        self.__horizontal_behavior = SizeBehavior.FIXED
        self.__vertical_behavior = SizeBehavior.FIXED

        self._hovered = False
        self._pressed = [False, False, False]

        self._last_pressed = 0.0

        # Public attributes
        self.on_focus = False
        self.parent_layout: "Layout" = None
        self.double_click_duration = 500.0
        self.repaint_on_mouse_interaction = False

        self.update_surface()

    @property
    def position(self) -> pygame.Vector2:
        """ Widget's absolute position in screen space. """
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

    @property
    def is_visible(self) -> float:
        """
        Whether the widget is visible or not.
        
        Hidden widgets are not processed or rendered.
        """
        return self.__is_visible

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

        if not self.__is_visible:
            return

        global_mouse = pygame.Vector2(*pygame.mouse.get_pos())
        local_mouse = global_mouse - self.position

        if self.absolute_frect.collidepoint(global_mouse.x, global_mouse.y):
            if not self._hovered:
                self.mouse_enter_event(local_mouse, global_mouse)

            self._hovered = True
            
            if self.repaint_on_mouse_interaction:
                self.repaint()
        else:
            if self._hovered:
                self.mouse_leave_event(local_mouse, global_mouse)

            self._hovered = False

            if self.repaint_on_mouse_interaction:
                self.repaint()

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    elapsed = (perf_counter() - self._last_pressed) * 1000.0
                    if elapsed < self.double_click_duration:
                        self._last_pressed = 0
                        self.mouse_double_click_event(local_mouse, global_mouse)

                    self._last_pressed = perf_counter()
                    
                if self._hovered:
                    self._pressed[event.button - 1] = True
                    button = MouseButton.from_pygame_event(event)
                    self.mouse_press_event(button, local_mouse, global_mouse)
                    self.focus()

                    if self.repaint_on_mouse_interaction:
                        self.repaint()

                else:
                    self.unfocus()

            elif event.type == pygame.MOUSEBUTTONUP:
                if self._pressed[event.button - 1]:
                    self._pressed[event.button - 1] = False
                    button = MouseButton.from_pygame_event(event)
                    self.mouse_release_event(button, local_mouse, global_mouse)

                    if self.repaint_on_mouse_interaction:
                        self.repaint()

            elif event.type == pygame.MOUSEWHEEL:
                if self._hovered:
                    precise_scroll = pygame.Vector2(event.precise_x, event.precise_y)
                    self.mouse_wheel_event(precise_scroll)

                    if self.repaint_on_mouse_interaction:
                        self.repaint()

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

        if not self.__is_visible:
            return

        if self.surface is not None:
            if self.__need_repaint:
                self.paint_event()
                self.__need_repaint = False

            surface.blit(self.surface, self.position)

    def update_surface(self, repaint: bool = True) -> None:
        """
        Update the widget surface and repaint.

        This method is usually called internally by layout management.

        Parameters
        ----------
        repaint
            Request a repaint after updating the surface.
        """

        if not self.current_size.is_valid():
            self.surface = None
            return
        
        self.surface = pygame.Surface(
            self.current_size.to_tuple(),
            pygame.SRCALPHA
        ).convert_alpha()
        
        if repaint:
            self.repaint()

    def repaint(self) -> None:
        """ Request a repaint. """
        self.__need_repaint = True
    
    def focus(self) -> None:
        """ Get the widget in focus. """

        if not self.on_focus:
            self.on_focus = True
            self.focus_event()
        else:
            self.on_focus = True

    def unfocus(self) -> None:
        """ Get the widget out of focus. """

        if self.on_focus:
            self.on_focus = False
            self.unfocus_event()
        else:
            self.on_focus = False

    def show(self) -> None:
        """ Make the widget visible. """

        self.__is_visible = True

        if self.parent_layout is not None:
            self.parent_layout.realign()

    def hide(self) -> None:
        """ Make the widget hidden. """

        self.__is_visible = False

        if self.parent_layout is not None:
            self.parent_layout.realign()

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

    def mouse_enter_event(self,
            local_position: pygame.Vector2,
            global_position: pygame.Vector2
            ) -> None:
        """ 
        This event can be implemented in a subclass to
        receive when the mouse cursor enters the widget.

        Parameters
        ----------
        local_position
            Local mouse position (in widget space) where this event occured.
        global_position
            Global mouse position (in screen space) where this event occured.
        """

    def mouse_leave_event(self,
            local_position: pygame.Vector2,
            global_position: pygame.Vector2
            ) -> None:
        """ 
        This event can be implemented in a subclass to
        receive when the mouse cursor leaves the widget.

        Parameters
        ----------
        local_position
            Local mouse position (in widget space) where this event occured.
        global_position
            Global mouse position (in screen space) where this event occured.
        """

    def mouse_press_event(self,
            button: MouseButton,
            local_position: pygame.Vector2,
            global_position: pygame.Vector2
            ) -> None:
        """ 
        This event can be implemented in a subclass to
        receive when the mouse button is pressed.

        Parameters
        ----------
        button
            Mouse button state.
        local_position
            Local mouse position (in widget space) where this event occured.
        global_position
            Global mouse position (in screen space) where this event occured.
        """

    def mouse_release_event(self,
            button: MouseButton,
            local_position: pygame.Vector2,
            global_position: pygame.Vector2
            ) -> None:
        """
        This event can be implemented in a subclass to
        receive when the mouse button is released.

        Parameters
        ----------
        button
            Mouse button state.
        local_position
            Local mouse position (in widget space) where this event occured.
        global_position
            Global mouse position (in screen space) where this event occured.
        """

    def mouse_double_click_event(self,
            local_position: pygame.Vector2,
            global_position: pygame.Vector2
            ) -> None:
        """
        This event can be implemented in a subclass to
        receive when the mouse is double clicked.

        Parameters
        ----------
        local_position
            Local mouse position (in widget space) where this event occured.
        global_position
            Global mouse position (in screen space) where this event occured.
        """

    def mouse_wheel_event(self, scroll: pygame.Vector2) -> None:
        """
        This event can be implemented in a subclass to
        receive when the mouse wheel is scrolled.

        Parameters
        ----------
        scroll
            Amount of wheel scroll in each axis.
        """