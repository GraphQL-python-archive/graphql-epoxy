from ..types.field import Field
from .thunk import TypeThunk


def yank_potential_fields(attrs, bases, field_class=Field):
    field_attrs = {}
    potential_types = (field_class, TypeThunk)

    for klass in reversed(bases):
        for field_attr_name, obj in klass.__dict__.items():
            if field_attr_name == 'T':
                continue

            if isinstance(obj, potential_types):
                field_attrs[field_attr_name] = obj

    for field_attr_name, obj in list(attrs.items()):
        if field_attr_name == 'T':
            continue

        if isinstance(obj, potential_types):
            field_attrs[field_attr_name] = attrs.pop(field_attr_name)

    return field_attrs
