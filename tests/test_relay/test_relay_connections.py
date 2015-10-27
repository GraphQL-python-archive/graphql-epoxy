from graphql.core import graphql
from epoxy.contrib.relay import RelayMixin
from epoxy.contrib.relay.data_source.memory import InMemoryDataSource
from epoxy.contrib.relay.utils import base64
from epoxy.registry import TypeRegistry

pet_names = ["Max", "Buddy", "Charlie", "Jack", "Cooper", "Rocky", "Toby", "Tucker", "Jake", "Bear", "Duke", "Teddy",
             "Oliver", "Riley", "Bailey", "Bentley", "Milo", "Buster", "Cody", "Dexter", "Winston", "Murphy", "Leo",
             "Lucky", "Oscar", "Louie", "Zeus", "Henry", "Sam", "Harley", "Baxter", "Gus", "Sammy", "Jackson", "Bruno",
             "Diesel", "Jax", "Gizmo", "Bandit", "Rusty", "Marley", "Jasper", "Brody", "Roscoe", "Hank", "Otis", "Bo",
             "Joey", "Beau", "Ollie", "Tank", "Shadow", "Peanut", "Hunter", "Scout", "Blue", "Rocco", "Simba", "Tyson",
             "Ziggy", "Boomer", "Romeo", "Apollo", "Ace", "Luke", "Rex", "Finn", "Chance", "Rudy", "Loki", "Moose",
             "George", "Samson", "Coco", "Benny", "Thor", "Rufus", "Prince", "Chester", "Brutus", "Scooter", "Chico",
             "Spike", "Gunner", "Sparky", "Mickey", "Kobe", "Chase", "Oreo", "Frankie", "Mac", "Benji", "Bubba",
             "Champ", "Brady", "Elvis", "Copper", "Cash", "Archie", "Walter"]

R = TypeRegistry()
Relay = R.Mixin(RelayMixin)


class Pet(R.Implements[R.Node]):
    name = R.String


data_source = InMemoryDataSource()


class Query(R.ObjectType):
    pets = Relay.Connection('Pet', R.Pet, resolver=data_source.make_connection_resolver(Relay, R.Pet))
    node = Relay.NodeField


Schema = R.Schema(R.Query)

pets = []
for i, pet_name in enumerate(pet_names, 1):
    pet = Pet(id=i, name=pet_name)
    pets.append(pet)
    data_source.add(pet)


def test_query_pets_all():
    result = graphql(Schema, '''
    {
        pets {
            edges {
                node {
                    id
                    name
                }
                cursor
            }
            pageInfo {
                hasPreviousPage
                hasNextPage
                startCursor
                endCursor
            }
        }
    }
    ''')

    expected_edges = [
        {
            'node': {
                'id': base64('Pet:%s' % p.id),
                'name': p.name
            },
            'cursor': base64('sc:%s' % p.id)
        }
        for p in pets
        ]

    expected_page_info = {
        'hasNextPage': False,
        'hasPreviousPage': False,
        'endCursor': expected_edges[-1]['cursor'],
        'startCursor': expected_edges[0]['cursor']
    }

    assert not result.errors
    assert result.data == {
        'pets': {
            'edges': expected_edges,
            'pageInfo': expected_page_info
        }
    }


def test_query_pets_first_5():
    result = graphql(Schema, '''
    {
        pets(first: 5) {
            edges {
                node {
                    id
                    name
                }
                cursor
            }
            pageInfo {
                hasPreviousPage
                hasNextPage
                startCursor
                endCursor
            }
        }
    }
    ''')

    expected_edges = [
        {
            'node': {
                'id': base64('Pet:%s' % p.id),
                'name': p.name
            },
            'cursor': base64('sc:%s' % p.id)
        }
        for p in pets[:5]
        ]

    expected_page_info = {
        'hasNextPage': True,
        'hasPreviousPage': False,
        'endCursor': expected_edges[-1]['cursor'],
        'startCursor': expected_edges[0]['cursor']
    }

    assert not result.errors
    assert result.data == {
        'pets': {
            'edges': expected_edges,
            'pageInfo': expected_page_info
        }
    }


