from graphql.core.type import GraphQLScalarType


class ScalarMeta(type):
    def __new__(mcs, name, bases, attrs):
        if attrs.pop('abstract', False):
            return super(ScalarMeta, mcs).__new__(mcs, name, bases, attrs)

        registry = mcs._get_registry()

        cls = super(ScalarMeta, mcs).__new__(mcs, name, bases, attrs)
        cls._registry = registry
        instance = cls()
        serialize = getattr(instance, 'serialize')
        parse_literal = getattr(instance, 'parse_literal')
        parse_value = getattr(instance, 'parse_value')

        mcs._register(GraphQLScalarType(
            name=name,
            description=attrs.get('__doc__', None),
            serialize=serialize,
            parse_value=parse_value,
            parse_literal=parse_literal
        ))

    @staticmethod
    def _register(mutation):
        raise NotImplementedError('_register must be implemented in the sub-metaclass')

    @staticmethod
    def _get_registry():
        raise NotImplementedError('_get_registry must be implemented in the sub-metaclass')
