# reversi

A pure-Python reversi (Othello) library inspired by [python-chess](https://github.com/niklasf/python-chess).

It provides a full-featured `Board` class with legal move generation, push/pop move history,
FEN serialization, ASCII display, and SVG rendering with Jupyter notebook integration.

---

## Installation

The package is not yet on PyPI. Add the project root to your Python path:

```python
import sys
sys.path.insert(0, "/path/to/reversi")

import reversi
```

---

## Quick Start

```python
import reversi

board = reversi.Board()

# Print the ASCII board
print(board)

# List legal moves for the current player
print(list(board.legal_moves))   # [Move(c4), Move(d3), Move(e6), Move(f5)]

# Make a move
board.push(reversi.Move(reversi.C4))

# Undo the last move
board.pop()

# Check the score
black, white = board.score()
print(f"Black: {black}  White: {white}")   # Black: 2  White: 2

# Check game result
print(board.result())   # '*' while game is in progress
```

---

## Board

### Constructor

```python
board = reversi.Board(setup=True)
```

Creates an 8x8 board. When `setup=True` (the default), the four starting discs are placed at
d4, e4, d5, e5. Pass `setup=False` for a blank board.

### Properties

| Property     | Type                  | Description                                           |
|--------------|-----------------------|-------------------------------------------------------|
| `turn`       | `Color`               | The side to move: `BLACK` or `WHITE`                  |
| `legal_moves`| `LegalMoveGenerator`  | Legal moves for the current side (see below)          |
| `move_stack` | `list`                | History as `(Move, captured_squares, color)` tuples   |

### Legal Moves

`board.legal_moves` returns a `LegalMoveGenerator`. It supports iteration, `len()`, membership
testing with `in`, and boolean evaluation.

```python
gen = board.legal_moves

for move in gen:             # iterate
    print(move)

print(len(gen))              # number of legal moves

reversi.Move(reversi.C4) in gen   # True/False membership test

if gen:                      # True when any legal move exists
    board.push(next(iter(gen)))
```

### Move Stack

```python
board.push(move)    # Apply a move and add it to the stack. Raises ValueError for illegal moves.
board.pop()         # Undo the last move and return it. Raises IndexError on empty stack.
board.peek()        # Return the last move without removing it. Raises IndexError on empty stack.
```

A pass move (`Move.pass_move()`) can only be pushed when the current player has no legal moves.

### Has Legal Move

```python
board.has_legal_move()              # check for the side to move
board.has_legal_move(reversi.BLACK) # check for a specific color
board.has_legal_move(reversi.WHITE)
```

### Game State

```python
board.is_game_over()   # True when neither player has a legal move
board.outcome()        # Returns Outcome or None if game is not over
board.result()         # '1-0' (black wins), '0-1' (white wins), '1/2-1/2' (draw), '*' (in progress)
board.score()          # (black_count, white_count) as a tuple of ints
```

### Disc Access

```python
disc = board.disc_at(reversi.D4)          # Returns Disc or None
board.set_disc_at(reversi.D4, reversi.Disc(reversi.WHITE))  # Place or replace a disc
board.set_disc_at(reversi.D4, None)       # Remove a disc
```

### Copy

```python
board.copy()            # Full copy including entire move stack
board.copy(stack=True)  # Same as above
board.copy(stack=False) # Copy board position only, no history
board.copy(stack=5)     # Copy with only the last 5 moves in the stack
```

### Clear

```python
board.clear()   # Reset to an empty board, BLACK to move, empty move stack
```

### FEN Serialization

The FEN format uses `X` for black discs and `O` for white discs, with run-length encoding of
empty squares, rows separated by `/` from rank 8 to rank 1, followed by a space and `b` or `w`
for the side to move.

```python
fen = board.fen()          # e.g. '8/8/8/3OX3/3XO3/8/8/8 b'
board.set_fen(fen)         # Restore position from a FEN string
```

### String Representations

```python
str(board)    # ASCII board, rank 8 at top, X = black, O = white, . = empty
repr(board)   # Board(fen='...')
```

Example ASCII output:

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

### Jupyter Integration

`Board` objects implement `_repr_svg_()` and render automatically as a colored SVG board in
Jupyter notebooks. No extra code is needed — just evaluate `board` in a cell.

---

## Move

```python
reversi.Move(square)         # A move placing a disc on the given square
reversi.Move.pass_move()     # A pass (no placement)
reversi.Move.from_str("d3")  # Parse from string: "d3", "pass", "pa", or "--"
```

| Method / Attribute | Description                                          |
|--------------------|------------------------------------------------------|
| `move.square`      | The target `Square`, or `None` for a pass            |
| `move.is_pass()`   | `True` if the move is a pass                         |
| `str(move)`        | `"d3"` for a placement, `"--"` for a pass            |
| `repr(move)`       | `"Move(d3)"` or `"Move.pass_move()"`                 |
| `bool(move)`       | `False` if the move is a pass, `True` otherwise      |

---

## Disc

```python
disc = reversi.Disc(reversi.BLACK)
disc = reversi.Disc(reversi.WHITE)

disc.color       # reversi.BLACK or reversi.WHITE
disc.symbol()    # 'X' for black, 'O' for white
```

---

## Outcome and Termination

`Board.outcome()` returns an `Outcome` when the game is over, or `None` if it is still in
progress.

```python
outcome = board.outcome()

outcome.termination   # Termination.COMPLETED
outcome.winner        # BLACK, WHITE, or None (draw)
outcome.result()      # '1-0', '0-1', or '1/2-1/2'
```

`Termination` is an enum with a single member:

| Member                  | Meaning                                              |
|-------------------------|------------------------------------------------------|
| `Termination.COMPLETED` | Both players have no legal moves; the game is over   |

---

## Constants

### Colors

```python
reversi.BLACK   # True
reversi.WHITE   # False
reversi.COLOR_NAMES   # {True: 'black', False: 'white'}
```

### Squares

Squares are integers `0`–`63`. `A1` is `0`; squares advance left-to-right, then
bottom-to-top, so `H8` is `63`.

```python
reversi.A1  # 0
reversi.H8  # 63
reversi.SQUARES       # list of all 64 Square values
reversi.SQUARE_NAMES  # ['a1', 'b1', ..., 'h8']
```

### Square Utility Functions

| Function                    | Description                                             |
|-----------------------------|---------------------------------------------------------|
| `square_name(square)`       | Returns the name string, e.g. `square_name(A1) == 'a1'` |
| `square_file(square)`       | File index 0–7 (a=0, h=7)                               |
| `square_rank(square)`       | Rank index 0–7 (rank 1=0, rank 8=7)                     |
| `parse_square(name)`        | Converts `'d4'` → `Square`; raises `ValueError` on bad input |

---

## SVG Rendering

```python
reversi.svg.board(
    board,
    size=400,
    coordinates=True,
    lastmove=None,
    show_legal=False,
    colors=None,
)
```

Returns an SVG string. All parameters after `board` are keyword-only.

| Parameter     | Type             | Default   | Description                                         |
|---------------|------------------|-----------|-----------------------------------------------------|
| `board`       | `Board` or `None`| `None`    | The board to render; `None` renders an empty board  |
| `size`        | `int`            | `400`     | Width and height of the SVG in pixels               |
| `coordinates` | `bool`           | `True`    | Whether to draw file/rank labels around the board   |
| `lastmove`    | `Square` or `None` | `None`  | Square to highlight as the last move                |
| `show_legal`  | `bool`           | `False`   | Overlay dots for legal moves of the current player  |
| `colors`      | `dict` or `None` | `None`    | Override any default colors (partial dicts accepted)|

### Default Color Keys

| Key            | Default                    | Description                         |
|----------------|----------------------------|-------------------------------------|
| `board`        | `#2e8b57`                  | Board fill color                    |
| `grid`         | `#1a5c38`                  | Grid line color                     |
| `black_disc`   | `#1a1a1a`                  | Black disc fill                     |
| `white_disc`   | `#f0f0f0`                  | White disc fill                     |
| `black_stroke` | `#000000`                  | Black disc border                   |
| `white_stroke` | `#cccccc`                  | White disc border                   |
| `coords`       | `#f0f0f0`                  | Coordinate label color              |
| `lastmove`     | `rgba(255, 255, 0, 0.4)`   | Last-move highlight overlay         |
| `legal`        | `rgba(0, 0, 0, 0.15)`      | Legal-move dot color                |

Example — render with legal move hints and a custom board color:

```python
svg_str = reversi.svg.board(
    board,
    size=500,
    show_legal=True,
    lastmove=reversi.C4,
    colors={"board": "#1e6b40"},
)
```

---

## Jupyter Notebook

Boards render automatically in Jupyter by calling `_repr_svg_()` internally — just evaluate
the board object in a cell:

```python
import reversi

board = reversi.Board()
board   # displays the SVG board inline
```

For custom SVG output, use `IPython.display.SVG` together with `reversi.svg.board()`:

```python
from IPython.display import SVG

SVG(reversi.svg.board(board, size=600, show_legal=True, coordinates=False))
```

---

## Example: Playing a Game

```python
import random
import reversi

board = reversi.Board()

while not board.is_game_over():
    moves = list(board.legal_moves)
    if moves:
        move = random.choice(moves)
    else:
        move = reversi.Move.pass_move()

    print(f"{'Black' if board.turn == reversi.BLACK else 'White'} plays {move}")
    board.push(move)

print(board)
black, white = board.score()
print(f"\nFinal score — Black: {black}  White: {white}")
print(f"Result: {board.result()}")

outcome = board.outcome()
if outcome.winner is None:
    print("Draw!")
else:
    print(f"Winner: {reversi.COLOR_NAMES[outcome.winner]}")
```
