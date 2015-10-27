from graphql.core import graphql
from epoxy.contrib.relay import RelayMixin
from epoxy.contrib.relay.data_source.memory import InMemoryDataSource
from epoxy.registry import TypeRegistry


def test_relay_node_definition():
    R = TypeRegistry()
    Relay = R.Mixin(RelayMixin, InMemoryDataSource())

    class Pet(R.Implements[R.Node]):
        name = R.String

    class Query(R.ObjectType):
        pets = R.Pet.List
        node = Relay.NodeField

    schema = R.Schema(R.Query)

    pets = {
        '5': Pet(id='5', name='Garfield'),
        '6': Pet(id='6', name='Odis')
    }

    data = Query(pets=[pets['5'], pets['6']])
    result = graphql(schema, '{ pets { id, name } }', data)
    assert result.data == {'pets': [{'id': 'UGV0OjU=', 'name': 'Garfield'}, {'id': 'UGV0OjY=', 'name': 'Odis'}]}
    assert not result.errors


def test_relay_node_definition_using_custom_type():
    R = TypeRegistry()
    Relay = R.Mixin(RelayMixin, InMemoryDataSource())

    class Pet(R.Implements[R.Node]):
        name = R.String

    class Query(R.ObjectType):
        pets = R.Pet.List
        node = Relay.NodeField

    schema = R.Schema(R.Query)

    @R.Pet.CanBe
    class MyPet(object):
        def __init__(self, id, name):
            self.id = id
            self.name = name

    pets = {
        '5': MyPet(id='5', name='Garfield'),
        '6': MyPet(id='6', name='Odis')
    }

    data = Query(pets=[pets['5'], pets['6']])
    result = graphql(schema, '{ pets { id, name } }', data)
    assert result.data == {'pets': [{'id': 'UGV0OjU=', 'name': 'Garfield'}, {'id': 'UGV0OjY=', 'name': 'Odis'}]}
    assert not result.errors


def test_relay_node_field_resolver():
    data_source = InMemoryDataSource()

    R = TypeRegistry()
    Relay = R.Mixin(RelayMixin, data_source)

    class Pet(R.Implements[R.Node]):
        name = R.String

    class Query(R.ObjectType):
        pets = R.Pet.List
        node = Relay.NodeField

    schema = R.Schema(R.Query)

    data_source.add(Pet(id='5', name='Garfield'))
    data_source.add(Pet(id='6', name='Odis'))

    result = graphql(schema, '''
    {
        node(id: "UGV0OjU=") {
            id,
            ... on Pet {
                name
            }
        }
    }
    ''')

    assert not result.errors
    assert result.data == {'node': {'id': 'UGV0OjU=', 'name': 'Garfield'}}
