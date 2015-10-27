class BaseDataSource(object):
    def fetch_node(self, object_type, id, resolve_info):
        raise NotImplementedError('Must implement fetch_node to resolve node by ID.')

    def make_connection_resolver(self, relay, object_type_thunk):
        raise NotImplementedError('Must implement make_connection_resolver so that RelayMixin can automatically '
                                  'create connection resolvers')
