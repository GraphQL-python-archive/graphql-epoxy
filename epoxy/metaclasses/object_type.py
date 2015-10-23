from collections import OrderedDict
from graphql.core.type import GraphQLObjectType
from ..utils.get_declared_fields import get_declared_fields
from ..utils.make_default_resolver import make_default_resolver
from ..utils.no_implementation_registration import no_implementation_registration
from ..utils.yank_potential_fields import yank_potential_fields


class ObjectTypeMeta(type):
    def __new__(mcs, name, bases, attrs):
        if attrs.get('abstract'):
            return super(ObjectTypeMeta, mcs).__new__(mcs, name, bases, attrs)

        potential_fields = yank_potential_fields(attrs)
        with no_implementation_registration():
            object_type = GraphQLObjectType(
                name,
                fields=lambda: mcs._build_field_map(attrs, potential_fields),
                description=attrs.get('__doc__'),
                interfaces=mcs._get_interfaces()
            )

        mcs._register(object_type)
        attrs['_registry'] = mcs._get_registry()
        attrs['T'] = object_type
        cls = super(ObjectTypeMeta, mcs).__new__(mcs, name, bases, attrs)
        attrs['_cls'] = cls
        return cls

    @staticmethod
    def _register(object_type):
        raise NotImplementedError('_register must be implemented in the sub-metaclass')

    @staticmethod
    def _get_registry():
        raise NotImplementedError('_get_registry must be implemented in the sub-metaclass')

    @staticmethod
    def _build_field_map(attrs, potential_fields):
        instance = attrs['_cls']()
        type = attrs['T']
        registry = attrs['_registry']
        interfaces = type.get_interfaces()
        fields = []

        for interface in interfaces:
            resolve_fn_getter = registry._get_interface_resolvers(interface).get
            fields += get_declared_fields(registry._get_interface_attrs(interface), resolve_fn_getter)

        fields += get_declared_fields(potential_fields)
        field_map = OrderedDict()

        for field_attr_name, field in fields:
            resolve_fn = (
                field.resolver or
                getattr(instance, 'resolve_{}'.format(field_attr_name), None) or
                field._interface_resolver or
                make_default_resolver(field_attr_name)
            )

            field_map[field.name] = field.to_field(resolve_fn)

        return field_map

    @staticmethod
    def _get_interfaces():
        return None
