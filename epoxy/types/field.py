from collections import OrderedDict
from graphql.core.type import GraphQLField, GraphQLInputObjectField
from ..types.argument import Argument
from ..utils.gen_id import gen_id
from ..utils.thunk import TypeThunk
from ..utils.to_camel_case import to_camel_case
from ..utils.wrap_resolver_translating_arguments import wrap_resolver_translating_arguments


class Field(object):
    def __init__(self, type, description=None, args=None, name=None, resolver=None, _counter=None,
                 _interface_resolver=None):
        self.name = name
        self.type = type
        self.description = description
        self.args = args
        self.resolver = resolver
        self._interface_resolver = _interface_resolver
        self._counter = _counter or gen_id()

    def to_field(self, registry, resolver):
        args, arguments_to_original_case = self.get_arguments(registry)

        if arguments_to_original_case:
            resolver = wrap_resolver_translating_arguments(resolver, arguments_to_original_case)

        return GraphQLField(registry[self.type](), args=args, resolver=resolver)

    def get_arguments(self, registry):
        if not self.args:
            return None, None

        arguments = []
        arguments_to_original_case = {}

        for k, argument in self.args.items():
            if isinstance(argument, TypeThunk):
                argument = Argument(argument, _counter=argument._counter, **(argument._kwargs or {}))

            elif not isinstance(argument, Argument):
                raise ValueError('Unknown argument value type %r' % argument)

            camel_cased_name = to_camel_case(k)
            if camel_cased_name in arguments_to_original_case:
                raise ValueError(
                    'Argument %s already exists as %s' %
                    (k, arguments_to_original_case[camel_cased_name])
                )

            arguments_to_original_case[camel_cased_name] = k
            arguments.append((
                camel_cased_name, argument
            ))

        if not isinstance(self.args, OrderedDict):
            arguments.sort(
                key=lambda i: i[1]._counter
            )

        # Remove things that wouldn't perform any meaningful translation.
        for k, v in list(arguments_to_original_case.items()):
            if k == v:
                del arguments_to_original_case[k]

        return OrderedDict([(k, v.to_argument(registry)) for k, v in arguments]), arguments_to_original_case


class InputField(object):
    def __init__(self, type, description=None, default_value=None, name=None, _counter=None):
        self.name = name
        self.type = type
        self.description = description
        self.default_value = default_value
        self._counter = _counter or gen_id()

    def to_field(self, registry):
        return GraphQLInputObjectField(registry[self.type](), default_value=self.default_value,
                                       description=self.description)
