from enum import Enum
from graphql.core.type import (
    GraphQLBoolean,
    GraphQLEnumType,
    GraphQLFloat,
    GraphQLID,
    GraphQLInputObjectType,
    GraphQLInt,
    GraphQLInterfaceType,
    GraphQLList,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLScalarType,
    GraphQLSchema,
    GraphQLString,
    GraphQLUnionType
)

import six
from .field import Field
from .metaclasses.object_type import ObjectTypeMeta
from .thunk import AttributeTypeThunk, IdentityTypeThunk, ThunkList
from .utils.enum_to_graphql_enum import enum_to_graphql_enum
from .utils.maybe_t import maybe_t
from .utils.method_dispatch import method_dispatch


class TypeRegistry(object):
    # Built-in Scalars
    Boolean = IdentityTypeThunk(GraphQLBoolean)
    Float = IdentityTypeThunk(GraphQLFloat)
    ID = IdentityTypeThunk(GraphQLID)
    Int = IdentityTypeThunk(GraphQLInt)
    String = IdentityTypeThunk(GraphQLString)

    # Type Containers
    NonNull = IdentityTypeThunk(GraphQLNonNull)
    List = IdentityTypeThunk(GraphQLList)

    # Fields
    Field = Field

    def __init__(self):
        self._registered_types = {}
        self.ObjectType = self._create_object_type_class()

    @method_dispatch
    def register(self, t):
        # Can't use dispatch, as it's not an instance, but a subclass of.
        if issubclass(t, Enum):
            return self.register(enum_to_graphql_enum(t))

        raise NotImplementedError('Unable to register {}.'.format(t))

    @register.register(GraphQLObjectType)
    @register.register(GraphQLUnionType)
    @register.register(GraphQLEnumType)
    @register.register(GraphQLInterfaceType)
    @register.register(GraphQLInputObjectType)
    @register.register(GraphQLScalarType)
    def register_(self, t):
        assert t.name not in self._registered_types
        self._registered_types[t.name] = t
        return t

    def _attr(self, item):
        if not isinstance(item, str):
            return maybe_t(item)

        value = self._registered_types.get(item)

        assert value, "Item {} does not exist".format(item)
        return value

    def __getattr__(self, item):
        return AttributeTypeThunk(self._attr, item)

    def __getitem__(self, item):
        if isinstance(item, tuple):
            return ThunkList([AttributeTypeThunk(self._attr, i) for i in item])

        return AttributeTypeThunk(self._attr, item)

    def __call__(self, t):
        return self.register(t)

    def _create_object_type_class(self):
        registry = self

        class RegistryObjectTypeMeta(ObjectTypeMeta):
            @staticmethod
            def _register(object_type):
                registry.register(object_type)

        class ObjectType(six.with_metaclass(RegistryObjectTypeMeta)):
            pass

        return ObjectType

    def schema(self, query, mutation=None):
        return GraphQLSchema(query=self[query](), mutation=self[mutation]())

    def type(self, name):
        return self[name]()

    def types(self, *names):
        return self[names]

    def with_resolved_types(self, callable):
        assert isinstance(callable, callable)


__all__ = ['TypeRegistry']
