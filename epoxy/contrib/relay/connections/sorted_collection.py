from bisect import bisect_left, bisect_right
from .cursor import CursorFactory

cursor = CursorFactory('sc:')


class SortedCollection(object):
    def __init__(self, key=None):
        self._given_key = key
        key = (lambda x: x) if key is None else key
        self._keys = []
        self._items = []
        self._key = key

    def clear(self):
        self._keys = []
        self._items = []

    def copy(self):
        cls = self.__class__(key=self._key)
        cls._items = self._items[:]
        cls._keys = self._keys[:]

    def __len__(self):
        return len(self._items)

    def __getitem__(self, i):
        return self._items[i]

    def __iter__(self):
        return iter(self._items)

    def __reversed__(self):
        return reversed(self._items)

    def __repr__(self):
        return '%s(%r, key=%s)' % (
            self.__class__.__name__,
            self._items,
            getattr(self._given_key, '__name__', repr(self._given_key))
        )

    def __reduce__(self):
        return self.__class__, (self._items, self._given_key)

    def __contains__(self, item):
        k = self._key(item)
        i = bisect_left(self._keys, k)
        j = bisect_right(self._keys, k)
        return item in self._items[i:j]

    def index(self, item):
        """Find the position of an item.  Raise ValueError if not found.'"""
        k = self._key(item)
        i = bisect_left(self._keys, k)
        j = bisect_right(self._keys, k)
        return self._items[i:j].index(item) + i

    def count(self, item):
        """Return number of occurrences of item'"""
        k = self._key(item)
        i = bisect_left(self._keys, k)
        j = bisect_right(self._keys, k)
        return self._items[i:j].count(item)

    def insert(self, item):
        """Insert a new item.  If equal keys are found, add to the left'"""
        k = self._key(item)
        i = bisect_left(self._keys, k)
        if i != len(self) and self._keys[i] == k:
            raise ValueError(u'An item with the same key {} already exists in this collection.'.format(k))

        self._keys.insert(i, k)
        self._items.insert(i, item)

    def remove(self, item):
        """Remove first occurrence of item.  Raise ValueError if not found'"""
        i = self.index(item)
        del self._keys[i]
        del self._items[i]

    def bisect_left(self, k):
        return bisect_left(self._keys, k)

    def bisect_right(self, k):
        return bisect_right(self._keys, k)

    @staticmethod
    def empty_connection(relay, type_name):
        Connection, Edge = relay.get_connection_and_edge_types(type_name)

        return Connection(
            edges=[],
            page_info=relay.PageInfo(
                start_cursor=None,
                end_cursor=None,
                has_previous_page=False,
                has_next_page=False,
            )
        )

    def get_connection(self, relay, type_name, args):
        Connection, Edge = relay.get_connection_and_edge_types(type_name)
        before = args.get('before')
        after = args.get('after')
        first = args.get('first')
        last = args.get('last')

        count = len(self)
        if not count:
            return self.empty_connection(relay, type_name)

        begin_key = cursor.get_offset(after, None)
        end_key = cursor.get_offset(before, None)

        lower_bound = begin = self.bisect_left(begin_key) + 1 if begin_key else 0
        upper_bound = end = self.bisect_right(end_key) - 1 if end_key else count

        if upper_bound < count and self._keys[upper_bound] != end_key:
            upper_bound = end = count

        if first is not None:
            end = min(begin + first, end)
        if last is not None:
            begin = max(end - last, begin)

        sliced_data = self._items[begin:end]

        edges = [Edge(node=node, cursor=cursor.from_offset(self._key(node))) for node in sliced_data]
        first_edge = edges[0] if edges else None
        last_edge = edges[-1] if edges else None

        return Connection(
            edges=edges,
            page_info=relay.PageInfo(
                start_cursor=first_edge and first_edge.cursor,
                end_cursor=last_edge and last_edge.cursor,
                has_previous_page=begin > lower_bound,
                has_next_page=end < upper_bound
            )
        )
