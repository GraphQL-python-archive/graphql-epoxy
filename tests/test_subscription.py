from graphql.core import graphql

from epoxy.registry import TypeRegistry


def test_can_define_and_execute_subscription():
    R = TypeRegistry()

    class Query(R.ObjectType):
        a = R.Int

    class Subscription(R.ObjectType):
        subscribe_to_foo = R.Boolean(args={'id': R.Int})

        def resolve_subscribe_to_foo(self, obj, args, info):
            return args.get('id') == 1

    Schema = R.Schema(R.Query, subscription=R.Subscription)

    response = graphql(Schema, '''
    subscription {
        subscribeToFoo(id: 1)
    }
    ''')

    assert not response.errors
    assert response.data == {
        'subscribeToFoo': True
    }
