# Disc

A simple value type representing a game piece placed on the board. Each `Disc`
holds a single `Color` and is considered equal to any other `Disc` that holds
the same color.

```python
from reversi import Disc, BLACK, WHITE
```

---

## Constructor

```python
Disc(color: Color) -> None
```

| Parameter | Type    | Description                        |
|-----------|---------|------------------------------------|
| `color`   | `Color` | The side this disc belongs to — `BLACK` (`True`) or `WHITE` (`False`). |

**Example**

```python
black_disc = Disc(BLACK)
white_disc = Disc(WHITE)
```

---

## Attributes

| Attribute | Type    | Description                           |
|-----------|---------|---------------------------------------|
| `color`   | `Color` | The color assigned at construction.   |

---

## Methods

### `symbol`

```python
def symbol(self) -> str
```

Returns the single-character board symbol for this disc.

| Color   | Return value |
|---------|--------------|
| `BLACK` | `"X"`        |
| `WHITE` | `"O"`        |

**Example**

```python
>>> Disc(BLACK).symbol()
'X'
>>> Disc(WHITE).symbol()
'O'
```

---

### `__repr__`

```python
def __repr__(self) -> str
```

Returns an unambiguous string representation of the disc, suitable for
debugging.

| Color   | Return value    |
|---------|-----------------|
| `BLACK` | `"Disc(black)"` |
| `WHITE` | `"Disc(white)"` |

**Example**

```python
>>> repr(Disc(BLACK))
'Disc(black)'
```

---

### `__eq__`

```python
def __eq__(self, other: object) -> bool
```

Two `Disc` instances are equal if and only if they have the same `color`. A
`Disc` compared against any non-`Disc` object returns `False`.

**Example**

```python
>>> Disc(BLACK) == Disc(BLACK)
True
>>> Disc(BLACK) == Disc(WHITE)
False
```

---

### `__hash__`

```python
def __hash__(self) -> int
```

Returns `hash(self.color)`. Consistent with `__eq__`, so `Disc` instances can
be used safely in sets and as dictionary keys.

**Example**

```python
>>> len({Disc(BLACK), Disc(BLACK), Disc(WHITE)})
2
```
