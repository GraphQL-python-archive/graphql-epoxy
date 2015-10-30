from graphql.core.type import GraphQLField, GraphQLObjectType
from graphql.core.type import GraphQLString
from epoxy import TypeRegistry
from pytest import raises


def test_reserved_names():
    R = TypeRegistry()

    for name in R._reserved_names:
        type = GraphQLObjectType(
            name=name,
            fields={'a': GraphQLField(GraphQLString)}
        )
        with raises(AssertionError) as excinfo:
            R(type)

        assert str(excinfo.value) == 'You cannot register a type named "{}".'.format(name)
