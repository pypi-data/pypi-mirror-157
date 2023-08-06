from hypothesis import given

from hexagonal import DIRECTIONS

from . import veci


@given(veci())
def test_symmetry(v):
    assert v == v


@given(veci(), veci())
def test_commutativity(u, v):
    assert (u == v) == (v == u)


@given(veci(), veci(), veci())
def test_transitivity(u, v, w):
    if u == v and v == w:
        assert u == w


@given(veci())
def test_offset_not_equal(v):
    assert all(v != v + d for d in DIRECTIONS)
