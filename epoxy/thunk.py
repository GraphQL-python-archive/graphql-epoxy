from graphql.core.type.definition import GraphQLList, GraphQLNonNull
from epoxy.utils.maybe_callable import maybe_callable


class TypeThunk(object):
    __slots__ = ()

    def __call__(self):
        raise NotImplementedError()

    @property
    def NonNull(self):
        return AttributeTypeThunk(GraphQLNonNull, self)

    @property
    def List(self):
        return AttributeTypeThunk(GraphQLList, self)


class IdentityTypeThunk(TypeThunk):
    __slots__ = 'item'

    def __init__(self, item):
        self.item = item

    def __call__(self):
        return self.item


class AttributeTypeThunk(TypeThunk):
    __slots__ = 'getter', 'item'

    def __init__(self, getter, item):
        self.getter = getter
        self.item = item

    def _resolve(self, item):
        if callable(item):
            return self._resolve(item())

        return maybe_callable(self.getter(item))

    def __call__(self):
        return self._resolve(self.item)

    def __repr__(self):
        return '<LazyAttribute {}>'.format(self.item)


class ThunkList(object):
    __slots__ = 'attributes'

    def __init__(self, attributes):
        self.attributes = attributes

    def __call__(self):
        return [maybe_callable(attr) for attr in self.attributes]
