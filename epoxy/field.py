from graphql.core.type import GraphQLField


class Field(object):
    _creation_counter = 0

    def __init__(self, type, description=None, args=None, name=None, resolver=None):
        self.name = name
        self.type = type
        self.description = description
        self.args = args
        self.resolver = resolver
        self._counter = Field._creation_counter
        Field._creation_counter += 1

    def to_field(self, resolver):
        return GraphQLField(self.type, self.args, resolver)
