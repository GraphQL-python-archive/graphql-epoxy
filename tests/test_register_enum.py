from graphql.core.type.definition import GraphQLEnumType
from epoxy.registry import TypeRegistry
from enum import Enum


def test_register_single_type():
    R = TypeRegistry()

    class MyEnum(Enum):
        FOO = 1
        BAR = 2
        BAZ = 3

    R(MyEnum)

    enum = R.type('MyEnum')
    assert isinstance(enum, GraphQLEnumType)
    values = enum.get_values()
    assert [v.name for v in values] == ['FOO', 'BAR', 'BAZ']
    assert [v.value for v in values] == [1, 2, 3]
