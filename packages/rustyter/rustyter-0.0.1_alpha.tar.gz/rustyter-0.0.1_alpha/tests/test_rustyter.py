import pytest
from itertools import tee

import rustyter


ITERABLES = [
    list(range(10)),
    list(),
    [0],
    [1, 2, 3, 4],
    [-1, -2.0, "a"],
    list(x ** 2 for x in range(15)),
]


@pytest.mark.parametrize("it", ITERABLES)
def test_sum_as_string(it):
    it1, it2 = tee(it)
    got = rustyter.It(it1)
    expected = it2

    assert all(a == b for a, b in zip(got, expected))


@pytest.mark.parametrize("it", ITERABLES)
def test_count(it):
    it1, it2 = tee(it)
    got = rustyter.It(it1).count()
    expected = len(list(it2))

    assert got == expected
