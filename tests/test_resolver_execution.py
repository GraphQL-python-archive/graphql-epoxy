from graphql.core import graphql

from epoxy.registry import TypeRegistry


def test_resolves_from_interface():
    R = TypeRegistry()

    class Pet(R.Interface):
        make_noise = R.String

        def resolve_make_noise(self, *args):
            return 'I am a pet, hear me roar!'

    class Dog(R.Implements.Pet):
        pass

    class Query(R.ObjectType):
        dog = R.Dog

        def resolve_dog(self, *args):
            return Dog()

    schema = R.Schema(R.Query)
    result = graphql(schema, '{ dog { makeNoise } }')
    assert not result.errors
    assert result.data == {'dog': {'makeNoise': 'I am a pet, hear me roar!'}}


def test_field_re_definition_wont_override():
    R = TypeRegistry()

    class Pet(R.Interface):
        make_noise = R.String

        def resolve_make_noise(self, *args):
            return 'I am a pet, hear me roar!'

    class Dog(R.Implements.Pet):
        make_noise = R.String

    class Query(R.ObjectType):
        dog = R.Dog

        def resolve_dog(self, *args):
            return Dog()

    schema = R.Schema(R.Query)
    result = graphql(schema, '{ dog { makeNoise } }')
    assert not result.errors
    assert result.data == {'dog': {'makeNoise': 'I am a pet, hear me roar!'}}


def test_will_choose_first_resolver_of_first_defined_interface():
    R = TypeRegistry()

    class Pet(R.Interface):
        make_noise = R.String

        def resolve_make_noise(self, *args):
            return 'I am a pet, hear me roar!'

    class Barker(R.Interface):
        make_noise = R.String

        def resolve_make_noise(self, *args):
            return 'Woof, woof!!'

    class Dog(R.Implements[Barker, Pet]):
        make_noise = R.String

    class Query(R.ObjectType):
        dog = R.Dog

        def resolve_dog(self, *args):
            return Dog()

    schema = R.Schema(R.Query)
    result = graphql(schema, '{ dog { makeNoise } }')
    assert not result.errors
    assert result.data == {'dog': {'makeNoise': 'Woof, woof!!'}}


def test_object_type_can_override_interface_resolver():
    R = TypeRegistry()

    class Pet(R.Interface):
        make_noise = R.String

        def resolve_make_noise(self, *args):
            return 'I am a pet, hear me roar!'

    class Dog(R.Implements.Pet):
        make_noise = R.String

        def resolve_make_noise(self, *args):
            return 'Woof woof! Bark bark!'

    class Query(R.ObjectType):
        dog = R.Dog

        def resolve_dog(self, *args):
            return Dog()

    schema = R.Schema(R.Query)

    result = graphql(schema, '{ dog { makeNoise } }')
    assert not result.errors
    assert result.data == {'dog': {'makeNoise': 'Woof woof! Bark bark!'}}
