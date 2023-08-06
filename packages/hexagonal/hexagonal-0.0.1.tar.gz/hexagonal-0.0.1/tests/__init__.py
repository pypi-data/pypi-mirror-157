from hypothesis import strategies as st

from hexagonal import Grid, Vec


@st.composite
def veci(draw, x=st.integers(), y=st.integers()) -> Vec[int]:
    return Vec(draw(x), draw(y))


@st.composite
def grid(draw, r=st.integers(min_value=0, max_value=20)) -> Grid[int]:
    return Grid(draw(r), 0)
