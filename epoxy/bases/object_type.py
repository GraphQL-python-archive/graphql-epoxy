class ObjectTypeBase(object):
    T = None
    _field_attr_map = None

    def __init__(self, **kwargs):
        field_map_init = kwargs.pop('__field_map_init', False)
        if field_map_init:
            return

        if self._field_attr_map is None:
            raise RuntimeError("You cannot construct type {} until it is used in a created Schema.".format(
                self.T
            ))

        # Todo: Maybe some type checking? Probably not tho.
        for field_name in self._field_attr_map.keys():
            if field_name in kwargs:
                setattr(self, field_name, kwargs.pop(field_name))

            else:
                setattr(self, field_name, None)

        if kwargs:
            raise TypeError('Type {} received unexpected keyword argument(s): {}.'.format(
                self.T,
                ', '.join(kwargs.keys())
            ))

    def __repr__(self):
        if self._field_attr_map is None:
            return '<{}>'.format(self.T)

        return '<{} {}>'.format(
            self.T,
            ' '.join('{}={!r}'.format(field_name, getattr(self, field_name))
                     for field_name in self._field_attr_map.keys())
        )
