from graphql.core.type import GraphQLArgument
from .utils.gen_id import gen_id


class Argument(object):
    def __init__(self, type, description=None, default_value=None, name=None, _counter=None):
        self.name = name
        self.type = type
        self.description = description
        self.default_value = default_value
        self._counter = _counter or gen_id()

    def to_argument(self, registry):
        return GraphQLArgument(registry[self.type](), self.default_value, self.description)
