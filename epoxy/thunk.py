import copy
from graphql.core.type.definition import GraphQLList, GraphQLNonNull
from .utils.gen_id import gen_id
from .utils.maybe_callable import maybe_callable


def clone_with_kwargs(thunk, kwargs):
    old_kwargs = thunk._kwargs
    if old_kwargs:
        kwargs = old_kwargs.copy().update(kwargs)

    clone = copy.copy(thunk)
    clone._kwargs = kwargs
    return clone


class TypeThunk(object):
    _kwargs = None

    def __init__(self):
        self._counter = gen_id()

    def __call__(self):
        raise NotImplementedError()


class ContainerTypeMixin(object):
    @property
    def NonNull(self):
        return AttributeTypeThunk(GraphQLNonNull, self)

    @property
    def List(self):
        return AttributeTypeThunk(GraphQLList, self)


class IdentityTypeThunk(TypeThunk, ContainerTypeMixin):
    def __init__(self, item):
        super(IdentityTypeThunk, self).__init__()
        self.item = item

    def __call__(self, **kwargs):
        if kwargs:
            return clone_with_kwargs(self, kwargs)

        return self.item


class ResolveThunkMixin(object):
    _kwargs = None

    def __init__(self, getter, item):
        self.getter = getter
        self.item = item

    def _resolve(self, item):
        if callable(item) and not hasattr(item, 'T'):
            return self._resolve(item())

        return maybe_callable(self.getter(item))

    def __call__(self, **kwargs):
        if kwargs:
            return clone_with_kwargs(self, kwargs)

        return self._resolve(self.item)


class ResolveThunk(ResolveThunkMixin, TypeThunk):
    pass


class AttributeTypeThunk(ResolveThunkMixin, ContainerTypeMixin, TypeThunk):
    def __init__(self, getter, item):
        ResolveThunkMixin.__init__(self, getter, item)
        ContainerTypeMixin.__init__(self)
        TypeThunk.__init__(self)

        if isinstance(item, TypeThunk):
            self._kwargs = item._kwargs

    def __repr__(self):
        return '<AttributeTypeThunk {}>'.format(self.item)


class RootTypeThunk(AttributeTypeThunk):
    def __init__(self, registry, getter, item):
        AttributeTypeThunk.__init__(self, getter, item)
        self.registry = registry

    def __call__(self, **kwargs):
        if kwargs:
            return clone_with_kwargs(self, kwargs)

        return self._resolve(self.item)

    # noinspection PyPep8Naming
    def CanBe(self, klass):
        self.registry._register_possible_type_for(self.item, klass)
        return klass


class ThunkList(object):
    def __init__(self, items):
        self.items = items

    def __call__(self):
        return [maybe_callable(item) for item in self.items]


class TransformThunkList(object):
    def __init__(self, items, transform):
        self.items = items
        self.transform = transform

    def __call__(self):
        return [self.transform(item) for item in maybe_callable(self.items)]
