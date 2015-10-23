from collections import OrderedDict
from graphql.core.type.definition import GraphQLInterfaceType
from ..utils.get_declared_fields import get_declared_fields
from ..utils.make_default_resolver import make_default_resolver
from ..utils.yank_potential_fields import yank_potential_fields


class InterfaceMeta(type):
    def __new__(mcs, name, bases, attrs):
        if attrs.get('abstract'):
            return super(InterfaceMeta, mcs).__new__(mcs, name, bases, attrs)

        potential_fields = yank_potential_fields(attrs)
        interface = GraphQLInterfaceType(
            name,
            fields=lambda: mcs._build_field_map(attrs, potential_fields),
            description=attrs.get('__doc__'),
            resolve_type=lambda: None
        )
        mcs._register(interface, potential_fields)
        attrs['_registry'] = mcs._get_registry()
        attrs['T'] = interface
        cls = super(InterfaceMeta, mcs).__new__(mcs, name, bases, attrs)
        attrs['_cls'] = cls
        return cls

    @staticmethod
    def _register(object_type, attrs):
        raise NotImplementedError('_register must be implemented in the sub-metaclass')

    @staticmethod
    def _get_registry():
        raise NotImplementedError('_get_registry must be implemented in the sub-metaclass')

    @staticmethod
    def _build_field_map(attrs, potential_fields):
        instance = attrs['_cls']()
        registry = attrs['_registry']

        fields = get_declared_fields(potential_fields)
        field_map = OrderedDict()

        for field_attr_name, field in fields:
            interface_resolve_fn = (
                field.resolver or
                getattr(instance, 'resolve_{}'.format(field_attr_name), None)
            )

            if interface_resolve_fn:
                registry._add_known_interface_resolver(attrs['T'], field_attr_name, interface_resolve_fn)

            resolve_fn = interface_resolve_fn or make_default_resolver(field_attr_name)

            field_map[field.name] = field.to_field(resolve_fn)

        return field_map
