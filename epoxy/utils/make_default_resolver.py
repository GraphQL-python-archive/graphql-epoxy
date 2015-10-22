def make_default_resolver(field_attr_name):
    def resolver(source, args, info):
        property = getattr(source, field_attr_name, None)
        if callable(property):
            return property()

        return property

    resolver.__name__ = 'resolve_{}'.format(field_attr_name)
    return resolver
