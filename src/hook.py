from typing import Callable


class Hook:
    """
    Callback handler for widget events.

    Similar to Qt's signal & slot system, hooks basically stores and emits
    callbacks to their owners. Widgets can have multiple hooks for specific actions.
    """

    def __init__(self) -> None:
        self.callbacks = []

    def connect(self, func: Callable) -> Callable:
        """
        Connect a callback function to this hook.

        Parameters
        ----------
        func
            Callback to connect.
        """

        self.callbacks.append(func)
        return func
    
    def emit(self, *args, **kwargs) -> None:
        """ Emit the hook. """

        for callback in self.callbacks:
            callback(*args, **kwargs)