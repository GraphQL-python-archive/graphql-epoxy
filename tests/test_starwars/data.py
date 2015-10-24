from .schema import Human, Droid, Episode

luke = Human(
    id='1000',
    name='Luke Skywalker',
    friends=['1002', '1003', '2000', '2001'],
    appears_in=[4, 5, 6],
    home_planet='Tatooine'
)

vader = Human(
    id='1001',
    name='Darth Vader',
    friends=['1004'],
    appears_in=[4, 5, 6],
    home_planet=['Tatooine']
)

han = Human(
    id='1002',
    name='Han Solo',
    friends=['1000', '1003', '2001'],
    appears_in=[4, 5, 6]
)

leia = Human(
    id='1003',
    name='Leia Organa',
    friends=['1000', '1002', '2000', '2001'],
    appears_in=[4, 5, 6],
    home_planet='Alderaan'
)

tarkin = Human(
    id='1004',
    name='Wilhuff Tarkin',
    friends=['1001'],
    appears_in=[4]
)

humans = {i.id: i for i in (luke, vader, han, leia, tarkin)}

threepio = Droid(
    id='2000',
    name='C-3PO',
    friends=['1000', '1002', '1003', '2001'],
    appears_in=[4, 5, 6],
    primary_function='Protocol'
)

artoo = Droid(
    id='2001',
    name='R2-D2',
    friends=['1000', '1002', '1003'],
    appears_in=[4, 5, 6],
    primary_function='Astromech'
)

droids = {i.id: i for i in (threepio, artoo)}


def get_character(id):
    return humans.get(id) or droids.get(id)


def get_hero(episode):
    if episode == 5:
        return luke

    return artoo


get_human = humans.get
get_droid = droids.get


def get_friends(character):
    return [get_character(id) for id in character.friends]
