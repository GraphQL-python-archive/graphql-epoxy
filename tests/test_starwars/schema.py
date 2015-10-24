from graphql.core.type.definition import GraphQLArgument
from epoxy.registry import TypeRegistry
import enum

R = TypeRegistry()


@R.Register
class Episode(enum.Enum):
    NEWHOPE = 4
    EMPIRE = 5
    JEDI = 6


class Character(R.Interface):
    id = R.String.NonNull
    name = R.String
    friends = R.Character.List
    appears_in = R.Episode.List

    def resolve_friends(self, obj, args, info):
        from .data import get_friends
        return get_friends(obj)

class Human(R.Implements.Character):
    home_planet = R.String


class Droid(R.Implements.Character):
    primary_function = R.String


class Query(R.ObjectType):
    # Args API will change.
    hero = R.Field(R.Character, args={
        'episode': GraphQLArgument(R.Episode())
    })

    human = R.Field(R.Human, args={
        'id': GraphQLArgument(R.String())
    })

    droid = R.Field(R.Droid, args={
        'id': GraphQLArgument(R.String())
    })

    def resolve_hero(self, obj, args, info):
        from .data import get_hero
        return get_hero(args.get('episode'))

    def resolve_human(self, obj, args, info):
        from .data import get_human
        return get_human(args['id'])

    def resolve_droid(self, obj, args, info):
        from .data import get_droid
        return get_droid(args['id'])


StarWarsSchema = R.Schema(R.Query)
