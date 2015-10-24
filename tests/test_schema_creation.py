from graphql.core import graphql

from epoxy.registry import TypeRegistry

R = TypeRegistry()


class Dog(R.ObjectType):
    name = R.String

    @staticmethod
    def resolve_name(obj, args, info):
        return 'Yes, this is dog.'


class Character(R.ObjectType):
    id = R.ID
    name = R.String
    friends = R.Character.List


def test_schema_creation_using_r_attr():
    schema = R.Schema(R.Dog)
    result = graphql(schema, '{ name }')
    assert not result.errors
    assert result.data == {'name': 'Yes, this is dog.'}


def test_schema_creation_using_string():
    schema = R.Schema('Dog')
    result = graphql(schema, '{ name }')
    assert not result.errors
    assert result.data == {'name': 'Yes, this is dog.'}


def test_schema_creation_using_r_item():
    schema = R.Schema(R['Dog'])
    result = graphql(schema, '{ name }')
    assert not result.errors
    assert result.data == {'name': 'Yes, this is dog.'}


def test_schema_creation_using_r_item_r_attr():
    schema = R.Schema(R[R.Dog])
    result = graphql(schema, '{ name }')
    assert not result.errors
    assert result.data == {'name': 'Yes, this is dog.'}


def test_schema_creation_using_object_type_class():
    schema = R.Schema(Dog)
    result = graphql(schema, '{ name }')
    assert not result.errors
    assert result.data == {'name': 'Yes, this is dog.'}
