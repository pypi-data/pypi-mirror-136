"""Decorators."""

import functools


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
