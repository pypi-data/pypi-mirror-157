from hypothesis import given

from . import grid, veci


@given(grid(), veci())
def test_fill(g, v):
    if abs(v) > g.radius:
        return
    assert g[v] == 0


@given(grid(), veci())
def test_store_load(g, v):
    if abs(v) > g.radius:
        return
    g[v] = 1
    assert g[v] == 1
