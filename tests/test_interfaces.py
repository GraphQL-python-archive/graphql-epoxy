from epoxy.registry import TypeRegistry


def test_register_interface():
    R = TypeRegistry()

    class Character(R.Interface):
        id = R.ID
        name = R.String
        friends_with = R.Character.List
        lives_remaining = R.Field(R.Int)

    character = Character.T
    fields = character.get_fields()
    assert list(fields.keys()) == ['id', 'name', 'friendsWith', 'livesRemaining']


def test_register_single_type():
    R = TypeRegistry()

    class Character(R.Interface):
        id = R.ID
        name = R.String
        friends_with = R.Character.List
        lives_remaining = R.Field(R.Int)

    class Human(R.Implements.Character):
        home_planet = R.String

    human = Human.T
    fields = human.get_fields()
    assert list(fields.keys()) == ['id', 'name', 'friendsWith', 'livesRemaining', 'homePlanet']


def test_implements_multiple_interfaces_via_r():
    R = TypeRegistry()

    class Character(R.Interface):
        id = R.ID
        name = R.String
        friends_with = R.Character.List
        lives_remaining = R.Field(R.Int)

    class Bean(R.Interface):
        real = R.Boolean

    class Human(R.Implements[R.Character, R.Bean]):
        home_planet = R.String

    human = Human.T
    fields = human.get_fields()
    assert list(fields.keys()) == ['id', 'name', 'friendsWith', 'livesRemaining', 'real', 'homePlanet']


def test_implements_multiple_interfaces_via_class():
    R = TypeRegistry()

    class Character(R.Interface):
        id = R.ID
        name = R.String
        friends_with = R.Character.List
        lives_remaining = R.Field(R.Int)

    class Bean(R.Interface):
        real = R.Boolean

    class Human(R.Implements[Character, Bean]):
        home_planet = R.String

    human = Human.T
    fields = human.get_fields()
    assert list(fields.keys()) == ['id', 'name', 'friendsWith', 'livesRemaining', 'real', 'homePlanet']


def test_implements_multiple_interfaces_via_string():
    R = TypeRegistry()

    class Character(R.Interface):
        id = R.ID
        name = R.String
        friends_with = R.Character.List
        lives_remaining = R.Field(R.Int)

    class Bean(R.Interface):
        real = R.Boolean

    class Human(R.Implements['Character', 'Bean']):
        home_planet = R.String

    human = Human.T
    fields = human.get_fields()
    assert list(fields.keys()) == ['id', 'name', 'friendsWith', 'livesRemaining', 'real', 'homePlanet']


def test_is_sensitive_to_implementation_order():
    R = TypeRegistry()

    class Character(R.Interface):
        id = R.ID
        name = R.String
        friends_with = R.Character.List
        lives_remaining = R.Field(R.Int)

    class Bean(R.Interface):
        real = R.Boolean
        hero = R.Boolean

    class Human(R.Implements[R.Bean, R.Character]):
        home_planet = R.String

    human = Human.T
    fields = human.get_fields()
    assert list(fields.keys()) == ['real', 'hero', 'id', 'name', 'friendsWith', 'livesRemaining', 'homePlanet']


def test_definition_order_wont_affect_field_order():
    R = TypeRegistry()

    class Bean(R.Interface):
        real = R.Boolean
        hero = R.Boolean

    class Character(R.Interface):
        id = R.ID
        name = R.String
        friends_with = R.Character.List
        lives_remaining = R.Field(R.Int)

    class Human(R.Implements[R.Character, Bean]):
        home_planet = R.String

    human = Human.T
    fields = human.get_fields()
    assert list(fields.keys()) == ['id', 'name', 'friendsWith', 'livesRemaining', 'real', 'hero', 'homePlanet']
