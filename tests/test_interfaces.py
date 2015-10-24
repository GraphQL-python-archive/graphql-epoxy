from graphql.core import graphql
from epoxy.registry import TypeRegistry


def test_register_interface():
    R = TypeRegistry()

    class Character(R.Interface):
        id = R.ID
        name = R.String
        friends_with = R.Character.List
        lives_remaining = R.Field(R.Int)

    character = Character.T
    fields = character.get_fields()
    assert list(fields.keys()) == ['id', 'name', 'friendsWith', 'livesRemaining']


def test_register_single_type():
    R = TypeRegistry()

    class Character(R.Interface):
        id = R.ID
        name = R.String
        friends_with = R.Character.List
        lives_remaining = R.Field(R.Int)

    class Human(R.Implements.Character):
        home_planet = R.String

    human = Human.T
    fields = human.get_fields()
    assert list(fields.keys()) == ['id', 'name', 'friendsWith', 'livesRemaining', 'homePlanet']


def test_implements_multiple_interfaces_via_r():
    R = TypeRegistry()

    class Character(R.Interface):
        id = R.ID
        name = R.String
        friends_with = R.Character.List
        lives_remaining = R.Field(R.Int)

    class Bean(R.Interface):
        real = R.Boolean

    class Human(R.Implements[R.Character, R.Bean]):
        home_planet = R.String

    human = Human.T
    fields = human.get_fields()
    assert list(fields.keys()) == ['id', 'name', 'friendsWith', 'livesRemaining', 'real', 'homePlanet']


def test_implements_multiple_interfaces_via_class():
    R = TypeRegistry()

    class Character(R.Interface):
        id = R.ID
        name = R.String
        friends_with = R.Character.List
        lives_remaining = R.Field(R.Int)

    class Bean(R.Interface):
        real = R.Boolean

    class Human(R.Implements[Character, Bean]):
        home_planet = R.String

    human = Human.T
    fields = human.get_fields()
    assert list(fields.keys()) == ['id', 'name', 'friendsWith', 'livesRemaining', 'real', 'homePlanet']


def test_implements_multiple_interfaces_via_string():
    R = TypeRegistry()

    class Character(R.Interface):
        id = R.ID
        name = R.String
        friends_with = R.Character.List
        lives_remaining = R.Field(R.Int)

    class Bean(R.Interface):
        real = R.Boolean

    class Human(R.Implements['Character', 'Bean']):
        home_planet = R.String

    human = Human.T
    fields = human.get_fields()
    assert list(fields.keys()) == ['id', 'name', 'friendsWith', 'livesRemaining', 'real', 'homePlanet']


def test_is_sensitive_to_implementation_order():
    R = TypeRegistry()

    class Character(R.Interface):
        id = R.ID
        name = R.String
        friends_with = R.Character.List
        lives_remaining = R.Field(R.Int)

    class Bean(R.Interface):
        real = R.Boolean
        hero = R.Boolean

    class Human(R.Implements[R.Bean, R.Character]):
        home_planet = R.String

    human = Human.T
    fields = human.get_fields()
    assert list(fields.keys()) == ['real', 'hero', 'id', 'name', 'friendsWith', 'livesRemaining', 'homePlanet']


def test_definition_order_wont_affect_field_order():
    R = TypeRegistry()

    class Bean(R.Interface):
        real = R.Boolean
        hero = R.Boolean

    class Character(R.Interface):
        id = R.ID
        name = R.String
        friends_with = R.Character.List
        lives_remaining = R.Field(R.Int)

    class Human(R.Implements[R.Character, Bean]):
        home_planet = R.String

    human = Human.T
    fields = human.get_fields()
    assert list(fields.keys()) == ['id', 'name', 'friendsWith', 'livesRemaining', 'real', 'hero', 'homePlanet']


def test_runtime_type_resolution():
    R = TypeRegistry()

    class Pet(R.Interface):
        name = R.String

    class Dog(R.Implements.Pet):
        bark = R.String

    class Cat(R.Implements.Pet):
        meow = R.String

    class Query(R.ObjectType):
        pets = R.Pet.List

    schema = R.Schema(Query)

    data = Query(pets=[
        Dog(name='Clifford', bark='Really big bark, because it\'s a really big dog.'),
        Cat(name='Garfield', meow='Lasagna')
    ])

    result = graphql(schema, '''
        {
            pets {
                name
                __typename
                ... on Dog {
                    bark
                }

                ... on Cat {
                    meow
                }
            }
        }

    ''', data)
    assert not result.errors
    assert result.data == {
        'pets': [{'__typename': 'Dog', 'bark': "Really big bark, because it's a really big dog.", 'name': 'Clifford'},
                 {'__typename': 'Cat', 'meow': 'Lasagna', 'name': 'Garfield'}]
    }
