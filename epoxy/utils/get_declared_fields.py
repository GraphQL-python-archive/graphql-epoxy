import copy

from ..types import Field
from .first_of import first_of
from .maybe_callable import maybe_callable
from .maybe_t import maybe_t
from .thunk import TypeThunk
from .to_camel_case import to_camel_case


def get_declared_fields(type_name, attrs, field_class=Field):
    fields = []

    for field_attr_name, obj in list(attrs.items()):
        if isinstance(obj, field_class):
            field = copy.copy(obj)
            field.name = first_of(field.name, to_camel_case(field_attr_name))
            # Bind field.type to the maybe scope.
            field.type = (lambda field_type: lambda: maybe_t(maybe_callable(field_type)))(field.type)
            fields.append((field_attr_name, field))

        elif isinstance(obj, TypeThunk):
            counter = obj._counter

            field = field_class(obj, name=to_camel_case(field_attr_name), _counter=counter, **(obj._kwargs or {}))
            fields.append((field_attr_name, field))

    fields.sort(key=lambda f: f[1]._counter)

    seen_field_names = set()
    for field_attr_name, field in fields:
        assert field.name not in seen_field_names, 'Duplicate field definition for name "{}" in type "{}.{}".'.format(
            field.name, type_name, field_attr_name
        )
        seen_field_names.add(field.name)

    return fields
