from graphql.core import graphql
from graphql.core.type import GraphQLArgument, GraphQLInputObjectType, GraphQLString
from graphql.core.type.scalars import GraphQLInt
from epoxy import TypeRegistry


def test_input_type_creation():
    R = TypeRegistry()

    class SimpleInput(R.InputType):
        a = R.Int
        b = R.Int
        some_underscore = R.String
        some_from_field = R.InputField(R.String, default_value='Hello World')

    input_type = SimpleInput.T
    assert input_type is R.SimpleInput()
    assert isinstance(input_type, GraphQLInputObjectType)
    fields = input_type.get_fields()
    assert list(fields.keys()) == ['a', 'b', 'someUnderscore', 'someFromField']
    assert [field.name for field in fields.values()] == ['a', 'b', 'someUnderscore', 'someFromField']

    assert fields['a'].type == GraphQLInt
    assert fields['b'].type == GraphQLInt
    assert fields['someUnderscore'].type == GraphQLString
    assert fields['someFromField'].type == GraphQLString
    assert fields['someFromField'].default_value == 'Hello World'

    input_value = SimpleInput({
        'a': 1,
        'someUnderscore': 'hello',
    })

    assert input_value.a == 1
    assert input_value.b is None
    assert input_value.some_underscore == 'hello'
    assert input_value.some_from_field == 'Hello World'


def test_input_type():
    R = TypeRegistry()

    class SimpleInput(R.InputType):
        a = R.Int
        b = R.Int

    class Query(R.ObjectType):
        f = R.String(args={
            'input': R.SimpleInput
        })

        def resolve_f(self, obj, args, info):
            input = SimpleInput(args['input'])
            return "I was given {i.a} and {i.b}".format(i=input)

    Schema = R.Schema(R.Query)
    query = '''
    {
        f(input: {a: 1, b: 2})
    }
    '''

    result = graphql(Schema, query)
    assert not result.errors
    assert result.data == {
        'f': "I was given 1 and 2"
    }
