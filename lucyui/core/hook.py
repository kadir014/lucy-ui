"""

    lucy-ui  -  Pygame UI & Layout Library

    This file is a part of the lucy-ui
    project and distributed under MIT license.
    https://github.com/kadir014/lucy-ui

"""

from typing import Callable


class Hook:
    """
    Callback handler for widget actions.

    Similar to Qt's signal & slot system, hooks basically stores and emits
    callbacks to their owners. Widgets can have multiple hooks for specific actions.
    """

    def __init__(self) -> None:
        self._callbacks = set()

    def connect(self, func: Callable) -> Callable:
        """
        Connect a callback function to this hook.

        Parameters
        ----------
        func
            Callback to connect.
        """

        self._callbacks.add(func)
        return func
    
    def disconnect(self, func: Callable) -> None:
        """
        Disconnect a callback function from this hook.

        Parameters
        ----------
        func
            Callback to disconnect.
        """

        if func in self._callbacks:
            self._callbacks.remove(func)
    
    def emit(self, *args, **kwargs) -> None:
        """ Emit the hook. """

        for callback in self._callbacks:
            callback(*args, **kwargs)