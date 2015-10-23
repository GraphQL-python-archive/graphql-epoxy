from graphql.core import graphql
from epoxy.registry import TypeRegistry
from pytest import raises

R = TypeRegistry()


class Human(R.ObjectType):
    name = R.String
    favorite_color = R.String


Schema = R.schema(R.Human)


def test_object_type_as_data():
    jake = Human(name='Jake', favorite_color='Red')
    assert jake.name == 'Jake'
    assert jake.favorite_color == 'Red'
    assert repr(jake) == '<Human name={!r} favorite_color={!r}>'.format(jake.name, jake.favorite_color)

    result = graphql(Schema, '{ name favoriteColor }', jake)
    assert not result.errors
    assert result.data == {'name': 'Jake', 'favoriteColor': 'Red'}


def test_object_type_as_data_with_partial_fields_provided():
    jake = Human(name='Jake')
    assert jake.name == 'Jake'
    assert jake.favorite_color is None
    assert repr(jake) == '<Human name={!r} favorite_color={!r}>'.format(jake.name, jake.favorite_color)

    result = graphql(Schema, '{ name favoriteColor }', jake)
    assert not result.errors
    assert result.data == {'name': 'Jake', 'favoriteColor': None}


def test_object_type_giving_unexpected_key():
    with raises(TypeError) as excinfo:
        Human(after_all=True)

    assert str(excinfo.value) == 'Type Human received unexpected keyword argument(s): after_all.'
