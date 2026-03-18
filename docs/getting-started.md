# Getting Started

## Installation

The library is pure Python with no external dependencies. It is not yet published on PyPI,
so add the project root to `sys.path` before importing.

```python
import sys
sys.path.insert(0, "/path/to/reversi")  # adjust to your checkout location

import reversi
```

---

## Quick Start

### Creating a Board

`reversi.Board()` sets up the standard opening position: two black discs and two white
discs placed in the centre. Black (`X`) moves first.

```python
import reversi

board = reversi.Board()
print(board)
```

Output:

```
8 . . . . . . . .
7 . . . . . . . .
6 . . . . . . . .
5 . . . X O . . .
4 . . . O X . . .
3 . . . . . . . .
2 . . . . . . . .
1 . . . . . . . .
  a b c d e f g h
```

`X` represents black discs and `O` represents white discs.

---

### Listing Legal Moves

`Board.legal_moves` returns a `LegalMoveGenerator`. It supports iteration, `len()`,
and `in` membership tests without generating the full list unnecessarily.

```python
board = reversi.Board()

# Iterate
for move in board.legal_moves:
    print(move)          # d3, c4, f5, e6

# Count
print(len(board.legal_moves))   # 4

# Membership test
print(reversi.Move.from_str("d3") in board.legal_moves)  # True
print(reversi.Move.from_str("a1") in board.legal_moves)  # False
```

---

### Making Moves

Create a `Move` from a square constant or from a string, then call `Board.push()`.

```python
board = reversi.Board()

# From a square constant
move = reversi.Move(reversi.D3)

# Equivalently, from a string
move = reversi.Move.from_str("d3")

board.push(move)

black, white = board.score()
print(black, white)   # 4 1
print(board.turn == reversi.WHITE)  # True — it is now White's turn
```

`Board.push()` places the disc, flips all captured opponent discs, and advances
`Board.turn` to the other player.

---

### Undoing Moves

`Board.pop()` removes the last move from the stack and fully restores the board,
including flipped discs and the turn indicator.

```python
board = reversi.Board()
board.push(reversi.Move.from_str("d3"))

print(board.score())   # (4, 1)

board.pop()

print(board.score())   # (2, 2)  — restored to starting position
print(board == reversi.Board())  # True
```

---

### Pass Moves

A player must pass when they have no legal moves but the opponent does. Create a pass
move with `Move.pass_move()`. Attempting to pass when legal moves exist raises a
`ValueError`.

```python
# Construct a position where Black has no legal moves
board = reversi.Board()

if not board.has_legal_move():
    board.push(reversi.Move.pass_move())

# String representation of a pass move
print(str(reversi.Move.pass_move()))    # --
print(bool(reversi.Move.pass_move()))   # False
```

---

### Checking Game State

```python
board = reversi.Board()

# Game in progress
print(board.is_game_over())  # False
print(board.result())        # *

# Play through to the end (example: manually set a finished position)
finished = reversi.Board(setup=False)
for sq in reversi.SQUARES:
    finished.set_disc_at(sq, reversi.Disc(reversi.BLACK))
finished.set_disc_at(reversi.A1, reversi.Disc(reversi.WHITE))

print(finished.is_game_over())    # True

outcome = finished.outcome()
print(outcome.winner == reversi.BLACK)                    # True
print(outcome.termination)                                # Termination.COMPLETED
print(outcome.result())                                   # 1-0
print(finished.result())                                  # 1-0

black, white = finished.score()
print(black, white)                                       # 63 1
```

`result()` returns `"1-0"` (black wins), `"0-1"` (white wins), `"1/2-1/2"` (draw),
or `"*"` when the game is still in progress.

---

### FEN Serialization

The board supports a compact FEN-like string. Rows run from rank 8 to rank 1,
separated by `/`. Empty squares are run-length encoded as digits. `X` = black,
`O` = white. A trailing ` b` or ` w` indicates the side to move.

```python
board = reversi.Board()

fen = board.fen()
print(fen)   # 8/8/8/3XO3/3OX3/8/8/8 b

# Round-trip
board2 = reversi.Board(setup=False)
board2.set_fen(fen)

print(board2.fen() == fen)   # True
print(board2 == board)       # True
```

`set_fen()` clears the move stack. Use `Board.copy()` beforehand if you need to
preserve undo history.

---

### Board Copy

`Board.copy()` returns an independent copy of the board. The `stack` keyword
controls how much of the move history is included.

```python
board = reversi.Board()
board.push(reversi.Move.from_str("d3"))

# stack=True (default) — copy the full move history
full_copy = board.copy(stack=True)
print(len(full_copy.move_stack))   # 1

# stack=False — position only, no history
lean_copy = board.copy(stack=False)
print(len(lean_copy.move_stack))   # 0

# stack=N — copy only the last N entries
partial_copy = board.copy(stack=1)
print(len(partial_copy.move_stack))  # 1

# Copies are fully independent
lean_copy.push(reversi.Move.from_str("c4"))
print(board == lean_copy)  # False
```

---

### SVG Rendering

#### Jupyter Notebooks

Jupyter calls `_repr_svg_()` automatically, so just evaluate the board in a cell:

```python
board  # displays an SVG board inline
```

#### Custom rendering with `reversi.svg.board()`

Use `reversi.svg.board()` directly for full control. Display it with
`IPython.display.SVG` outside of the automatic repr path.

```python
from IPython.display import SVG, display

board = reversi.Board()
board.push(reversi.Move.from_str("d3"))

svg_str = reversi.svg.board(
    board,
    size=500,             # pixel dimensions (default: 400)
    coordinates=True,     # show rank/file labels (default: True)
    lastmove=reversi.D3,  # highlight the last played square
    show_legal=True,      # overlay legal-move markers
    colors={              # override any default color
        "board": "#2e8b57",
        "black_disc": "#1a1a1a",
        "white_disc": "#f0f0f0",
    },
)

display(SVG(svg_str))
```

All `colors` keys and their defaults:

| Key            | Default                  | Description                    |
|----------------|--------------------------|--------------------------------|
| `board`        | `#2e8b57`                | Board background fill          |
| `grid`         | `#1a5c38`                | Grid line colour               |
| `black_disc`   | `#1a1a1a`                | Black disc fill                |
| `white_disc`   | `#f0f0f0`                | White disc fill                |
| `black_stroke` | `#000000`                | Black disc border              |
| `white_stroke` | `#cccccc`                | White disc border              |
| `coords`       | `#f0f0f0`                | Rank/file label colour         |
| `lastmove`     | `rgba(255, 255, 0, 0.4)` | Last-move highlight overlay    |
| `legal`        | `rgba(0, 0, 0, 0.15)`    | Legal-move dot fill            |
