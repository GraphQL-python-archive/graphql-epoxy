from collections import OrderedDict
from functools import partial

from graphql.core.type.definition import GraphQLInputObjectType

from ..types.field import InputField
from ..utils.get_declared_fields import get_declared_fields
from ..utils.weak_ref_holder import WeakRefHolder
from ..utils.yank_potential_fields import yank_potential_fields


class InputTypeMeta(type):
    def __new__(mcs, name, bases, attrs):
        if attrs.pop('abstract', False):
            return super(InputTypeMeta, mcs).__new__(mcs, name, bases, attrs)

        name = attrs.pop('_name', name)
        class_ref = WeakRefHolder()
        declared_fields = get_declared_fields(name, yank_potential_fields(attrs, bases, InputField), InputField)
        interface = GraphQLInputObjectType(
            name,
            fields=partial(mcs._build_field_map, class_ref, declared_fields),
            description=attrs.get('__doc__'),
        )

        mcs._register(interface)
        cls = super(InputTypeMeta, mcs).__new__(mcs, name, bases, attrs)
        cls.T = interface
        cls._registry = mcs._get_registry()
        class_ref.set(cls)

        return cls

    @staticmethod
    def _register(object_type):
        raise NotImplementedError('_register must be implemented in the sub-metaclass')

    @staticmethod
    def _get_registry():
        raise NotImplementedError('_get_registry must be implemented in the sub-metaclass')

    @staticmethod
    def _build_field_map(class_ref, fields):
        cls = class_ref.get()
        if not cls:
            return

        registry = cls._registry
        field_map = OrderedDict()
        field_attr_map = OrderedDict()

        for field_attr_name, field in fields:
            graphql_field = field_map[field.name] = field.to_field(registry)

            if field_attr_name in field_attr_map:
                del field_attr_map[field_attr_name]

            field_attr_map[field_attr_name] = (field.name, graphql_field)

        cls._field_attr_map = field_attr_map
        return field_map
