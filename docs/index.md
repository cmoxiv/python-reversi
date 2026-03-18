# reversi

A pure-Python reversi (Othello) library inspired by python-chess.

`reversi` provides a clean, programmatic interface for working with Reversi (Othello) boards in
Python. It handles the full rules of the game — legal move generation, disc flipping, pass
detection, and game-over conditions — so you can focus on writing players, solvers, and
analysis tools. The library ships with FEN serialization, a push/pop move stack, ASCII display,
and SVG rendering with first-class Jupyter notebook support.

## Features

- Legal move generation via an iterable `LegalMoveGenerator`
- Push and pop moves with a full board history stack
- FEN serialization for saving and restoring board positions
- ASCII board display for quick inspection in terminals and tests
- SVG rendering with automatic Jupyter notebook integration
- `BLACK` (`X`) and `WHITE` (`O`) color constants; BLACK always moves first

## At a Glance

```python
import reversi

board = reversi.Board()

# List all legal moves for the side to move
moves = list(board.legal_moves)
print(moves)  # [Move(c4), Move(d3), Move(e6), Move(f5)]

# Push a move onto the board
board.push(reversi.Move.from_str("c4"))

# Display the board in ASCII
print(board)
```

Example ASCII output (BLACK = `X`, WHITE = `O`):

```
  a b c d e f g h
1 . . . . . . . .
2 . . . . . . . .
3 . . . . . . . .
4 . . X X X . . .
5 . . . X O . . .
6 . . . . . . . .
7 . . . . . . . .
8 . . . . . . . .
Turn: white
```

> **Note:** `BLACK` is represented as `X` and `WHITE` as `O` in all ASCII output.
> In standard Reversi, BLACK always moves first.

## Documentation

### Getting Started

| Page                                | Description                        |
|-------------------------------------|------------------------------------|
| [Getting Started](getting-started.md) | Installation and quick start guide |

### User Guide

| Page                    | Description                          |
|-------------------------|--------------------------------------|
| [User Guide](guide.md)  | Core concepts, patterns, and recipes |

### API Reference

| Page                                       | Description                              |
|--------------------------------------------|------------------------------------------|
| [Board](api/board.md)                      | Board state, move execution, and history |
| [Move](api/move.md)                        | Move representation and parsing          |
| [Disc](api/disc.md)                        | Disc color and symbol                    |
| [Outcome & Termination](api/outcome.md)    | Game result and termination conditions   |
| [Constants & Utilities](api/constants.md)  | Square names, colors, and helper functions |
| [SVG Rendering](api/svg.md)                | SVG output and Jupyter integration       |
