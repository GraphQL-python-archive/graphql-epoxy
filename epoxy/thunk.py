from graphql.core.type.definition import GraphQLList, GraphQLNonNull
from epoxy.utils.gen_id import gen_id
from epoxy.utils.maybe_callable import maybe_callable


class TypeThunk(object):
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

    def __call__(self):
        return self.item


class ResolveThunkMixin(object):
    def __init__(self, getter, item):
        self.getter = getter
        self.item = item

    def _resolve(self, item):
        if callable(item) and not hasattr(item, 'T'):
            return self._resolve(item())

        return maybe_callable(self.getter(item))

    def __call__(self):
        return self._resolve(self.item)


class ResolveThunk(ResolveThunkMixin, TypeThunk):
    pass


class AttributeTypeThunk(ResolveThunkMixin, ContainerTypeMixin, TypeThunk):
    def __init__(self, getter, item):
        ResolveThunkMixin.__init__(self, getter, item)
        ContainerTypeMixin.__init__(self)
        TypeThunk.__init__(self)

    def __repr__(self):
        return '<AttributeTypeThunk {}>'.format(self.item)


class RootTypeThunk(AttributeTypeThunk):
    def __init__(self, registry, getter, item):
        AttributeTypeThunk.__init__(self, getter, item)
        self.registry = registry

    def __call__(self):
        return self._resolve(self.item)

    # noinspection PyPep8Naming
    def CanBe(self, klass):
        raise NotImplementedError('CanBe not yet implemented.')


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
