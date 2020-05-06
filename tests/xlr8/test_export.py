import pytest

from xlr8.export import _transform, depth, length


@pytest.mark.parametrize(
    'obj,expected',
    [(None, 0),
     ('Something', 0),
     ({'basic': 1}, 1),
     ({'basic': {'nested': 4}}, 2),
     ({'basic': {'nested': {'array': [1, 2, {'inside': 4}]}}}, 4)])
def test_depth(obj, expected):
    assert depth(obj) == expected


@pytest.mark.parametrize(
    'obj,expected',
    [({'name': 'John'}, 1),
     ({'lead': {'name': 'Josh',
                'birth': '15-08'}}, 2),
     ({'lead': {'name': 'Jock',
                'birth': '15-08',
                'address': {'street': 'sa',
                                      'city': 'ctba'}}}, 4),
     ({'lead': {'name': 'Ben',
                'phones': [{'number': '1', 'code': 2, 'f': 2},
                           {'number': '2', 'code': 3}]}}, 7),
     ({'lead': {'name': 'Ben',
                'phones': [{'number': '1', 'code': 2},
                           {'number': '2'}]}}, 5),
     (1, 1),
     ([1, 2, 3], 3),
     ([{'name': 'jonh', 'age': 32}, {}], 4)])
def test_length(obj, expected):
    assert length(obj) == expected


@pytest.mark.parametrize(
    'example,expected',
    [(None, 0),
     ({'basic': 1}, 1),
     ({'basic': {'nested': 4}}, 2),
     ({'basic': {'nested': {'array': [1, 2, {'inside': 4}]}}}, 4)])
def test_transform(example, expected):
    pass
