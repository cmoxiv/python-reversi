# Constants and Utilities

API reference for type aliases, board constants, and utility functions.

---

## Type Aliases

| Alias    | Underlying Type | Description                                      |
|----------|-----------------|--------------------------------------------------|
| `Color`  | `bool`          | Represents a player color: `True` or `False`     |
| `Square` | `int`           | Represents a board square by index: `0`–`63`     |

These are not distinct classes — they are plain `bool` and `int` values annotated with aliases
for clarity. Any `bool` is a valid `Color`; any `int` in range `0`–`63` is a valid `Square`.

---

## Colors

### Constants

| Name          | Value   | Description            |
|---------------|---------|------------------------|
| `BLACK`       | `True`  | The black player       |
| `WHITE`       | `False` | The white player       |

### `COLOR_NAMES`

```python
COLOR_NAMES: dict[Color, str]
```

Maps each color constant to its lowercase display name.

| Key     | Value     |
|---------|-----------|
| `BLACK` | `"black"` |
| `WHITE` | `"white"` |

**Usage**

```python
COLOR_NAMES[BLACK]  # "black"
COLOR_NAMES[WHITE]  # "white"
```

### Flipping Colors

Because `BLACK` and `WHITE` are plain booleans, the built-in `not` operator flips between them:

```python
not BLACK  # False == WHITE
not WHITE  # True  == BLACK
```

This is the idiomatic way to switch the active player.

---

## Squares

### Numbering Scheme

Squares are numbered **file-first, then rank** — that is, all eight squares of rank 1 come
before any square of rank 2:

```
a1=0,  b1=1,  c1=2,  d1=3,  e1=4,  f1=5,  g1=6,  h1=7
a2=8,  b2=9,  c2=10, d2=11, e2=12, f2=13, g2=14, h2=15
...
a8=56, b8=57, c8=58, d8=59, e8=60, f8=61, g8=62, h8=63
```

The general formula is: `square = rank_index * 8 + file_index`
where `file_index` is `0` for file `a` through `7` for file `h`, and `rank_index` is `0` for
rank `1` through `7` for rank `8`.

### Named Square Constants

All 64 squares are available as module-level constants. Each constant name is the algebraic
coordinate in uppercase (e.g., `A1`, `D4`, `H8`).

| File a | File b | File c | File d | File e | File f | File g | File h |
|--------|--------|--------|--------|--------|--------|--------|--------|
| A1 = 0  | B1 = 1  | C1 = 2  | D1 = 3  | E1 = 4  | F1 = 5  | G1 = 6  | H1 = 7  |
| A2 = 8  | B2 = 9  | C2 = 10 | D2 = 11 | E2 = 12 | F2 = 13 | G2 = 14 | H2 = 15 |
| A3 = 16 | B3 = 17 | C3 = 18 | D3 = 19 | E3 = 20 | F3 = 21 | G3 = 22 | H3 = 23 |
| A4 = 24 | B4 = 25 | C4 = 26 | D4 = 27 | E4 = 28 | F4 = 29 | G4 = 30 | H4 = 31 |
| A5 = 32 | B5 = 33 | C5 = 34 | D5 = 35 | E5 = 36 | F5 = 37 | G5 = 38 | H5 = 39 |
| A6 = 40 | B6 = 41 | C6 = 42 | D6 = 43 | E6 = 44 | F6 = 45 | G6 = 46 | H6 = 47 |
| A7 = 48 | B7 = 49 | C7 = 50 | D7 = 51 | E7 = 52 | F7 = 53 | G7 = 54 | H7 = 55 |
| A8 = 56 | B8 = 57 | C8 = 58 | D8 = 59 | E8 = 60 | F8 = 61 | G8 = 62 | H8 = 63 |

### `SQUARES`

```python
SQUARES: list[Square]
```

A list of all 64 square indices in ascending order, equivalent to `list(range(64))`.
Ordered file-first: `[A1, B1, C1, D1, E1, F1, G1, H1, A2, B2, ..., H8]`.

### `SQUARE_NAMES`

```python
SQUARE_NAMES: list[str]
```

A list of all 64 square names as lowercase algebraic strings, parallel to `SQUARES`.
`SQUARE_NAMES[i]` is the name of square `i`.

```python
SQUARE_NAMES[0]   # "a1"
SQUARE_NAMES[27]  # "d4"
SQUARE_NAMES[63]  # "h8"
```

### `FILE_NAMES`

```python
FILE_NAMES: str  # "abcdefgh"
```

A string of the eight file letters in board order. `FILE_NAMES[file_index]` gives the letter
for a given file index (0–7).

### `RANK_NAMES`

```python
RANK_NAMES: str  # "12345678"
```

A string of the eight rank digits in board order. `RANK_NAMES[rank_index]` gives the digit
for a given rank index (0–7).

---

## Utility Functions

### `square_name`

```python
def square_name(square: Square) -> str
```

Returns the lowercase algebraic name of a square.

**Parameters**

| Parameter | Type     | Description                         |
|-----------|----------|-------------------------------------|
| `square`  | `Square` | A square index in the range `0`–`63` |

**Returns** — `str`: The two-character algebraic name, e.g. `"a1"`, `"d4"`, `"h8"`.

**Example**

```python
square_name(0)   # "a1"
square_name(27)  # "d4"
square_name(63)  # "h8"
```

---

### `square_file`

```python
def square_file(square: Square) -> int
```

Returns the file index (column) of a square.

**Parameters**

| Parameter | Type     | Description                          |
|-----------|----------|--------------------------------------|
| `square`  | `Square` | A square index in the range `0`–`63` |

**Returns** — `int`: File index in the range `0`–`7`, where `0` is file `a` and `7` is file `h`.

**Example**

```python
square_file(0)   # 0  (file a)
square_file(7)   # 7  (file h)
square_file(27)  # 3  (file d)
```

---

### `square_rank`

```python
def square_rank(square: Square) -> int
```

Returns the rank index (row) of a square.

**Parameters**

| Parameter | Type     | Description                          |
|-----------|----------|--------------------------------------|
| `square`  | `Square` | A square index in the range `0`–`63` |

**Returns** — `int`: Rank index in the range `0`–`7`, where `0` is rank `1` and `7` is rank `8`.

**Example**

```python
square_rank(0)   # 0  (rank 1)
square_rank(56)  # 7  (rank 8)
square_rank(27)  # 3  (rank 4)
```

---

### `parse_square`

```python
def parse_square(name: str) -> Square
```

Parses a lowercase algebraic square name and returns the corresponding square index.

**Parameters**

| Parameter | Type  | Description                                                   |
|-----------|-------|---------------------------------------------------------------|
| `name`    | `str` | A two-character algebraic name such as `"a1"`, `"d4"`, `"h8"` |

**Returns** — `Square`: The square index (`int`) in the range `0`–`63`.

**Raises**

| Exception    | Condition                                                |
|--------------|----------------------------------------------------------|
| `ValueError` | The name is not a valid algebraic square (e.g. `"z9"`)  |

**Example**

```python
parse_square("a1")  # 0
parse_square("d4")  # 27
parse_square("h8")  # 63

parse_square("z9")  # raises ValueError
```
