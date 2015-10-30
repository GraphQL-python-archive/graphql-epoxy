class InputTypeBase(object):
    T = None
    _field_attr_map = None

    def __init__(self, arg_value=None):
        if arg_value is None:
            return

        if self._field_attr_map is None:
            raise RuntimeError("You cannot construct type {} until it is used in a created Schema.".format(
                self.T
            ))

        for attr_name, (field_name, field) in self._field_attr_map.items():
            if field_name in arg_value:
                setattr(self, attr_name, arg_value[field_name])

            else:
                setattr(self, attr_name, field.default_value)

    def __repr__(self):
        if self._field_attr_map is None:
            return '<{}>'.format(self.T)

        return '<{} {}>'.format(
            self.T,
            ' '.join('{}={!r}'.format(field_name, getattr(self, field_name))
                     for field_name in self._field_attr_map.keys())
        )
