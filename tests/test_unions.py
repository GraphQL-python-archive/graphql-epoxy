from graphql.core import graphql
from epoxy import TypeRegistry


def test_runtime_type_resolution():
    R = TypeRegistry()

    class Pet(R.Union[R.Dog, R.Cat]):
        pass

    class Dog(R.ObjectType):
        bark = R.String
        name = R.String

    class Cat(R.ObjectType):
        meow = R.String
        name = R.String

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
                __typename
                ... on Dog {
                    name
                    bark
                }

                ... on Cat {
                    name
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
