from graphql.core import graphql
from epoxy.contrib.relay import RelayMixin
from epoxy.contrib.relay.data_source.memory import InMemoryDataSource
from epoxy.contrib.relay.utils import base64
from epoxy.registry import TypeRegistry

letter_chars = ['A', 'B', 'C', 'D', 'E']

data_source = InMemoryDataSource()

R = TypeRegistry()
Relay = R.Mixin(RelayMixin, data_source)


class Letter(R.Implements[Relay.Node]):
    letter = R.String


class Query(R.ObjectType):
    letters = Relay.Connection('Letter', R.Letter)
    node = Relay.NodeField


Schema = R.Schema(R.Query)

letters = {}
for i, letter in enumerate(letter_chars, 1):
    l = Letter(id=i, letter=letter)
    letters[letter] = l
    data_source.add(l)


def edges(selected_letters):
    return [
        {
            'node': {
                'id': base64('Letter:%s' % l.id),
                'letter': l.letter
            },
            'cursor': base64('sc:%s' % l.id)
        }
        for l in [letters[i] for i in selected_letters]
    ]


def cursor_for(ltr):
    l = letters[ltr]
    return base64('sc:%s' % l.id)


def execute(args=''):
    if args:
        args = '(' + args + ')'

    return graphql(Schema, '''
    {
        letters%s {
            edges {
                node {
                    id
                    letter
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
    }
    ''' % args)


def check(args, letters, has_previous_page=False, has_next_page=False):
    result = execute(args)
    expected_edges = edges(letters)
    expected_page_info = {
        'hasPreviousPage': has_previous_page,
        'hasNextPage': has_next_page,
        'endCursor': expected_edges[-1]['cursor'] if expected_edges else None,
        'startCursor': expected_edges[0]['cursor'] if expected_edges else None
    }

    assert not result.errors
    assert result.data == {
        'letters': {
            'edges': expected_edges,
            'pageInfo': expected_page_info
        }
    }


def test_returns_all_elements_without_filters():
    check('', 'ABCDE')


def test_respects_a_smaller_first():
    check('first: 2', 'AB', has_next_page=True)


def test_respects_an_overly_large_first():
    check('first: 10', 'ABCDE')


def test_respects_a_smaller_last():
    check('last: 2', 'DE', has_previous_page=True)


def test_respects_an_overly_large_last():
    check('last: 10', 'ABCDE')


def test_respects_first_and_after():
    check('first: 2, after: "{}"'.format(cursor_for('B')), 'CD', has_next_page=True)


def test_respects_first_and_after_with_long_first():
    check('first: 10, after: "{}"'.format(cursor_for('B')), 'CDE')


def test_respects_last_and_before():
    check('last: 2, before: "{}"'.format(cursor_for('D')), 'BC', has_previous_page=True)


def test_respects_last_and_before_with_long_last():
    check('last: 10, before: "{}"'.format(cursor_for('D')), 'ABC')


def test_respects_first_and_after_and_before_too_few():
    check('first: 2, after: "{}", before: "{}"'.format(cursor_for('A'), cursor_for('E')), 'BC', has_next_page=True)


def test_respects_first_and_after_and_before_too_many():
    check('first: 4, after: "{}", before: "{}"'.format(cursor_for('A'), cursor_for('E')), 'BCD')


def test_respects_first_and_after_and_before_exactly_right():
    check('first: 3, after: "{}", before: "{}"'.format(cursor_for('A'), cursor_for('E')), "BCD")


def test_respects_last_and_after_and_before_too_few():
    check('last: 2, after: "{}", before: "{}"'.format(cursor_for('A'), cursor_for('E')), 'CD', has_previous_page=True)


def test_respects_last_and_after_and_before_too_many():
    check('last: 4, after: "{}", before: "{}"'.format(cursor_for('A'), cursor_for('E')), 'BCD')


def test_respects_last_and_after_and_before_exactly_right():
    check('last: 3, after: "{}", before: "{}"'.format(cursor_for('A'), cursor_for('E')), 'BCD')


def test_returns_no_elements_if_first_is_0():
    check('first: 0', '', has_next_page=True)


def test_returns_all_elements_if_cursors_are_invalid():
    check('before: "invalid" after: "invalid"', 'ABCDE')


def test_returns_all_elements_if_cursors_are_on_the_outside():
    check('before: "{}" after: "{}"'.format(base64('sc:%s' % 6), base64('sc:%s' % 0)), 'ABCDE')


def test_returns_no_elements_if_cursors_cross():
    check('before: "{}" after: "{}"'.format(base64('sc:%s' % 2), base64('sc:%s' % 4)), '')
