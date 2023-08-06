"""
Hexagon provides classes for dealing with hexagonal grids.

Vec is an integer hexagonal vector, VecF is a floating one, and Grid is
a hexagonal grid indexed by Vecs.
"""
from __future__ import annotations

from random import randint
from typing import Generic, NoReturn, TypeVar

__version__ = "0.0.1"

def random(radius: int) -> Vec[int]:
    """Get a random Vec with at most a given radius."""
    while True:
        pos = Vec(randint(-radius, radius), randint(-radius, radius))
        if abs(pos) <= radius:
            return pos


N = TypeVar("N", float, int)


class Vec(Generic[N]):
    """A hexagonal vector."""

    __slots__ = ("x", "y")
    x: N
    y: N

    def __init__(self, x: N, y: N) -> None:
        object.__setattr__(self, "x", x)
        object.__setattr__(self, "y", y)

    @property
    def z(self) -> N:
        return -self.x - self.y

    def __setattr__(self, *_) -> NoReturn:
        raise TypeError(f"{self.__class__.__qualname__} is immutable")

    def __eq__(self, other: object, /) -> bool:
        return isinstance(other, Vec) and self.x == other.x and self.y == other.y

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __add__(self, other: Vec[N], /) -> Vec[N]:
        return Vec(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vec[N]) -> Vec[N]:
        return Vec(self.x - other.x, self.y - other.y)

    def __neg__(self) -> Vec[N]:
        return Vec(-self.x, -self.y)

    def __mul__(self, scalar: N) -> Vec[N]:
        return Vec(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar: float) -> Vec[float]:
        return Vec(self.x / scalar, self.y / scalar)

    def __str__(self) -> str:
        return f"({self.x} {self.y} {self.z})"

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}({self.x}, {self.y})"

    def __bool__(self) -> bool:
        return self.x != 0 or self.y != 0

    def __abs__(self) -> N:
        return max(abs(a) for a in self.to_tuple())

    def cartesian(self, size: float = 1) -> tuple[float, float]:
        return (size * (self.x - self.y), size * 2 * self.z)

    def to_tuple(self) -> tuple[N, N, N]:
        return (self.x, self.y, self.z)


T = TypeVar("T")


class Grid(Generic[T]):
    """A hexagonal grid."""

    def __init__(self, radius: int, fill: T) -> None:
        self.radius = radius
        self.grid: list[list[T]] = []
        self.positions: list[Vec[int]] = []
        for x in range(-radius, radius + 1):
            y_count = 2 * radius + 1 - abs(x)
            self.grid.append([fill for _ in range(y_count)])
            for y in range(-radius, radius + 1):
                pos = Vec(x, y)
                if abs(pos) <= radius:
                    self.positions.append(pos)

    def __getitem__(self, position: Vec[int]) -> T:
        return self.grid[position.x + self.radius][
            position.y + min(position.x, 0) + self.radius
        ]

    def __setitem__(self, position: Vec[int], value: T) -> None:
        self.grid[position.x + self.radius][
            position.y + min(position.x, 0) + self.radius
        ] = value

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__qualname__} radius={self.radius} grid={self.grid!r}>"
        )


DIRECTIONS = (
    EA := Vec(1, -1),
    NE := Vec(1, 0),
    NW := Vec(0, 1),
    WE := Vec(-1, 1),
    SW := Vec(-1, 0),
    SE := Vec(0, -1),
)

DIRECTION_NAMES = ("ea", "ne", "nw", "we", "sw", "se")
