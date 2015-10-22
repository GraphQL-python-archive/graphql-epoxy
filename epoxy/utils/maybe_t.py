from graphql.core.type.definition import GraphQLType


def maybe_t(obj):
    if isinstance(getattr(obj, 'T', None), GraphQLType):
        return obj.T

    return obj
