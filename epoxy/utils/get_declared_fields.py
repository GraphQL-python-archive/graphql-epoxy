import copy
from graphql.core.type.definition import GraphQLType
from ..field import Field
from ..thunk import TypeThunk
from ..utils.first_of import first_of
from ..utils.maybe_callable import maybe_callable
from ..utils.maybe_t import maybe_t
from ..utils.to_camel_case import to_camel_case


def get_declared_fields(attrs, resolve_fn_getter=None):
    fields = []

    for field_attr_name, obj in list(attrs.items()):
        if isinstance(obj, Field):
            field = copy.copy(obj)

            if resolve_fn_getter:
                field._interface_resolver = resolve_fn_getter(field_attr_name)

            field.name = first_of(field.name, to_camel_case(field_attr_name))
            field.type = maybe_t(maybe_callable(field.type))
            fields.append((field_attr_name, field))

            continue

        if isinstance(obj, TypeThunk):
            counter = obj._counter
            obj = obj()

            if isinstance(obj, GraphQLType):
                if resolve_fn_getter:
                    interface_resolver = resolve_fn_getter(field_attr_name)
                else:
                    interface_resolver = None

                field = Field(obj, name=to_camel_case(field_attr_name), _counter=counter,
                              _interface_resolver=interface_resolver)

                fields.append((field_attr_name, field))

    fields.sort(key=lambda f: f[1]._counter)
    return fields
