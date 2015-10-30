from graphql.core.type import GraphQLField, GraphQLNonNull
from graphql.core.type.definition import GraphQLArgument


class MutationMeta(type):
    def __new__(mcs, name, bases, attrs):
        if attrs.pop('abstract', False):
            return super(MutationMeta, mcs).__new__(mcs, name, bases, attrs)

        registry = mcs._get_registry()

        input = attrs.pop('Input')
        output = attrs.pop('Output')

        assert input and not hasattr(input, 'T'), 'A mutation must define a class named "Input" inside of it that ' \
                                                  'does not subclass an R.InputType'
        assert output and not hasattr(output, 'T'), 'A mutation must define a class named "Output" inside of it that ' \
                                                    'does not subclass an R.ObjectType'

        Input = type(name + 'Input', (registry.InputType,), dict(vars(input)))
        Output = type(name + 'Payload', (registry.ObjectType,), dict(vars(output)))
        attrs['Input'] = Input
        attrs['Output'] = Output

        cls = super(MutationMeta, mcs).__new__(mcs, name, bases, attrs)
        cls._registry = registry
        instance = cls()
        resolver = getattr(instance, 'execute')
        assert resolver and callable(resolver), 'A mutation must define a function named "execute" that will execute ' \
                                                'the mutation.'

        mutation_name = name[0].lower() + name[1:]

        mcs._register(mutation_name, registry.with_resolved_types(lambda R: GraphQLField(
            type=R[Output],
            args={
                'input': GraphQLArgument(GraphQLNonNull(R[Input]))
            },
            resolver=lambda obj, args, info: resolver(obj, Input(args.get('input')), info)
        )))

    @staticmethod
    def _register(mutation_name, mutation):
        raise NotImplementedError('_register must be implemented in the sub-metaclass')

    @staticmethod
    def _get_registry():
        raise NotImplementedError('_get_registry must be implemented in the sub-metaclass')
