from collections import OrderedDict
from functools import partial
from graphql.core.type import GraphQLObjectType
from graphql.core.type.definition import GraphQLInterfaceType, GraphQLUnionType
from ..utils.get_declared_fields import get_declared_fields
from ..utils.make_default_resolver import make_default_resolver
from ..utils.no_implementation_registration import no_implementation_registration
from ..utils.weak_ref_holder import WeakRefHolder
from ..utils.yank_potential_fields import yank_potential_fields


class ObjectTypeMeta(type):
    def __new__(mcs, name, bases, attrs):
        if attrs.pop('abstract', False):
            return super(ObjectTypeMeta, mcs).__new__(mcs, name, bases, attrs)

        with no_implementation_registration():
            union_type = GraphQLUnionType(
                name,
                types=mcs._get_types()
                description=attrs.get('__doc__'),
            )

        mcs._register(union_type)
        cls = super(ObjectTypeMeta, mcs).__new__(mcs, name, bases, attrs)
        cls.T = union_type
        cls._registry = mcs._get_registry()

        return cls

    @staticmethod
    def _register(union_type):
        raise NotImplementedError('_register must be implemented in the sub-metaclass')

    @staticmethod
    def _get_registry():
        raise NotImplementedError('_get_registry must be implemented in the sub-metaclass')

    @staticmethod
    def _get_types():
        return None
