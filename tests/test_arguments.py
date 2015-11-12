from collections import OrderedDict
from pytest import raises
from graphql.core import graphql
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


def test_resolved_args_will_be_translated_to_original_casing():
    R = TypeRegistry()

    class Query(R.ObjectType):
        argument_keys = R.String.List(args={
            'foo': R.String,
            'foo_bar': R.String
        })

        def resolve_argument_keys(self, obj, args, info):
            return list(sorted(args.keys()))

    Schema = R.Schema(R.Query)
    result = graphql(Schema, '''
    {
        argumentKeys(foo: "Hello", fooBar: "World")
    }
    ''')

    assert not result.errors

    assert result.data == {
        'argumentKeys': ['foo', 'foo_bar']
    }


def test_will_recognize_casing_conversion_conflicts():
    R = TypeRegistry()

    class Query(R.ObjectType):
        argument_keys = R.String.List(args={
            'foo_bar': R.String,
            'fooBar': R.String
        })

        def resolve_argument_keys(self, obj, args, info):
            return list(sorted(args.keys()))

    with raises(ValueError) as excinfo:
        Schema = R.Schema(R.Query)

    assert str(excinfo.value) in (
        'Argument foo_bar already exists as fooBar',
        'Argument fooBar already exists as foo_bar',
    )
