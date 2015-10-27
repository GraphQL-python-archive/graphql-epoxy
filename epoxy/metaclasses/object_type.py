from collections import OrderedDict
from functools import partial
from graphql.core.type import GraphQLObjectType
from ..utils.get_declared_fields import get_declared_fields
from ..utils.make_default_resolver import make_default_resolver
from ..utils.no_implementation_registration import no_implementation_registration
from ..utils.weak_ref_holder import WeakRefHolder
from ..utils.yank_potential_fields import yank_potential_fields


class ObjectTypeMeta(type):
    def __new__(mcs, name, bases, attrs):
        if attrs.pop('abstract', False):
            return super(ObjectTypeMeta, mcs).__new__(mcs, name, bases, attrs)

        name = attrs.pop('_name', name)
        class_ref = WeakRefHolder()
        registry = mcs._get_registry()
        declared_fields = get_declared_fields(name, yank_potential_fields(attrs))

        with no_implementation_registration():
            object_type = GraphQLObjectType(
                name,
                fields=partial(mcs._build_field_map, class_ref, declared_fields),
                description=attrs.get('__doc__'),
                interfaces=mcs._get_interfaces()
            )

            object_type.is_type_of = registry._create_is_type_of(object_type)

        cls = super(ObjectTypeMeta, mcs).__new__(mcs, name, bases, attrs)
        mcs._register(object_type, cls)
        cls._registry = registry
        cls.T = object_type
        class_ref.set(cls)

        return cls

    @staticmethod
    def _register(object_type, cls):
        raise NotImplementedError('_register must be implemented in the sub-metaclass')

    @staticmethod
    def _get_registry():
        raise NotImplementedError('_get_registry must be implemented in the sub-metaclass')

    @staticmethod
    def _build_field_map(class_ref, declared_fields):
        cls = class_ref.get()
        if not cls:
            return

        instance = cls(__field_map_init=True)
        type = cls.T
        registry = cls._registry
        interfaces = type.get_interfaces()
        fields = []

        known_interface_resolvers = {}

        for interface in interfaces:
            interface.get_fields()  # This triggers the interface to resolve the field thunks.
            fields += registry._get_interface_declared_fields(interface)

        for field_attr_name, field in fields:
            if field._interface_resolver and field.name not in known_interface_resolvers:
                known_interface_resolvers[field.name] = field._interface_resolver

        fields += declared_fields
        field_map = OrderedDict()
        field_attr_map = OrderedDict()

        for field_attr_name, field in fields:
            resolve_fn = (
                field.resolver or
                getattr(instance, 'resolve_{}'.format(field_attr_name), None) or
                field._interface_resolver or
                known_interface_resolvers.get(field.name) or
                make_default_resolver(field_attr_name)
            )

            # In the case where field definitions are duplicated, we are going to use the latest definition.
            # We delete, so that when inserted into the OrderedMap again, it will be ordered last, instead
            # of in the position of the previous one.
            if field.name in field_map:
                del field_map[field.name]

            graphql_field = field.to_field(registry, resolve_fn)
            field_map[field.name] = graphql_field

            if field_attr_name in field_attr_map:
                del field_attr_map[field_attr_name]

            field_attr_map[field_attr_name] = graphql_field

        cls._field_attr_map = field_attr_map
        return field_map

    @staticmethod
    def _get_interfaces():
        return None
