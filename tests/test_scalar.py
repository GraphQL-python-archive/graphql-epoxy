import datetime
from graphql.core import graphql
from graphql.core.language import ast
from graphql.core.type import GraphQLScalarType
from epoxy.registry import TypeRegistry


def test_custom_scalar_type():
    R = TypeRegistry()

    def serialize_date_time(dt):
        assert isinstance(dt, datetime.datetime)
        return dt.isoformat()

    def parse_literal(node):
        if isinstance(node, ast.StringValue):
            return datetime.datetime.strptime(node.value, "%Y-%m-%dT%H:%M:%S.%f")

    def parse_value(value):
        return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")

    DateTimeType = GraphQLScalarType(name='DateTime', serialize=serialize_date_time,
                                     parse_literal=parse_literal,
                                     parse_value=parse_value)
    R(DateTimeType)

    class Query(R.ObjectType):
        datetime = R.DateTime(args={
            'in': R.DateTime
        })

        def resolve_datetime(self, obj, args, info):
            return args.get('in')

    now = datetime.datetime.now()
    isoformat = now.isoformat()

    Schema = R.Schema(R.Query)

    response = graphql(Schema, '''
        {
            datetime(in: "%s")
        }

    ''' % isoformat)

    assert not response.errors
    assert response.data == {
        'datetime': isoformat
    }

    response = graphql(Schema, '''
        query Test($date: DateTime) {
            datetime(in: $date)
        }

    ''', args={
        'date': isoformat
    })

    assert not response.errors
    assert response.data == {
        'datetime': isoformat
    }


def test_register_scalar_type():
    R = TypeRegistry()

    class DateTime(R.Scalar):
        @staticmethod
        def serialize(dt):
            assert isinstance(dt, datetime.datetime)
            return dt.isoformat()

        @staticmethod
        def parse_literal(node):
            if isinstance(node, ast.StringValue):
                return datetime.datetime.strptime(node.value, "%Y-%m-%dT%H:%M:%S.%f")

        @staticmethod
        def parse_value(value):
            return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")

    class Query(R.ObjectType):
        datetime = R.DateTime(args={
            'in': R.DateTime
        })

        def resolve_datetime(self, obj, args, info):
            return args.get('in')

    now = datetime.datetime.now()
    isoformat = now.isoformat()

    Schema = R.Schema(R.Query)

    response = graphql(Schema, '''
        {
            datetime(in: "%s")
        }

    ''' % isoformat)

    assert not response.errors
    assert response.data == {
        'datetime': isoformat
    }

    response = graphql(Schema, '''
        query Test($date: DateTime) {
            datetime(in: $date)
        }

    ''', args={
        'date': isoformat
    })

    assert not response.errors
    assert response.data == {
        'datetime': isoformat
    }
