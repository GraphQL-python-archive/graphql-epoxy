from graphql.core import graphql
from epoxy import TypeRegistry


def test_simple_mutation():
    R = TypeRegistry()

    class SimpleAddition(R.Mutation):
        class Input:
            a = R.Int
            b = R.Int

        class Output:
            sum = R.Int

        def execute(self, obj, input, info):
            return self.Output(sum=input.a + input.b)

    # Dummy query -- does nothing.
    class Query(R.ObjectType):
        foo = R.String

    Schema = R.Schema(R.Query, R.Mutations)

    mutation_query = '''
    mutation testSimpleAdd {
        simpleAddition(input: {a: 5, b: 10}) {
            sum
        }
    }
    '''

    result = graphql(Schema, mutation_query)
    assert not result.errors
    assert result.data == {
        'simpleAddition': {
            'sum': 15
        }
    }
