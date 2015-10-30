# Epoxy [![Build Status](https://travis-ci.org/graphql-python/graphql-epoxy.svg?branch=v0.1a0)](https://travis-ci.org/graphql-python/graphql-epoxy) [![Coverage Status](https://coveralls.io/repos/graphql-python/graphql-epoxy/badge.svg?branch=master&service=github)](https://coveralls.io/github/graphql-python/graphql-epoxy?branch=master) [![PyPI version](https://badge.fury.io/py/graphql-epoxy.svg)](https://badge.fury.io/py/graphql-epoxy)

Epoxy is a magical tool for rapid development of GraphQL types, schemas, resolvers, mutations quickly & pragmatically.

* **Minimal Boilerplate**: You can create a GraphQL schema and execute it in less than 5 lines of code.
* **Definition Ordering**: It doesn't matter. Define your objects in any order you want. Epoxy will take care of the rest.
* **Quick**: Once you create your schema, epoxy doesn't get in the way. Your resolvers will be called directly by 
`graphql-core` with no additional indirection.

This codebase is currently a **WORK IN PROGRESS**, and is currently at alpha stages. The API may change without notice. 
If you're looking for a more stable pythonic `graphql-core` wrapper, check out 
[`graphene`](https://github.com/graphql-python/graphene).

## Installation

Epoxy is available on pypi under the package name `graphql-epoxy`, you can get it by running:

```sh
pip install graphql-epoxy==0.1a0
```

## Usage

Defining a GraphQL Schema using Epoxy is as simple as creating a `TypeRegistry` and using it to create types for you.

```python

from epoxy import TypeRegistry
R = TypeRegistry()

class Character(R.Interface):
    id = R.ID
    name = R.String
    friends = R.Character.List
    

class Human(R.Implements.Character):
    home_planet = R.String.NonNull
    
    
class Query(R.ObjectType):
    human = R.Human
    foo = R.Foo  # This is defined below! Ordering doesn't matter! 
    
    def resolve_human(self, obj, args, info):
        """This will be used as the description of the field Query.human."""
        return Human(5, 'Bob', [Human(6, 'Bill')]

```

You can even have `epoxy` learn about your already defined Python enums. 

```python
class MoodStatus(enums.Enum):
    HAPPY = 1
    SAD = 2
    MELANCHOLY = 3


R(MoodStatus)

```

And then use it in an ObjectType:

```python
class Foo(R.ObjectType):
    mood = R.MoodStatus
    # or 
    mood = R.Field(R.MoodStatus, description="Describing the mood of Foo, is sometimes pretty hard.")

    def resolve_mood(self, *args):
        return MoodStatus.HAPPY.value

```

Schema is a `GraphQLSchema` object. You can now use it with graphql:

```python
schema = R.schema(R.Query)

result = graphql(schema, '''
{
    human {
        id
        name
        homePlanet
        friends {
            name
            homePlanet
        }
        
    }
}
''')

```

The schema is now defined as: 

```graphql

enum MoodStatus {
    HAPPY
    SAD
    MELANCHOLY
}

interface Character {
    id: ID
    name: String
    friends: [Character]
}

type Human implements Character {
    id: ID
    name: String
    friends: [Character]
    homePlanet: String!
}

type Foo {
    mood: MoodStatus
}

type Query {
    human: Human
    foo: Foo
}
```

Notice that `epoxy` converted snake_cased fields to camelCase in the GraphQL Schema.

## ObjectTypes become containers

You can bring your own objects, (like a Django or SQLAlchemy model), or you can use the class you just created:

```python

me = Human(id=2, name='Jake', home_planet='Earth', friends=[Human(id=3, name='Syrus', home_planet='Earth')])

print(me) # <Human id=2, name='Jake', home_planet='Earth', friends=[<Human id=3, name='Syrus', home_planet='Earth', friends=[]>]]>
print(me.name) # Jake
```

Epoxy will automatically resolve the runtime types of your objects if class that you created from `R.ObjectType`, but 
if you want to bring your own `Human` (i.e. a model.Model from Django), just tell Epoxy about it! And if you don't want
to, you can just override the `is_type_of` function inside `Human` to something more to your liking.

### `my_app/models.py`
```python
from django.db import models
from my_app.graphql import R

@R.Human.CanBe
class RealHumanBean(models.Model):
    """
    And a real hero.
    """
    name = models.CharField(name=Name)


# Or if you don't want to use the decorator:
R.Human.CanBe(Human)
```

## Relay Support (WIP)
 - [x] Node
 - [x] Connection & Edges
 - [ ] Mutations

At this point, Epoxy has rudimentary `relay` support. Enable support for `Relay` by mixing in the `RelayMixin` using
`TypeResolver.Mixin`. 

```python
from epoxy.contrib.relay import RelayMixin
from epoxy.contrib.relay.data_source.memory import InMemoryDataSource

# Epoxy provides an "in memory" data source, that implements `epoxy.contrib.relay.data_source.BaseDataSource`,
# which can be used to easily create a mock data source. In practice, you'd implement your own data source.
data_source = InMemoryDataSource()

R = TypeRegistry()
Relay = R.Mixin(RelayMixin, data_source)
```

### Node Definition
Once `RelayMixin` has been mixed into the Registry, things can subclass `Node` automatically!

```python

class Pet(R.Implements[Relay.Node]):
    name = R.String
    
```

### Connection Definition & `NodeField`
Connections can be defined upon any object type. Here we'll make a `Query` root node that provides a connection
to a list of pets & a node field to resolve an indivudal node. 

```python

class Query(R.ObjectType):
    pets = Relay.Connection('Pet', R.Pet) # The duplicate 'Pet' definition is just temporary and will be removed.
    node = Relay.NodeField

```

### Adding some data!
Let's add some pets to the `data_source` and query them!

```python

# Schema has to be defined so that all thunks are resolved before we can use `Pet` as a container.
Schema = R.Schema(R.Query)

pet_names = ["Max", "Buddy", "Charlie", "Jack", "Cooper", "Rocky"]

for i, pet_name in enumerate(pet_names, 1):
    data_source.add(Pet(id=i, name=pet_name))

```


### Running Relay Connection Query:

```python

result = graphql(Schema, '''
{
    pets(first: 5) {
        edges {
            node {
                id
                name
            }
            cursor
        }
        pageInfo {
            hasPreviousPage
            hasNextPage
            startCursor
            endCursor
        }
    }
    node(id: "UGV0OjU=") {
        id
        ... on Pet {
            name
        }
    }
}
''')
```


## Mutations (Coming Soon)

Epoxy also supports defining mutations. Making a Mutation a Relay mutation is as simple as changing `R.Mutation` to 
`Relay.Mutation`.


```python

class AddFriend(R.Mutation):
    class Input:
        human_to_add = R.ID.NonNull
        
    class Output:
        new_friends_list = R.Human.List
        
    @R.resolve_with_args
    def resolve(self, obj, human_to_add):
        obj.add_friend(human_to_add)
        return self.Output(new_friends_list=obj.friends)

        
schema = R.schema(R.Query, R.Mutations)

```

You can then execute the query:


```graphql
mutation AddFriend {
    addFriend(input: {humanToAdd: 6}) {
        newFriendsList {
            id
            name
            homePlanet
        }
    }
}
```