def test_query_pets_last_5():
    result = graphql(Schema, '''
    {
        pets(last: 5) {
            edges {
                node {
                    id
                    name
                }
                cursor
            }
            pageInfo {
                hasPreviousPage
                hasNextPage
                startCursor
                endCursor
            }
        }
    }
    ''')

    expected_edges = [
        {
            'node': {
                'id': base64('Pet:%s' % p.id),
                'name': p.name
            },
            'cursor': base64('sc:%s' % p.id)
        }
        for p in pets[-5:]
        ]

    expected_page_info = {
        'hasNextPage': False,
        'hasPreviousPage': True,
        'endCursor': expected_edges[-1]['cursor'],
        'startCursor': expected_edges[0]['cursor']
    }

    assert not result.errors
    assert result.data == {
        'pets': {
            'edges': expected_edges,
            'pageInfo': expected_page_info
        }
    }


def test_query_pets_first_10_last_5():
    result = graphql(Schema, '''
    {
        pets(first: 10, last: 5) {
            edges {
                node {
                    id
                    name
                }
                cursor
            }
            pageInfo {
                hasPreviousPage
                hasNextPage
                startCursor
                endCursor
            }
        }
    }
    ''')

    expected_edges = [
        {
            'node': {
                'id': base64('Pet:%s' % p.id),
                'name': p.name
            },
            'cursor': base64('sc:%s' % p.id)
        }
        for p in pets[:10][-5:]
        ]

    expected_page_info = {
        'hasNextPage': True,
        'hasPreviousPage': True,
        'endCursor': expected_edges[-1]['cursor'],
        'startCursor': expected_edges[0]['cursor']
    }

    assert not result.errors
    assert result.data == {
        'pets': {
            'edges': expected_edges,
            'pageInfo': expected_page_info
        }
    }


def test_after_cursor():
    result = graphql(Schema, '''
    {
        pets(first: 10, after: "c2M6MTA=") {
            edges {
                node {
                    id
                    name
                }
                cursor
            }
            pageInfo {
                hasPreviousPage
                hasNextPage
                startCursor
                endCursor
            }
        }
    }
    ''')

    expected_edges = [
        {
            'node': {
                'id': base64('Pet:%s' % p.id),
                'name': p.name
            },
            'cursor': base64('sc:%s' % p.id)
        }
        for p in pets[9:19]
        ]

    assert len(expected_edges) == 10
    expected_page_info = {
        'hasNextPage': True,
        'hasPreviousPage': False,
        'endCursor': expected_edges[-1]['cursor'],
        'startCursor': expected_edges[0]['cursor']
    }

    assert not result.errors
    assert result.data == {
        'pets': {
            'edges': expected_edges,
            'pageInfo': expected_page_info
        }
    }


def test_before_cursor():
    result = graphql(Schema, '''
    {
        pets(first: 10, before: "c2M6MTA=") {
            edges {
                node {
                    id
                    name
                }
                cursor
            }
            pageInfo {
                hasPreviousPage
                hasNextPage
                startCursor
                endCursor
            }
        }
    }
    ''')

    expected_edges = [
        {
            'node': {
                'id': base64('Pet:%s' % p.id),
                'name': p.name
            },
            'cursor': base64('sc:%s' % p.id)
        }
        for p in pets[:10]
        ]

    assert len(expected_edges) == 10
    expected_page_info = {
        'hasNextPage': False,
        'hasPreviousPage': False,
        'endCursor': expected_edges[-1]['cursor'],
        'startCursor': expected_edges[0]['cursor']
    }

    assert not result.errors
    assert result.data == {
        'pets': {
            'edges': expected_edges,
            'pageInfo': expected_page_info
        }
    }
