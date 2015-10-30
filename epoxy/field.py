from graphql.core.type import GraphQLField, GraphQLInputObjectField
from .utils.gen_id import gen_id


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
        return GraphQLField(registry[self.type](), args=self.args, resolver=resolver)


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
