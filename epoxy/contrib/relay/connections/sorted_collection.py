from bisect import bisect_left, bisect_right
from .cursor import CursorFactory

cursor = CursorFactory('sc:')


class SortedCollection(object):
    """Sequence sorted by a key function.

    SortedCollection() is much easier to work with than using bisect() directly.
    It supports key functions like those use in sorted(), min(), and max().
    The result of the key function call is saved so that keys can be searched
    efficiently.

    Instead of returning an insertion-point which can be hard to interpret, the
    five find-methods return a specific item in the sequence. They can scan for
    exact matches, the last item less-than-or-equal to a key, or the first item
    greater-than-or-equal to a key.

    Once found, an item's ordinal position can be located with the index() method.
    New items can be added with the insert() and insert_right() methods.
    Old items can be deleted with the remove() method.

    The usual sequence methods are provided to support indexing, slicing,
    length lookup, clearing, copying, forward and reverse iteration, contains
    checking, item counts, item removal, and a nice looking repr.

    Finding and indexing are O(log n) operations while iteration and insertion
    are O(n).  The initial sort is O(n log n).

    The key function is stored in the 'key' attribute for easy introspection or
    so that you can assign a new key function (triggering an automatic re-sort).

    In short, the class was designed to handle all of the common use cases for
    bisect but with a simpler API and support for key functions.

    >>> from pprint import pprint
    >>> from operator import itemgetter

    >>> s = SortedCollection(key=itemgetter(2))
    >>> for record in [
    ...         ('roger', 'young', 30),
    ...         ('angela', 'jones', 28),
    ...         ('bill', 'smith', 22),
    ...         ('david', 'thomas', 32)]:
    ...     s.insert(record)

    >>> pprint(list(s))         # show records sorted by age
    [('bill', 'smith', 22),
     ('angela', 'jones', 28),
     ('roger', 'young', 30),
     ('david', 'thomas', 32)]

    >>> s.find_le(29)           # find oldest person aged 29 or younger
    ('angela', 'jones', 28)
    >>> s.find_lt(28)           # find oldest person under 28
    ('bill', 'smith', 22)
    >>> s.find_gt(28)           # find youngest person over 28
    ('roger', 'young', 30)

    >>> r = s.find_ge(32)       # find youngest person aged 32 or older
    >>> s.index(r)              # get the index of their record
    3
    >>> s[3]                    # fetch the record at that index
    ('david', 'thomas', 32)

    >>> s.key = itemgetter(0)   # now sort by first name
    >>> pprint(list(s))
    [('angela', 'jones', 28),
     ('bill', 'smith', 22),
     ('david', 'thomas', 32),
     ('roger', 'young', 30)]

    """

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

        begin_key = cursor.get_offset(after, None) or self._keys[0]
        end_key = cursor.get_offset(before, None) or self._keys[-1]

        begin = self.bisect_left(begin_key)
        end = self.bisect_right(end_key)

        if begin >= count or begin >= end:
            return self.empty_connection(relay, type_name)

        first_preslice_cursor = cursor.from_offset(self._keys[begin])
        last_preslice_cursor = cursor.from_offset(self._keys[min(end, count) - 1])

        if first is not None:
            end = min(begin + first, end)
        if last is not None:
            begin = max(end - last, begin)

        if begin >= count or begin >= end:
            return self.empty_connection(relay, type_name)

        sliced_data = self._items[begin:end]

        edges = [Edge(node=node, cursor=cursor.from_offset(self._key(node))) for node in sliced_data]
        first_edge = edges[0]
        last_edge = edges[-1]

        return Connection(
            edges=edges,
            page_info=relay.PageInfo(
                start_cursor=first_edge.cursor,
                end_cursor=last_edge.cursor,
                has_previous_page=(first_edge.cursor != first_preslice_cursor),
                has_next_page=(last_edge.cursor != last_preslice_cursor)
            )
        )
