from collections import OrderedDict

from graphql.core.type import GraphQLField, GraphQLInputObjectField

from .argument import Argument
from .thunk import TypeThunk
from .utils.gen_id import gen_id
from .utils.to_camel_case import to_camel_case


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
        return GraphQLField(registry[self.type](), args=self.get_arguments(registry), resolver=resolver)

    def get_arguments(self, registry):
        if not self.args:
            return None

        arguments = []

        for k, argument in self.args.items():
            if isinstance(argument, TypeThunk):
                argument = Argument(argument, _counter=argument._counter, **(argument._kwargs or {}))

            elif not isinstance(argument, Argument):
                raise ValueError('Unknown argument value type %r' % argument)

            arguments.append((
                to_camel_case(k), argument
            ))

        if not isinstance(self.args, OrderedDict):
            arguments.sort(
                key=lambda i: i[1]._counter
            )

        return OrderedDict([(k, v.to_argument(registry)) for k, v in arguments])


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
