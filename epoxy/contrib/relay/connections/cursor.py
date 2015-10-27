from ..utils import base64, unbase64


class CursorFactory(object):
    def __init__(self, prefix):
        self.prefix = prefix
        self.cursor_type = int
        self.max_cursor_length = 10

    def from_offset(self, offset):
        """
        Creates the cursor string from an offset.
        """
        return base64(self.prefix + str(offset))

    def to_offset(self, cursor):
        """
        Rederives the offset from the cursor string.
        """
        try:
            return self.cursor_type(unbase64(cursor)[len(self.prefix):len(self.prefix) + self.max_cursor_length])
        except:
            return None

    def get_offset(self, cursor, default_offset=0):
        """
        Given an optional cursor and a default offset, returns the offset
        to use; if the cursor contains a valid offset, that will be used,
        otherwise it will be the default.
        """
        if cursor is None:
            return default_offset

        offset = self.to_offset(cursor)
        try:
            return self.cursor_type(offset)
        except:
            return default_offset
