from collections import OrderedDict

from six import wraps


def wrap_resolver_translating_arguments(resolver, arguments_to_original_case):
    translate_key = arguments_to_original_case.get

    @wraps(resolver)
    def wrapped(obj, args, info):
        new_args = OrderedDict() if isinstance(args, OrderedDict) else {}
        for k in args:
            new_args[translate_key(k, k)] = args[k]

        return resolver(obj, new_args, info)

    return wrapped
