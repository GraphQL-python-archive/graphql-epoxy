# Epoxy [![Build Status](https://travis-ci.org/jhgg/epoxy.svg?branch=master)](https://travis-ci.org/jhgg/epoxy)

Epoxy is a magical tool for rapid development of GraphQL types, schemas, resolvers, mutations quickly & pragmatically.

* **Minimal Boilerplate**: You can create a GraphQL schema and execute it in less than 5 lines of code.
* **Definition Ordering**: It doesn't matter. Define your objects in any order you want. Epoxy will take care of the rest.
* **Quick**: Once you create your schema, epoxy doesn't get in the way. Your resolvers will be called directly by 
`graphql-core` with no additional indirection.

This codebase is currently a **WORK IN PROGRESS** and does not currently work. If you're looking for a pythonic 
`graphql-core` wrapper, check out [`graphene`](https://github.com/graphql-python/graphene).

## Installation

Epoxy is available on pypi under the package name `graphql-epoxy`, you can get it by running:

```sh
pip install graphql-epoxy
```

## Usage

Defining a GraphQL Schema using Epoxy is as simple as creating a `TypeRegistry` and using it to create types for you.

```python

from epoxy import TypeRegistry
R = TypeRegistry()

class Character(R.ObjectType):
    id = R.ID
    name = R.String
    friends = R.Character.List
    

class Human(R.ObjectTypeWithInterfaces(Character)):
    home_planet = R.String.NonNull
    
    
class Query(R.ObjectType):
    human = R.Human
    
    def resolve_human(self, obj, args, info):
        return Human(5, 'Bob', [Human(6, 'Bill')]


schema = R.schema(R.Query)

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


    def resolve_mood(self, *args):
        return MoodStatus.HAPPY.value

```

Schema is a `GraphQLSchema` object. You can now use it with graphql:

```python
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

Notice that `epoxy` converted snake_cased fields to camel_case in the GraphQL Schema.

## Mutations (Coming Soon)

Epoxy also supports defining mutations:


```python

class AddFriend(R.Mutation):
    class Input(R.InputType):
        human_to_add = R.ID.NonNull
        
    class Output(R.OutputType):
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






