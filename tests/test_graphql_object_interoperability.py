from collections import namedtuple
from graphql.core import graphql
from graphql.core.type import GraphQLObjectType, GraphQLField, GraphQLString
from epoxy.registry import TypeRegistry


def test_resolves_regular_graphql_type():
    BuiltInType = GraphQLObjectType(
        name='BuiltInType',
        fields={
            'someString': GraphQLField(GraphQLString)
        }
    )

    BuiltInTypeTuple = namedtuple('BuiltInTypeData', 'someString')

    R = TypeRegistry()

    class Query(R.ObjectType):
        built_in_type = R.Field(BuiltInType)

        def resolve_built_in_type(self, obj, args, info):
            return BuiltInTypeTuple('Hello World. I am a string.')

    R(BuiltInType)

    schema = R.Schema(R.Query)
    result = graphql(schema, '{ builtInType { someString } }')
    assert not result.errors
    assert result.data == {'builtInType': {'someString': 'Hello World. I am a string.'}}