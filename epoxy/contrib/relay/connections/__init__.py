from graphql.core.type import GraphQLArgument, GraphQLInt, GraphQLString

__author__ = 'jake'

connection_args = {
    'before': GraphQLArgument(GraphQLString),
    'after': GraphQLArgument(GraphQLString),
    'first': GraphQLArgument(GraphQLInt),
    'last': GraphQLArgument(GraphQLInt),
}
