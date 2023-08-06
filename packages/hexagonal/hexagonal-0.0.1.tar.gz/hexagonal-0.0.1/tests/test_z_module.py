from hypothesis import given, strategies as st

from hexagonal import Vec

from . import veci


class TestAbelianGroup:
    @given(veci(), veci(), veci())
    def test_associativity(self, u, v, w):
        assert (u + v) + w == u + (v + w)

    @given(veci())
    def test_identity(self, v):
        assert Vec(0, 0) + v == v + Vec(0, 0) == v

    @given(veci())
    def test_inverses(self, v):
        assert -v + v == v + -v == Vec(0, 0)
        assert --v == v

    @given(veci(), veci())
    def test_commutativity(self, u, v):
        assert u + v == v + u


@given(veci())
def test_multiplicative_identity(v):
    assert v * 1 == v


@given(st.integers(), st.integers(), veci(), veci())
def test_distributativity(x, y, u, v):
    assert (u + v) * x == u * x + v * x
    assert v * (x + y) == v * x + v * y


@given(st.integers(), st.integers(), veci())
def test_associativity(x, y, v):
    assert (v * x) * y == v * (x * y)
