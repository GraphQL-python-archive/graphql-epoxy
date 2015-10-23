from collections import defaultdict
from enum import Enum

from graphql.core.type import (
    GraphQLBoolean,
    GraphQLEnumType,
    GraphQLFloat,
    GraphQLID,
    GraphQLInputObjectType,
    GraphQLInt,
    GraphQLInterfaceType,
    GraphQLObjectType,
    GraphQLScalarType,
    GraphQLSchema,
    GraphQLString,
    GraphQLUnionType
)
from graphql.core.type.definition import get_named_type
from graphql.core.type.schema import type_map_reducer

import six
from .field import Field
from .metaclasses.interface import InterfaceMeta
from .metaclasses.object_type import ObjectTypeMeta
from .thunk import AttributeTypeThunk, ResolveThunk, RootTypeThunk, ThunkList, TransformThunkList
from .utils.enum_to_graphql_enum import enum_to_graphql_enum
from .utils.maybe_t import maybe_t
from .utils.method_dispatch import method_dispatch

builtin_scalars = [
    GraphQLBoolean,
    GraphQLFloat,
    GraphQLID,
    GraphQLInt,
    GraphQLString
]


class TypeRegistry(object):
    # Fields
    Field = Field

    def __init__(self):
        self._registered_types = {}
        self._added_impl_types = set()
        self._interface_field_attrs = {}
        self._interface_resolvers = defaultdict(dict)
        self.ObjectType = self._create_object_type_class()
        self.Implements = self._create_implement_type_class()
        self.Interface = self._create_interface_type_class()

        for type in builtin_scalars:
            self.register(type)

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
        assert t.name not in ('ObjectType', 'Implements', 'Interface')
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
        return RootTypeThunk(self, self._attr, item)

    def __getitem__(self, item):
        if isinstance(item, tuple):
            return ThunkList([AttributeTypeThunk(self._attr, i) for i in item])

        return RootTypeThunk(self, self._attr, item)

    def __call__(self, t):
        return self.register(t)

    def _create_object_type_class(self, interface_thunk=None):
        registry = self

        class RegistryObjectTypeMeta(ObjectTypeMeta):
            @staticmethod
            def _register(object_type):
                registry.register(object_type)

            @staticmethod
            def _get_registry():
                return registry

            @staticmethod
            def _get_interfaces():
                if interface_thunk is not None:
                    return TransformThunkList(interface_thunk, get_named_type)

                return None

        class ObjectType(six.with_metaclass(RegistryObjectTypeMeta)):
            abstract = True

        return ObjectType

    def _create_implement_type_class(self):
        registry = self

        class Implements(object):
            def __getattr__(self, item):
                return self[item]

            def __getitem__(self, item):
                if isinstance(item, tuple):
                    type_thunk = ThunkList([ResolveThunk(registry._attr, i) for i in item])

                else:
                    type_thunk = ThunkList([ResolveThunk(registry._attr, item)])

                return registry._create_object_type_class(type_thunk)

        implements = Implements()
        return implements

    def _create_interface_type_class(self):
        registry = self

        class RegistryInterfaceMeta(InterfaceMeta):
            @staticmethod
            def _register(interface, attrs):
                registry.register(interface)
                registry._add_interface_attrs(interface, attrs)

            @staticmethod
            def _get_registry():
                return registry

        class Interface(six.with_metaclass(RegistryInterfaceMeta)):
            abstract = True

        return Interface

    def _add_interface_attrs(self, interface, attrs):
        self._interface_field_attrs[interface] = attrs

    def _get_interface_attrs(self, interface):
        return self._interface_field_attrs.get(interface, {})

    def _add_known_interface_resolver(self, interface, field_name, resolver):
        self._interface_resolvers[interface][field_name] = resolver

    def _get_interface_resolvers(self, interface):
        return self._interface_resolvers[interface]

    def _add_impl_to_interfaces(self, *types):
        type_map = {}
        for type in types:
            type_map = type_map_reducer(type_map, type)

        for type in type_map:
            if not isinstance(type, GraphQLObjectType):
                continue

            if type in self._added_impl_types:
                continue

            self._added_impl_types.add(type)
            for interface in type.get_interfaces():
                if type in interface._impls:
                    continue

                interface._impls.append(type)

    def schema(self, query, mutation=None):
        query = self[query]()
        mutation = self[mutation]()
        self._add_impl_to_interfaces(query, mutation)
        return GraphQLSchema(query=query, mutation=mutation)

    def type(self, name):
        return self[name]()

    def types(self, *names):
        return self[names]

    def with_resolved_types(self, callable):
        assert isinstance(callable, callable)


__all__ = ['TypeRegistry']
