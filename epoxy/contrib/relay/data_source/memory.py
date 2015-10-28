from collections import defaultdict
from operator import attrgetter
from six import text_type

from ..connections.sorted_collection import SortedCollection
from .base import BaseDataSource


class InMemoryDataSource(BaseDataSource):
    def __init__(self):
        self.objects_by_type_and_id = defaultdict(dict)
        self.objects_by_type = defaultdict(lambda: SortedCollection(key=attrgetter('id')))

    def add(self, obj):
        self.objects_by_type_and_id[obj.T][text_type(obj.id)] = obj
        self.objects_by_type[obj.T].insert(obj)

    def fetch_node(self, object_type, id, resolve_info):
        return self.objects_by_type_and_id[object_type].get(text_type(id))

    def make_connection_resolver(self, relay, object_type_thunk):
        def resolver(obj, args, info):
            object_type = relay.R[object_type_thunk]()
            return self.objects_by_type[object_type].get_connection(relay, object_type.name, args)

        return resolver
