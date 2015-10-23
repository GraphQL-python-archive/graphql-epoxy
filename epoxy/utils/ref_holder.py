from weakref import ReferenceType, ref


class RefHolder(object):
    ref = None

    def __init__(self, ref=None):
        if ref is not None:
            self.set(ref)

    def _delete_ref(self, ref):
        if ref is self.ref:
            self.ref = None

    def get(self):
        if isinstance(self.ref, ReferenceType):
            return self.ref()

    def set(self, item):
        self.ref = ref(item, self._delete_ref)
