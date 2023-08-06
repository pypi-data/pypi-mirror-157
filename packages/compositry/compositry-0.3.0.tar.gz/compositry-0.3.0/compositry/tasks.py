# Encoding: UTF-8
# pylint: disable=missing-module-docstring

import functools as fn
from typing import Callable, Optional

import colorama


class Task:
    """Manages tasks."""

    registry: dict[int, Callable] = {}

    @classmethod
    def register(
        cls,
        task: Callable = None,  # type: ignore
        *,
        deprecated: str = "",
        on_decorated: Optional[Callable[[Callable], Callable]] = None,
        on_preprocess: Optional[Callable[[tuple, dict], tuple[tuple, dict]]] = None,
        on_register: Optional[Callable] = None,
    ):
        """Registers a function as a task.

        Register a given function as a task (usually a stateless, functional component).
        For stateful tasks, one may use (although is not limited to) closures and/or
        stores.

        ### Parameters
            - function: `Callable`
                - Function to register as a task.
            - *
            - deprecated: `str`
                - Mark a task as deprecated and print an informative message.
            - on_decorated: `Optional[Callable[[Callable], Callable]]`
                - Callback hook to modify the task's attributes.
            - on_preprocess: `Optional[Callable[[tuple, dict], tuple[tuple, dict]]]`
                - Callback hook to preprocess a task's inputs.
            - on_register: `Optional[Callable]`
                - Callback hook to run a function on registration.

        ### Raises
            - `TypeError`: The task is not a function.
        """

        # Another layer is added in the event I can make being able to use the decorator
        # with or without the parentheses possible. Future proofing, in a nutshell.
        def _decorator(add_parentheses_to_the_decorator: Callable) -> Callable:
            # Constants
            BG = colorama.Back  # pylint: disable=invalid-name
            FG = colorama.Fore  # pylint: disable=invalid-name
            style = colorama.Style

            if deprecated:
                print(f"{BG.YELLOW}{FG.BLACK} WARN {style.RESET_ALL} {deprecated}")

            @fn.wraps(task)
            def _wrapper(*args, **kwargs):
                if on_preprocess:
                    hook = on_preprocess(*args, **kwargs)
                    return add_parentheses_to_the_decorator(*hook[0], *hook[1])

                return add_parentheses_to_the_decorator(*args, **kwargs)

            # Adds the task to the registry if not there
            if _wrapper not in cls.registry.values():
                _ = add_parentheses_to_the_decorator
                cls.registry.update({hash(_wrapper): _})

                if not isinstance(_, Callable):
                    print(f"{BG.RED}{FG.BLACK} ERROR! {style.RESET_ALL}")
                    raise ValueError(f"{_} is not a function.")

            # Calls the given function during registration
            if isinstance(on_register, Callable):
                on_register()

            # Same as above, but modifies the returned task
            if isinstance(on_decorated, Callable):
                return on_decorated(_wrapper)

            return _wrapper

        if task is None:
            return _decorator
        return _decorator(task)

    @classmethod
    def deregister(cls, task: Callable) -> None:
        """Deregisters a task and makes it completely unusable.

        Deregister a task from the registry, rendering it completely unusable on future
        calls to the task. This does not work with tasks that are not being tracked and
        it is recommended to use this with caution.

        ### Parameters
            - task: `Callable`
                - Task to deregister.
        """
        if hash(task) in cls.registry:
            del globals()[cls.registry[hash(task)].__name__]
            cls.registry.pop(hash(task))


__all__ = ("Task",)
