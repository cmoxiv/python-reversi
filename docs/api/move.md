# Move

Represents a single move in a Reversi game — either a placement on a specific square or a pass.

```python
from reversi import Move, Square
```

---

## Class Signature

```python
class Move:
    def __init__(self, square: Optional[Square] = None) -> None
```

---

## Constructor

### `Move(square=None)`

Creates a new `Move` instance.

| Parameter | Type              | Default | Description                                           |
|-----------|-------------------|---------|-------------------------------------------------------|
| `square`  | `Optional[Square]` | `None`  | Target square for a placement move, or `None` to pass |

**Returns:** `Move`

```python
m = Move(Square.D3)   # placement move on d3
p = Move()            # pass move
```

---

## Class Methods

### `Move.pass_move() -> Move`

Creates a pass move. Equivalent to `Move()` but communicates intent explicitly.

**Returns:** `Move` with `square = None`

```python
p = Move.pass_move()
print(p.is_pass())  # True
```

---

### `Move.from_str(s: str) -> Move`

Parses a string and returns the corresponding `Move`. Input is case-insensitive.

**Parameters**

| Parameter | Type  | Description                                    |
|-----------|-------|------------------------------------------------|
| `s`       | `str` | Square notation (e.g. `"d3"`) or a pass alias |

**Pass aliases** — any of the following strings produce a pass move:

| Input    | Notes          |
|----------|----------------|
| `"pass"` | Full word      |
| `"pa"`   | Short form     |
| `"--"`   | Symbolic form  |

**Returns:** `Move`

**Raises:** `ValueError` — if `s` is not a valid square notation and is not a recognised pass alias.

```python
Move.from_str("d3")    # Move(d3)
Move.from_str("D3")    # Move(d3)  — case-insensitive
Move.from_str("pass")  # Move.pass_move()
Move.from_str("pa")    # Move.pass_move()
Move.from_str("--")    # Move.pass_move()

Move.from_str("zz")    # raises ValueError
```

---

## Instance Methods

### `is_pass() -> bool`

Returns `True` when this move is a pass (i.e. `square is None`), `False` for any placement move.

**Returns:** `bool`

```python
Move.pass_move().is_pass()   # True
Move(Square.D3).is_pass()    # False
```

---

## Special Methods

### `__str__() -> str`

Returns a human-readable string representation of the move.

| Move type | Output |
|-----------|--------|
| Placement | `"d3"` (lower-case square notation) |
| Pass      | `"--"` |

```python
str(Move(Square.D3))    # "d3"
str(Move.pass_move())   # "--"
```

---

### `__repr__() -> str`

Returns an unambiguous representation suitable for debugging.

| Move type | Output              |
|-----------|---------------------|
| Placement | `"Move(d3)"`        |
| Pass      | `"Move.pass_move()"` |

```python
repr(Move(Square.D3))    # "Move(d3)"
repr(Move.pass_move())   # "Move.pass_move()"
```

---

### `__eq__(other: object) -> bool`

Compares two moves for equality. Equality is determined solely by the `square` attribute — two moves are equal if and only if they reference the same square (or both are pass moves).

**Returns:** `bool`

```python
Move(Square.D3) == Move(Square.D3)   # True
Move(Square.D3) == Move(Square.E4)   # False
Move.pass_move() == Move()           # True
Move(Square.D3) == Move.pass_move()  # False
```

---

### `__hash__() -> int`

Returns `hash(self.square)`. Consistent with `__eq__`, so `Move` instances can be used in sets and as dictionary keys.

```python
seen = {Move(Square.D3), Move.pass_move()}
Move(Square.D3) in seen   # True
```

---

### `__bool__() -> bool`

Returns `False` for a pass move and `True` for any placement move. This mirrors the null-move pattern used in python-chess, where a "null" (pass) move is falsy.

| Move type | `bool(move)` |
|-----------|--------------|
| Pass      | `False`      |
| Placement | `True`       |

```python
if Move(Square.D3):
    print("placement move")   # printed

if not Move.pass_move():
    print("pass move")        # printed
```

---

## Attributes

| Attribute | Type               | Description                                      |
|-----------|--------------------|--------------------------------------------------|
| `square`  | `Optional[Square]` | Target square for placement, or `None` for pass  |

---

## Notes

- `from_str` is case-insensitive: `"D3"` and `"d3"` produce the same move.
- The three pass aliases (`"pass"`, `"pa"`, `"--"`) are all accepted by `from_str`; `"--"` is also the canonical `str()` output for a pass move.
- The bool behaviour (`pass → False`, `placement → True`) is intentional and mirrors the python-chess null-move convention, making guard clauses like `if move:` natural.
- Equality compares only `square`; no other state is considered.
