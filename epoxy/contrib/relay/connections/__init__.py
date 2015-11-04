from graphql.core.type import GraphQLInt, GraphQLString

from ....argument import Argument

__author__ = 'jake'

connection_args = {
    'before': Argument(GraphQLString),
    'after': Argument(GraphQLString),
    'first': Argument(GraphQLInt),
    'last': Argument(GraphQLInt),
}
