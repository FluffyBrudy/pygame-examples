import logging
from collections.abc import Callable
from typing import Any

log = logging.getLogger(__name__)


def move_towards(src: float, dest: float, dx: float):
    abs_dx = abs(dx)
    if src < dest:
        return min(src + abs_dx, dest)
    return max(src - abs_dx, dest)


def emit_callbacks(callbacks: list[Callable[..., Any]], *args: Any, **kwargs: Any) -> None:
    for callback in list(callbacks):
        try:
            callback(*args, **kwargs)
        except Exception:
            log.exception("Error in callback %r", callback)
