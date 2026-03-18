# Board

API reference for `LegalMoveGenerator` and `Board`, the two core classes in `reversi.core`.

Both classes mirror the design patterns established by
[python-chess](https://python-chess.readthedocs.io/): a `Board` holds the current position and
a `LegalMoveGenerator` provides lazy, iterable access to the legal moves in that position.

---

## Type Aliases

The following type aliases are used throughout this reference.

| Alias    | Underlying type                                 | Notes                                |
|----------|-------------------------------------------------|--------------------------------------|
| `Color`  | `bool`                                          | `BLACK = True`, `WHITE = False`      |
| `Square` | `int`                                           | `0` (a1) through `63` (h8)           |
| `Move`   | `Move`                                          | Class defined in `reversi.core`      |
| `Disc`   | `Disc`                                          | Class defined in `reversi.core`      |
| `Outcome`| `Outcome`                                       | Class defined in `reversi.core`      |

---

## LegalMoveGenerator

```python
class LegalMoveGenerator:
    def __init__(self, board: Board) -> None
```

A lazy generator of legal moves for a given board position. An instance is created fresh every
time `Board.legal_moves` is accessed, so it always reflects the current board state.

`LegalMoveGenerator` supports Python's standard collection protocol: iteration, membership
testing, length, and boolean evaluation. It does **not** cache results internally — each
protocol operation recomputes the legal move list from the board. For repeated queries on an
unchanged position, convert to a `list` once.

### Constructor

#### `__init__(board: Board) -> None`

Binds the generator to `board`. The generator holds a reference to the live board; changes to
the board are immediately reflected.

| Parameter | Type    | Description                                   |
|-----------|---------|-----------------------------------------------|
| `board`   | `Board` | The board whose legal moves will be generated |

---

### Protocol Methods

#### `__iter__() -> Iterator[Move]`

Iterates over all legal moves for `board.turn` in the current position. Moves are yielded in
board-square order (a1 to h8). Pass moves are **not** included — `LegalMoveGenerator` only
yields placement moves.

```python
board = Board()
for move in board.legal_moves:
    print(move)  # d3, c4, f5, e6
```

---

#### `__contains__(move: object) -> bool`

Tests whether `move` is a legal move in the current position. Non-`Move` objects always return
`False`.

| Parameter | Type     | Description          |
|-----------|----------|----------------------|
| `move`    | `object` | The move to test     |

Returns `True` if `move` is legal for `board.turn`, `False` otherwise.

```python
board = Board()
print(Move.from_str("d3") in board.legal_moves)  # True
print(Move.from_str("a1") in board.legal_moves)  # False
```

---

#### `__len__() -> int`

Returns the number of legal moves available to `board.turn`.

```python
board = Board()
print(len(board.legal_moves))  # 4
```

---

#### `__bool__() -> bool`

Returns `True` if there is at least one legal move for `board.turn`, `False` if the current
side has no legal placement move.

```python
board = Board()
if board.legal_moves:
    print("moves available")
```

---

#### `__repr__() -> str`

Returns a human-readable representation listing the current legal moves.

Format: `LegalMoveGenerator([d3, c4, f5, e6])`

```python
board = Board()
print(repr(board.legal_moves))  # LegalMoveGenerator([d3, c4, f5, e6])
```

---

## Board

```python
class Board:
    def __init__(self, setup: bool = True) -> None
```

An 8x8 reversi board. Holds the disc grid, the side to move, and the full move history. Provides
push/pop move execution, legal-move generation, game-state queries, FEN serialization, and
copy semantics.

The board uses algebraic square names (`a1`–`h8`), where `a1` is the bottom-left corner (rank 1,
file a) and `h8` is the top-right (rank 8, file h). Internally, squares are indexed `0`–`63`
in row-major order starting from a1.

---

### Constructor & Setup

#### `__init__(setup: bool = True) -> None`

Creates a new board.

| Parameter | Type   | Default | Description                                                      |
|-----------|--------|---------|------------------------------------------------------------------|
| `setup`   | `bool` | `True`  | If `True`, places the four standard opening discs and sets turn to `BLACK`. If `False`, the grid is empty and turn is `BLACK`. |

When `setup=True` the initial position is:

```
d4 = WHITE   e4 = BLACK
d5 = BLACK   e5 = WHITE
```

```python
board = Board()           # standard starting position
empty = Board(setup=False) # blank board, useful for set_fen()
```

---

#### `clear() -> None`

Resets the board to a fully empty state: all 64 squares become empty, `turn` is set to
`BLACK`, and `move_stack` is cleared.

This is equivalent to creating `Board(setup=False)` but modifies the instance in-place.

```python
board = Board()
board.clear()
print(board.score())  # (0, 0)
```

---

### Attributes

#### `turn: Color`

The side whose turn it is to move. Always either `BLACK` (`True`) or `WHITE` (`False`). Updated
automatically by `push()` and `pop()`.

```python
board = Board()
print(board.turn)  # True  (BLACK)
```

---

#### `move_stack: list[tuple[Move, list[Square], Color]]`

The full history of pushed moves. Each entry is a three-tuple:

| Index | Type            | Description                                          |
|-------|-----------------|------------------------------------------------------|
| `0`   | `Move`          | The move that was played                             |
| `1`   | `list[Square]`  | Squares of discs that were flipped by the move       |
| `2`   | `Color`         | The color that played the move                       |

For pass moves the flipped-squares list is always empty (`[]`).

Direct mutation of `move_stack` is possible but will leave the board in an inconsistent state.
Use `push()` and `pop()` for all normal move execution.

```python
board = Board()
board.push(Move.from_str("d3"))
move, flipped, color = board.move_stack[-1]
print(move, flipped, color)  # d3 [D4] True
```

---

#### `legal_moves: LegalMoveGenerator`  *(property)*

Returns a fresh `LegalMoveGenerator` for the current position and `board.turn`. Accessing this
property does not mutate the board.

```python
board = Board()
moves = list(board.legal_moves)  # [Move(d3), Move(c4), Move(f5), Move(e6)]
```

---

### Disc Access

#### `disc_at(square: Square) -> Optional[Disc]`

Returns the disc occupying `square`, or `None` if the square is empty.

| Parameter | Type     | Description              |
|-----------|----------|--------------------------|
| `square`  | `Square` | The square to inspect    |

Returns `Optional[Disc]` — a `Disc` instance if occupied, `None` if empty.

```python
board = Board()
print(board.disc_at(D4))  # Disc(white)
print(board.disc_at(A1))  # None
```

---

#### `set_disc_at(square: Square, disc: Optional[Disc]) -> None`

Places or removes a disc on `square` without performing legality checks or updating `turn`.
Passing `None` for `disc` clears the square.

This method bypasses all game rules and is intended for board setup, testing, and FEN loading.
It does **not** record anything in `move_stack`.

| Parameter | Type              | Description                                          |
|-----------|-------------------|------------------------------------------------------|
| `square`  | `Square`          | The target square                                    |
| `disc`    | `Optional[Disc]`  | The disc to place, or `None` to clear the square     |

```python
board = Board(setup=False)
board.set_disc_at(D4, Disc(WHITE))
board.set_disc_at(E4, Disc(BLACK))
```

---

### Move Generation

#### `has_legal_move(color: Optional[Color] = None) -> bool`

Returns `True` if `color` has at least one legal placement move in the current position.

| Parameter | Type               | Default | Description                                              |
|-----------|--------------------|---------|----------------------------------------------------------|
| `color`   | `Optional[Color]`  | `None`  | The color to check. If `None`, defaults to `board.turn`. |

Returns `bool`.

This is equivalent to `bool(board.legal_moves)` when `color` is `None`, but allows checking
either color independently (useful for game-over detection).

```python
board = Board()
print(board.has_legal_move())       # True  (checks board.turn)
print(board.has_legal_move(WHITE))  # True
print(board.has_legal_move(BLACK))  # True
```

---

### Push/Pop

#### `push(move: Move) -> None`

Applies `move` to the board, updating the grid, flipping captured discs, recording the move in
`move_stack`, and toggling `turn`.

**Pass moves:** A pass (`Move.pass_move()`) is only legal when the current side has no legal
placement move. Attempting to pass when placement moves exist raises `ValueError`.

**Placement moves:** A placement move is legal when the target square is empty and placing there
would flip at least one opponent disc. Attempting to place on an occupied square or on a square
that captures nothing raises `ValueError`.

| Parameter | Type   | Description       |
|-----------|--------|-------------------|
| `move`    | `Move` | The move to apply |

Raises `ValueError` with a descriptive message in the following cases:

| Condition                                                    | Message                                          |
|--------------------------------------------------------------|--------------------------------------------------|
| Pass attempted while legal placement moves exist             | `"cannot pass when legal moves are available"`   |
| Placement on an occupied square                              | `"square <name> is occupied"`                    |
| Placement that captures no opponent discs                    | `"<move> is not a legal move"`                   |

```python
board = Board()
board.push(Move.from_str("d3"))
print(board.turn)  # False  (WHITE to move)
```

---

#### `pop() -> Move`

Reverses the last move: removes the placed disc, restores all flipped discs to their previous
color, and restores `turn` to the color that played the move.

Returns the `Move` that was reversed.

Raises `IndexError` with message `"pop from empty move stack"` if `move_stack` is empty.

```python
board = Board()
board.push(Move.from_str("d3"))
move = board.pop()
print(move)        # d3
print(board.turn)  # True  (BLACK again)
```

---

#### `peek() -> Move`

Returns the last move played without reversing it. Does not modify the board.

Returns the `Move` at the top of `move_stack`.

Raises `IndexError` with message `"peek on empty move stack"` if `move_stack` is empty.

```python
board = Board()
board.push(Move.from_str("d3"))
print(board.peek())  # Move(d3)
```

---

### Game State

#### `is_game_over() -> bool`

Returns `True` if the game is over, i.e. neither `BLACK` nor `WHITE` has any legal placement
move. Returns `False` if at least one side can still move.

```python
board = Board()
print(board.is_game_over())  # False
```

---

#### `outcome() -> Optional[Outcome]`

Returns an `Outcome` object describing the result of a finished game, or `None` if the game is
still in progress.

Returns `Optional[Outcome]`:

- `None` — game is not over yet
- `Outcome(termination=Termination.COMPLETED, winner=BLACK)` — black wins
- `Outcome(termination=Termination.COMPLETED, winner=WHITE)` — white wins
- `Outcome(termination=Termination.COMPLETED, winner=None)` — draw (equal disc counts)

```python
if board.is_game_over():
    o = board.outcome()
    print(o.result())  # "1-0", "0-1", or "1/2-1/2"
```

---

#### `result() -> str`

Returns a result string for the current position.

| Return value  | Meaning                              |
|---------------|--------------------------------------|
| `"1-0"`       | Black wins                           |
| `"0-1"`       | White wins                           |
| `"1/2-1/2"`   | Draw (equal disc counts at game end) |
| `"*"`         | Game is still in progress            |

```python
board = Board()
print(board.result())  # "*"
```

---

#### `score() -> tuple[int, int]`

Returns the current disc counts as `(black_count, white_count)`.

Returns `tuple[int, int]` — a two-element tuple where index 0 is the number of black discs and
index 1 is the number of white discs currently on the board.

```python
board = Board()
print(board.score())  # (2, 2)
```

---

### Copy

#### `copy(*, stack: Union[bool, int] = True) -> Board`

Returns a deep copy of the board. The `stack` keyword argument controls how much of the move
history is copied.

| Parameter | Type              | Default | Description                                                      |
|-----------|-------------------|---------|------------------------------------------------------------------|
| `stack`   | `Union[bool, int]`| `True`  | Controls move history copying (see table below)                  |

`stack` behavior:

| Value          | Effect                                                          |
|----------------|-----------------------------------------------------------------|
| `True`         | Full move history is copied                                     |
| `False`        | Move history is not copied; the copy starts with an empty stack |
| `int` (n >= 0) | Only the last `n` entries of the move history are copied        |

The grid and `turn` are always fully copied regardless of `stack`.

```python
original = Board()
original.push(Move.from_str("d3"))

full_copy  = original.copy()             # includes full move_stack
clean_copy = original.copy(stack=False)  # no move history
tail_copy  = original.copy(stack=2)      # last 2 moves only
```

---

### Serialization

#### `fen() -> str`

Returns a FEN-like string representing the current board position.

The format is:

```
<rows> <side>
```

- `<rows>`: eight row strings joined by `/`, from rank 8 down to rank 1. Each row encodes
  squares left-to-right (a to h). Empty runs are represented as a decimal digit; `X` denotes a
  black disc; `O` denotes a white disc.
- `<side>`: `b` for Black to move, `w` for White to move.

```python
board = Board()
print(board.fen())  # "8/8/8/3XO3/3OX3/8/8/8 b"
```

---

#### `set_fen(fen: str) -> None`

Parses `fen` and restores the board to the encoded position. Clears the grid and `move_stack`
before applying the new position.

| Parameter | Type  | Description                         |
|-----------|-------|-------------------------------------|
| `fen`     | `str` | A FEN string produced by `fen()`    |

Raises `ValueError` in the following cases:

| Condition                                          | Example message                                  |
|----------------------------------------------------|--------------------------------------------------|
| Wrong number of space-separated parts              | `"invalid FEN: '...'"` (not exactly 2 parts)    |
| Wrong number of rank rows                          | `"invalid FEN: expected 8 rows, got N"`          |
| Unrecognised character in a row                    | `"invalid FEN character: '?'"`                   |

```python
board = Board(setup=False)
board.set_fen("8/8/8/3XO3/3OX3/8/8/8 b")
print(board.score())  # (2, 2)
```

---

### Display

#### `__str__() -> str`

Returns a multi-line ASCII representation of the board, with rank numbers on the left and file
letters along the bottom. Black discs are shown as `X`, white discs as `O`, and empty squares
as `.`.

```python
board = Board()
print(str(board))
# 8 . . . . . . . .
# 7 . . . . . . . .
# 6 . . . . . . . .
# 5 . . . O X . . .
# 4 . . . X O . . .
# 3 . . . . . . . .
# 2 . . . . . . . .
# 1 . . . . . . . .
#   a b c d e f g h
```

---

#### `__repr__() -> str`

Returns a string that can reconstruct the board's current position.

Format: `Board(fen='<fen_string>')`

```python
board = Board()
print(repr(board))  # Board(fen='8/8/8/3XO3/3OX3/8/8/8 b')
```

---

#### `_repr_svg_() -> str`

Returns an SVG string rendering of the board, used automatically by Jupyter notebooks when a
`Board` is the last expression in a cell. Delegates to `reversi.svg.board()`.

This method is part of the IPython display protocol and is not intended to be called directly.

---

### Comparison

#### `__eq__(other: object) -> bool`

Two boards are equal if and only if they have the same disc configuration on all 64 squares
**and** the same `turn`. The `move_stack` is **not** considered.

Returns `NotImplemented` if `other` is not a `Board` instance, allowing Python to try the
reflected comparison.

```python
a = Board()
b = Board()
print(a == b)  # True

b.push(Move.from_str("d3"))
b.pop()
print(a == b)  # True  (same grid and turn, move_stack differs but is ignored)
```

---

#### `__hash__() -> int`

Returns `hash(self.fen())`. Two boards that compare equal via `__eq__` will always produce
the same hash value, satisfying the Python hash contract.

Boards are hashable and may be used as dictionary keys or stored in sets.

```python
seen = set()
board = Board()
seen.add(board)
print(board in seen)  # True
```
