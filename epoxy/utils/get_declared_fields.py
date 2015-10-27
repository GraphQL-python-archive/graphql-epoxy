import copy
from ..field import Field
from ..thunk import TypeThunk
from ..utils.first_of import first_of
from ..utils.maybe_callable import maybe_callable
from ..utils.maybe_t import maybe_t
from ..utils.to_camel_case import to_camel_case


def get_declared_fields(type_name, attrs):
    fields = []

    for field_attr_name, obj in list(attrs.items()):
        if isinstance(obj, Field):
            field = copy.copy(obj)
            field.name = first_of(field.name, to_camel_case(field_attr_name))
            # Bind field.type to the maybe scope.
            field.type = (lambda field_type: lambda: maybe_t(maybe_callable(field_type)))(field.type)
            fields.append((field_attr_name, field))

            continue

        if isinstance(obj, TypeThunk):
            counter = obj._counter

            field = Field(obj, name=to_camel_case(field_attr_name), _counter=counter, **(obj._kwargs or {}))
            fields.append((field_attr_name, field))

    fields.sort(key=lambda f: f[1]._counter)

    seen_field_names = set()
    for field_attr_name, field in fields:
        assert field.name not in seen_field_names, 'Duplicate field definition for name "{}" in type "{}.{}".'.format(
            field.name, type_name, field_attr_name
        )
        seen_field_names.add(field.name)

    return fields
