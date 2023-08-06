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


def verbose(_func: object=None, *, message: str=None, stream: str="stdout") -> object:
    """Print [message] for telling what the function does or is about to do."""
    def decorator(func: object) -> object:
        @functools.wraps(func)
        def wrapper(*args: tuple, **kwargs: dict) -> None:
            if message:
                if not isinstance(message, str):
                    raise TypeError("Message has to be string")
                if stream == "stdout":
                    print(message, file=sys.stdout)
                elif stream == "stderr":
                    print(message, file=sys.stderr)
                else:
                    raise ValueError("Stream has to be either 'stdout' or 'stderr'")
            func(*args, **kwargs)
        return wrapper
    return decorator if _func is None else decorator(_func)


def slow_down(_func: object=None, *, interval: int | float=1) -> object:
    """Sleep [interval] before calling the function."""
    def decorator(func: object) -> object:
        @functools.wraps(func)
        def wrapper(*args: tuple, **kwargs: dict) -> None:
            if not any([isinstance(interval, int), isinstance(interval, float)]):
                raise TypeError("Interval has to be either int or float")
            time.sleep(interval)
            func(*args, **kwargs)
        return wrapper
    return decorator if _func is None else decorator(_func)
