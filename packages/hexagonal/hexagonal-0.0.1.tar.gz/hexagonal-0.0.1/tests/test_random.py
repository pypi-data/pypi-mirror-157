from hypothesis import given, strategies as st

from hexagonal import random


@given(st.integers(min_value=0))
def test_random(r):
    assert abs(random(r)) <= r
