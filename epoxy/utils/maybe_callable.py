def maybe_callable(obj):
    if callable(obj):
        return obj()

    return obj
