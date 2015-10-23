from contextlib import contextmanager
from graphql.core.type import definition


@contextmanager
def no_implementation_registration():
    old_definition = definition.add_impl_to_interfaces
    definition.add_impl_to_interfaces = lambda type: None
    try:
        yield

    finally:
        definition.add_impl_to_interfaces = old_definition
