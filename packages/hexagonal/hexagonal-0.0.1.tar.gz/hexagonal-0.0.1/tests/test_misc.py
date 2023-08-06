from hypothesis import given, strategies as st

from hexagonal import DIRECTIONS, Vec

from . import veci


@given(veci())
def test_to_tuple(v):
    assert Vec(v.to_tuple()[0], v.to_tuple()[1]) == v


@given(veci())
def test_repr(v):
    assert eval(repr(v)) == v


@given(veci())
def test_invariant(v):
    assert v.x + v.y + v.z == 0


@given(veci())
def test_bool(v):
    assert bool(v) == (v != Vec(0, 0))


@given(st.integers())
def test_abs(n):
    assert all([abs(d * n) == abs(n) for d in DIRECTIONS])


@given(veci(), veci())
def test_cartesian_addition(u, v):
    assert (u + v).cartesian() == tuple(
        u.cartesian()[i] + v.cartesian()[i] for i in range(2)
    )
