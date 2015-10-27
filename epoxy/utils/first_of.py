from .maybe_callable import maybe_callable


def first_of(*args):
    for arg in args:
        arg = maybe_callable(arg)
        if arg:
            return arg
