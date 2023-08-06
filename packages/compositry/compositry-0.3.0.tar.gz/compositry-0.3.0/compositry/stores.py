# Encoding: UTF-8
# pylint: disable=missing-module-docstring

from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    Final,
    Generic,
    Hashable,
    Optional,
    TypeVar,
    Union,
)

S = TypeVar("S")
_NONE: Final = type


@dataclass
class Writable(Generic[S]):
    """Stores a readable/writable value."""

    state: S

    @classmethod
    def __post_init__(cls) -> None:
        cls.global_store: dict = {}

    def __call__(self, state: Union[S, _NONE] = _NONE):
        if state is _NONE:
            return self.state

        self.state = state
        return None

    def get(self):
        """Get the current state."""
        return self.state

    def set(self, state: S) -> None:
        """Set the current state."""
        self.state = state

    @classmethod
    def get_global(cls, key):
        """Get state from the global store."""
        return cls.global_store[key]

    @classmethod
    def set_global(cls, key: Hashable, value: Any) -> None:
        """Set state from the global store."""
        cls.global_store.update({key: value})

    @classmethod
    def del_global(cls, key):
        """Delete state from the global store."""
        cls.global_store.pop(key)


@dataclass
class Derive(Generic[S]):
    """Derive from a store's value."""

    state: Writable
    callback: Optional[Callable[[Any], Any]] = None

    def __call__(self, get_callback: bool) -> None:
        if isinstance(self.callback, Callable):
            result = self.callback(self.state())
            if get_callback:
                return result

        return self.state()


__all__ = ("Writable", "Derive")
