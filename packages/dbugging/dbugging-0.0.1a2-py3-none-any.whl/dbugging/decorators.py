"""Decorators."""

import functools
import sys
import time


def debug(func: object) -> object:
    """Print the function signature and (possible) return value."""
    @functools.wraps(func)
    def wrapper(*args: tuple, **kwargs: dict) -> None:
        args_repr: list = [repr(a) for a in args]
        kwargs_repr: list = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature: str = ", ".join(args_repr + kwargs_repr)
        print(f"Calling {func.__name__}({signature})")
        value: object = func(*args, **kwargs)
        print(f"{func.__name__!r} returned {value!r}")
        return value
    return wrapper


def verbose(message: str, stream: str="stdout") -> object:
    """Print verbose message about an ongoing operation."""
    def decorator(func: object) -> object:
        @functools.wraps(func)
        def wrapper(*args: tuple, **kwargs: dict) -> None:
            if not isinstance(message, str):
                raise TypeError(f"Invalid type {message}, needs to be string")
            if stream == "stdout":
                print(message, file=sys.stdout)
            elif stream == "stderr":
                print(message, file=sys.stderr)
            else:
                raise ValueError(f"Invalid value {stream}, use 'stdout' or 'stderr'")
            func(*args, **kwargs)
        return wrapper
    return decorator


def slow_down(interval: int=1) -> object:
    """Sleep [interval] before calling the function."""
    def decorator(func: object) -> object:
        @functools.wraps(func)
        def wrapper(*args: tuple, **kwargs: dict) -> None:
            if not isinstance(interval, int):
                raise TypeError("Interval must be an integer")
            time.sleep(interval)
            func(*args, **kwargs)
        return wrapper
    return decorator
