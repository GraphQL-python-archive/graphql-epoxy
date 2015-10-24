from collections import defaultdict
from enum import Enum
from functools import partial
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
from graphql.core.type.definition import GraphQLType, get_named_type
import six

from .bases.class_type_creator import ClassTypeCreator
from .bases.object_type import ObjectTypeBase
from .field import Field
from .metaclasses.interface import InterfaceMeta
from .metaclasses.object_type import ObjectTypeMeta
from .metaclasses.union import UnionMeta
from .thunk import AttributeTypeThunk, RootTypeThunk, ThunkList, TransformThunkList
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
        self._interface_declared_fields = {}
        self._registered_types_can_be = defaultdict(set)
        self.ObjectType = self._create_object_type_class()
        self.Implements = ClassTypeCreator(self, self._create_object_type_class)
        self.Union = ClassTypeCreator(self, self._create_union_type_class)
        self.Interface = self._create_interface_type_class()

        for type in builtin_scalars:
            self.Register(type)

    @method_dispatch
    def Register(self, t):
        # Can't use dispatch, as it's not an instance, but a subclass of.
        if issubclass(t, Enum):
            self.Register(enum_to_graphql_enum(t))
            return t

        raise NotImplementedError('Unable to register {}.'.format(t))

    @Register.register(GraphQLObjectType)
    @Register.register(GraphQLUnionType)
    @Register.register(GraphQLEnumType)
    @Register.register(GraphQLInterfaceType)
    @Register.register(GraphQLInputObjectType)
    @Register.register(GraphQLScalarType)
    def register_(self, t):
        assert not t.name.startswith('_'), \
            'Registered type name cannot start with an "_".'
        assert t.name not in ('ObjectType', 'Implements', 'Interface', 'Schema', 'Register'), \
            'You cannot register a type named "{}".'.format(type.name)
        assert t.name not in self._registered_types, \
            'There is already a registered type named "{}".'.format(type.name)

        self._registered_types[t.name] = t
        return t

    def _resolve_type(self, item):
        if item is None:
            return None

        if not isinstance(item, str):
            item = maybe_t(item)
            assert isinstance(item, GraphQLType), \
                'Attempted to resolve an item {} that is not a GraphQLType'.format(item)

            return item

        value = self._registered_types.get(item)
        assert value, "Type {} was requested, but was not registered.".format(item)
        return value

    def __getattr__(self, item):
        return RootTypeThunk(self, self._resolve_type, item)

    def __getitem__(self, item):
        if isinstance(item, tuple):
            return ThunkList([AttributeTypeThunk(self._resolve_type, i) for i in item])

        return RootTypeThunk(self, self._resolve_type, item)

    def __call__(self, t):
        return self.Register(t)

    def _create_object_type_class(self, interface_thunk=None):
        registry = self

        class RegistryObjectTypeMeta(ObjectTypeMeta):
            @staticmethod
            def _register(object_type, type_class):
                registry.Register(object_type)
                registry._registered_types_can_be[object_type].add(type_class)

            @staticmethod
            def _get_registry():
                return registry

            @staticmethod
            def _get_interfaces():
                if interface_thunk is not None:
                    return TransformThunkList(interface_thunk, get_named_type)

                return None

        @six.add_metaclass(RegistryObjectTypeMeta)
        class ObjectType(ObjectTypeBase):
            abstract = True

        return ObjectType

    def _create_interface_type_class(self):
        registry = self

        class RegistryInterfaceMeta(InterfaceMeta):
            @staticmethod
            def _register(interface, declared_fields):
                registry.Register(interface)
                registry._add_interface_declared_fields(interface, declared_fields)

            @staticmethod
            def _get_registry():
                return registry

        class Interface(six.with_metaclass(RegistryInterfaceMeta)):
            abstract = True

        return Interface

    def _create_union_type_class(self, types_thunk):
        registry = self

        class RegistryUnionMeta(UnionMeta):
            @staticmethod
            def _register(union):
                registry.Register(union)

            @staticmethod
            def _get_registry():
                return registry

        class Union(six.with_metaclass(RegistryUnionMeta)):
            abstract = True

            @staticmethod
            def _get_types():
                return TransformThunkList(types_thunk, get_named_type)

        return Union

    def _create_is_type_of(self, type):
        return partial(self._is_type_of, type)

    def _is_type_of(self, type, obj, info):
        return obj.__class__ in self._registered_types_can_be[type]

    def _add_interface_declared_fields(self, interface, attrs):
        self._interface_declared_fields[interface] = attrs

    def _get_interface_declared_fields(self, interface):
        return self._interface_declared_fields.get(interface, {})

    def _add_impl_to_interfaces(self):
        for type in self._registered_types.values():
            if not isinstance(type, GraphQLObjectType):
                continue

            if type in self._added_impl_types:
                continue

            self._added_impl_types.add(type)
            for interface in type.get_interfaces():
                if type in interface._impls:
                    continue

                interface._impls.append(type)

    def Schema(self, query, mutation=None):
        query = self[query]()
        mutation = self[mutation]()
        self._add_impl_to_interfaces()
        return GraphQLSchema(query=query, mutation=mutation)

    def type(self, name):
        return self[name]()

    def types(self, *names):
        return self[names]

    def with_resolved_types(self, callable):
        assert isinstance(callable, callable)


__all__ = ['TypeRegistry']
