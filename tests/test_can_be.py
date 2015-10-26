from graphql.core import graphql
from epoxy import TypeRegistry


def test_can_be():
    R = TypeRegistry()

    @R.Cat.CanBe
    class MyCat(object):
        def __init__(self, name, meow):
            self.name = name
            self.meow = meow

    class Pet(R.Interface):
        name = R.String

    class Dog(R.Implements.Pet):
        bark = R.String

    class Cat(R.Implements.Pet):
        meow = R.String

    class Bird(R.Implements.Pet):
        tweet = R.String

    class Query(R.ObjectType):
        pets = R.Pet.List

    @R.Dog.CanBe
    class MyDog(object):
        def __init__(self, name, bark):
            self.name = name
            self.bark = bark

    schema = R.Schema(Query)

    @R.Bird.CanBe
    class MyBird(object):
        def __init__(self, name, tweet):
            self.name = name
            self.tweet = tweet

    data = Query(pets=[
        MyDog(name='Clifford', bark='Really big bark, because it\'s a really big dog.'),
        MyCat(name='Garfield', meow='Lasagna'),
        MyBird(name='Tweetie', tweet='#yolo'),

        Dog(name='OTClifford', bark='Really big bark, because it\'s a really big dog.'),
        Cat(name='OTGarfield', meow='Lasagna'),
        Bird(name='OTTweetie', tweet='#yolo'),
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

                ... on Bird {
                    tweet
                }
            }
        }

    ''', data)
    assert not result.errors
    assert result.data == {
        'pets': [
            {'__typename': 'Dog', 'bark': "Really big bark, because it's a really big dog.", 'name': 'Clifford'},
            {'__typename': 'Cat', 'meow': 'Lasagna', 'name': 'Garfield'},
            {'__typename': 'Bird', 'tweet': '#yolo', 'name': 'Tweetie'},
            {'__typename': 'Dog', 'bark': "Really big bark, because it's a really big dog.", 'name': 'OTClifford'},
            {'__typename': 'Cat', 'meow': 'Lasagna', 'name': 'OTGarfield'},
            {'__typename': 'Bird', 'tweet': '#yolo', 'name': 'OTTweetie'},
        ]
    }
