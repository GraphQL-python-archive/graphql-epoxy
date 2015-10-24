def maybe_callable(obj):
    if callable(obj) and not hasattr(obj, 'T'):
        return obj()

    return obj
