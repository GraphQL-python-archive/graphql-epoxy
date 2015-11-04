from collections import OrderedDict

from graphql.core.type import GraphQLString, GraphQLInt, GraphQLID, GraphQLNonNull

from epoxy.registry import TypeRegistry
from epoxy.types.argument import Argument

make_args = lambda R: {
    'a': R.Int,
    'b_cool': R.String,
    'c': R.ID.NonNull,
    'd': Argument(R.String, default_value="hello world"),
    'z': R.String(default_value="hello again", description="This is a description"),
    'x': R.Int(default_value=7),
    'y': Argument(GraphQLString),
    'q': R.TestInputType,
    'w': Argument(R.TestInputType)
}

make_ordered_dict_args = lambda R: OrderedDict([
    ('a', R.Int),
    ('b_cool', R.String),
    ('c', R.ID.NonNull),
    ('d', Argument(R.String, default_value="hello world")),
    ('z', R.String(default_value="hello again", description="This is a description")),
    ('x', R.Int(default_value=7)),
    ('y', Argument(GraphQLString)),
    ('q', R.TestInputType),
    ('w', Argument(R.TestInputType)),
])


def check_args(test_input_type, args):
    expected_keys = ['a', 'bCool', 'c', 'd', 'z', 'x', 'y', 'q', 'w']
    keys = [a.name for a in args]

    assert keys == expected_keys

    a, b, c, d, z, x, y, q, w = args

    assert a.type is GraphQLInt
    assert b.type is GraphQLString
    assert isinstance(c.type, GraphQLNonNull)
    assert c.type.of_type is GraphQLID
    assert d.type is GraphQLString
    assert d.default_value == "hello world"
    assert z.type is GraphQLString
    assert z.default_value == "hello again"
    assert z.description == "This is a description"
    assert x.type is GraphQLInt
    assert x.default_value == 7
    assert y.type is GraphQLString
    assert q.type is test_input_type
    assert w.type is test_input_type


def test_args_will_magically_order():
    R = TypeRegistry()

    class TestInputType(R.InputType):
        a = R.Int
        b = R.Int

    class Query(R.ObjectType):
        int = R.Int(
            args=make_args(R)
        )
        int_from_field = R.Field(R.Int, args=make_args(R))

    query_type = R.Query()
    check_args(TestInputType.T, query_type.get_fields()['int'].args)
    check_args(TestInputType.T, query_type.get_fields()['intFromField'].args)


def test_args_can_also_use_ordered_dict():
    R = TypeRegistry()

    class TestInputType(R.InputType):
        a = R.Int
        b = R.Int

    class Query(R.ObjectType):
        int = R.Int(
            args=make_ordered_dict_args(R)
        )
        int_from_field = R.Field(R.Int, args=make_ordered_dict_args(R))

    query_type = R.Query()
    check_args(TestInputType.T, query_type.get_fields()['int'].args)
    check_args(TestInputType.T, query_type.get_fields()['intFromField'].args)
