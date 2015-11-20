from graphql.core.type.definition import GraphQLObjectType, GraphQLField
from graphql.core.type.scalars import GraphQLString
from pytest import raises

from epoxy import TypeRegistry


def test_will_disallow_duplicate_type_names_from_being_registered():
    type = GraphQLObjectType(name='Query', fields={
        'a': GraphQLField(GraphQLString)
    })

    type_duplicated = GraphQLObjectType(name='Query', fields={
        'a': GraphQLField(GraphQLString)
    })

    R = TypeRegistry()
    R(type)

    with raises(AssertionError) as excinfo:
        R(type_duplicated)

    assert str(excinfo.value) == 'There is already a registered type named "Query".'


def test_will_allow_the_same_type_to_be_registered_more_than_once():
    type = GraphQLObjectType(name='Query', fields={
        'a': GraphQLField(GraphQLString)
    })

    R = TypeRegistry()
    assert R(type)
    assert R(type)


def test_cannot_register_type_starting_with_an_underscore():
    type = GraphQLObjectType(name='_Query', fields={
        'a': GraphQLField(GraphQLString)
    })

    R = TypeRegistry()

    with raises(AssertionError) as excinfo:
        R(type)

    assert str(excinfo.value) == 'Registered type name cannot start with an "_".'


def test_cannot_register_type_thats_using_reserved_name():
    R = TypeRegistry()
    for name in TypeRegistry._reserved_names:
        type = GraphQLObjectType(name=name, fields={
            'a': GraphQLField(GraphQLString)
        })
        with raises(AssertionError) as excinfo:
            R(type)

        assert str(excinfo.value) == 'You cannot register a type named "{}".'.format(name)
