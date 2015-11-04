from ..utils.thunk import ResolveThunk, ThunkList


class ClassTypeCreator(object):
    def __init__(self, registry, class_type_creator):
        self._registry = registry
        self._class_type_creator = class_type_creator

    def __getattr__(self, item):
        return self[item]

    def __getitem__(self, item):
        if isinstance(item, tuple):
            type_thunk = ThunkList([ResolveThunk(self._registry._resolve_type, i) for i in item])

        else:
            type_thunk = ThunkList([ResolveThunk(self._registry._resolve_type, item)])

        return self._class_type_creator(type_thunk)
