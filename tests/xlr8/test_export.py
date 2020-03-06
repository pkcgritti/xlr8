import pytest

from xlr8.export import _get_depth, _transform


@pytest.mark.parametrize(
    'example,expected',
    [(None, 0),
     ({'basic': 1}, 1),
     ({'basic': {'nested': 4}}, 2),
     ({'basic': {'nested': {'array': [1, 2, {'inside': 4}]}}}, 4)])
def test_get_depth(example, expected):
    assert _get_depth(example) == expected


@pytest.mark.parametrize(
    'example,expected',
    [(None, 0),
     ({'basic': 1}, 1),
     ({'basic': {'nested': 4}}, 2),
     ({'basic': {'nested': {'array': [1, 2, {'inside': 4}]}}}, 4)])
def test_transform():
    pass
