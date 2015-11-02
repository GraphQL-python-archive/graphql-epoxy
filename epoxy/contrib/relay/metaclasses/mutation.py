from ....metaclasses.mutation import MutationMeta


class RelayMutationMeta(MutationMeta):
    @staticmethod
    def _process_input_attrs(registry, input_attrs):
        input_attrs['client_mutation_id'] = registry.String
        return input_attrs

    @staticmethod
    def _process_output_attrs(registry, output_attrs):
        output_attrs['client_mutation_id'] = registry.String
        return output_attrs

    @staticmethod
    def _process_resolver(resolver, input_class, obj, args, info):
        input_obj = input_class(args.get('input'))
        result = resolver(obj, input_obj, info)
        result.client_mutation_id = input_obj.client_mutation_id
        return result
