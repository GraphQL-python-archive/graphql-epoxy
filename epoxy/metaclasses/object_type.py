from collections import OrderedDict
from graphql.core.type import GraphQLObjectType
from graphql.core.type.definition import GraphQLType
from ..field import Field
from ..thunk import TypeThunk
from ..utils.first_of import first_of
from ..utils.make_default_resolver import make_default_resolver
from ..utils.maybe_callable import maybe_callable
from ..utils.maybe_t import maybe_t
from ..utils.to_camel_case import to_camel_case


class ObjectTypeMeta(type):
    def __new__(mcs, name, bases, attrs):
        object_type = GraphQLObjectType(
            name,
            fields=lambda: mcs._build_field_map(attrs),
            description=attrs.get('__doc__')
        )
        mcs._register(object_type)
        attrs['T'] = object_type
        cls = super(ObjectTypeMeta, mcs).__new__(mcs, name, bases, attrs)
        attrs['_cls'] = cls
        return cls

    @staticmethod
    def _register(object_type):
        raise NotImplementedError('_register must be implemented in the sub-metaclass')

    @staticmethod
    def _get_declared_fields(attrs):
        fields = []

        for field_attr_name, obj in list(attrs.items()):
            if field_attr_name == 'T':
                continue

            if isinstance(obj, Field):
                field = attrs.pop(field_attr_name)
                field.name = first_of(field.name, to_camel_case(field_attr_name))
                field.type = maybe_t(maybe_callable(field.type))
                fields.append((field_attr_name, field))

            if isinstance(obj, TypeThunk):
                obj = obj()

            if isinstance(obj, GraphQLType):
                field = Field(obj, name=to_camel_case(field_attr_name))
                fields.append((field_attr_name, field))

        fields.sort(key=lambda f: f[1]._creation_counter)
        return fields

    @staticmethod
    def _build_field_map(attrs):
        instance = attrs['_cls']()

        fields = ObjectTypeMeta._get_declared_fields(attrs)
        field_map = OrderedDict()

        for field_attr_name, field in fields:
            resolve_fn = (
                field.resolver or
                getattr(instance, 'resolve_{}'.format(field_attr_name), None) or
                make_default_resolver(field_attr_name)
            )

            field_map[field.name] = field.to_field(resolve_fn)

        return field_map
