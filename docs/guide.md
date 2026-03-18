# reversi User Guide

This guide teaches concepts and patterns for working with the `reversi` library beyond
basic API usage. It covers the game rules, how the board is modelled in code, the move
lifecycle, game-tree search, FEN serialization, and complete runnable examples.

---

## Reversi Rules Overview

Reversi (also marketed as Othello) is played on an **8×8 board** by two players, **Black**
and **White**. Black always moves first.

### Starting Position

Four discs are placed in the centre before play begins:

| Square | Disc  |
|--------|-------|
| d4     | White |
| e4     | Black |
| d5     | Black |
| e5     | White |

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

### Making a Move

A move places one disc of your color on an empty square. The placement is legal only if it
**captures at least one opponent disc**. A capture occurs when your new disc and one of your
existing discs sandwich a continuous line of opponent discs in any of the 8 directions
(horizontal, vertical, or diagonal). Every captured disc is flipped to your color.

### Passing

If the player whose turn it is has **no legal move**, they must pass. A pass does not place
any disc. The opponent then plays again. Passing when legal moves are available is illegal
and `Board.push` will raise `ValueError`.

### Game End

The game ends when **neither player can move**. This usually happens when the board is full,
but it can also occur earlier if all remaining empty squares are illegal for both players.
The player with **more discs wins**. Equal counts result in a draw.

---

## Board Representation

### Square Numbering

Squares are plain integers in the range `0`–`63`. The numbering uses **file-major order**:
files advance first (a → h), then ranks (1 → 8).

```
A1 = 0   B1 = 1   C1 = 2  ...  H1 = 7
A2 = 8   B2 = 9   ...          H2 = 15
...
A8 = 56  B8 = 57  ...          H8 = 63
```

Named constants are exported for every square (`A1`, `B1`, …, `H8`) so you can write
readable code without magic numbers:

```python
import reversi

print(reversi.A1)   # 0
print(reversi.H8)   # 63
print(reversi.D4)   # 27
```

Utility functions convert between integers and names:

```python
reversi.square_name(27)      # 'd4'
reversi.square_file(27)      # 3   (d = index 3, 0-based)
reversi.square_rank(27)      # 3   (rank 4 = index 3, 0-based)
reversi.parse_square('d4')   # 27
```

### Colors

`Color` is a type alias for `bool`.

| Constant       | Value   | Symbol |
|----------------|---------|--------|
| `reversi.BLACK` | `True`  | `X`    |
| `reversi.WHITE` | `False` | `O`    |

Flipping a color is idiomatic Python: `not color`. This is used throughout the library
(e.g., `self.turn = not self.turn` after a move) and in any code you write.

```python
color = reversi.BLACK
opponent = not color   # reversi.WHITE
```

### The Grid

Internally the board stores a list of 64 `Optional[Disc]` entries, indexed by square
integer. `None` means the square is empty. You rarely access `_grid` directly; instead use
`board.disc_at(square)` to read and `board.set_disc_at(square, disc)` to write.

```python
board = reversi.Board()

disc = board.disc_at(reversi.D4)   # Disc(white)
print(disc.color)                  # False  (WHITE)
print(disc.symbol())               # 'O'

board.set_disc_at(reversi.D4, None)               # remove disc
board.set_disc_at(reversi.D4, reversi.Disc(reversi.WHITE))  # restore it
```

### FEN Format

The library uses a compact FEN-like string to serialise positions. The format is:

```
<ranks> <turn>
```

- **Ranks** are listed from rank 8 down to rank 1, separated by `/`.
- Within each rank, squares go from file a to file h.
- `X` = black disc, `O` = white disc, a digit = that many consecutive empty squares.
- **Turn** is `b` for Black to move, `w` for White to move.

Starting position FEN:

```
8/8/8/3OX3/3XO3/8/8/8 b
```

Breaking that down:

| Segment  | Meaning                                                  |
|----------|----------------------------------------------------------|
| `8`      | Rank 8 — eight empty squares                            |
| `8`      | Rank 7 — eight empty squares                            |
| `8`      | Rank 6 — eight empty squares                            |
| `3OX3`   | Rank 5 — three empty, White on d5, Black on e5, three empty |
| `3XO3`   | Rank 4 — three empty, Black on d4, White on e4, three empty |
| `8`      | Rank 3 — eight empty squares                            |
| `8`      | Rank 2 — eight empty squares                            |
| `8`      | Rank 1 — eight empty squares                            |
| `b`      | Black to move                                           |

---

## Move Lifecycle

### Generating Legal Moves

`board.legal_moves` returns a `LegalMoveGenerator`. It is a lightweight lazy object — it
does not materialise all moves until you iterate, count, or test membership.

```python
board = reversi.Board()
gen = board.legal_moves

# Iterate
for move in gen:
    print(move)

# Count without full iteration overhead
print(len(gen))          # e.g. 4 from the starting position

# Membership test
reversi.Move(reversi.C4) in gen   # True

# Boolean — any legal move exists?
if gen:
    print("has moves")
```

### Creating Moves

| Constructor                    | Result                                         |
|--------------------------------|------------------------------------------------|
| `Move(square)`                 | Placement on the given square integer          |
| `Move.from_str("d3")`          | Parse from algebraic notation                  |
| `Move.from_str("pass")`        | Pass move (also accepts `"pa"` or `"--"`)      |
| `Move.pass_move()`             | Pass move directly                             |

```python
m1 = reversi.Move(reversi.C4)
m2 = reversi.Move.from_str("c4")
print(m1 == m2)   # True

p = reversi.Move.pass_move()
print(p.is_pass())   # True
print(bool(p))       # False  — pass moves are falsy
print(str(p))        # '--'
```

### Pushing a Move

`board.push(move)` validates and applies the move in one step:

1. Checks the target square is empty (or that a pass is only used when no legal move exists).
2. Computes all opponent discs captured in all 8 directions.
3. Raises `ValueError` if the move is illegal.
4. Places the disc on the target square.
5. Flips all captured discs to the current player's color.
6. Records `(move, captured_squares, color)` on `board.move_stack`.
7. Flips `board.turn` to the opponent.

```python
board = reversi.Board()
board.push(reversi.Move.from_str("c4"))
print(board.turn == reversi.WHITE)   # True — turn has switched
```

### Popping a Move

`board.pop()` reverses the last push **perfectly**:

1. Pops the top entry from `move_stack`.
2. Restores `board.turn` to the color that made the move.
3. Removes the placed disc from the board.
4. Flips all recorded captures back to the opponent's color.
5. Returns the `Move` that was undone.

```python
move = board.pop()
print(str(move))   # 'c4'
print(board.turn == reversi.BLACK)   # True — back to Black
```

Because `pop` reconstructs the exact prior state from the stored capture list, no
snapshots are needed. This makes the push/pop pattern very memory-efficient for deep search.

### The Move Stack

`board.move_stack` is a plain Python list. Each element is a 3-tuple:

```python
(move, captured_squares, color)
# move              — the Move object
# captured_squares  — list[Square] of flipped opponent discs
# color             — Color of the player who made the move
```

You can inspect history without undoing:

```python
for move, captures, color in board.move_stack:
    name = reversi.COLOR_NAMES[color]
    print(f"{name}: {move}  ({len(captures)} captures)")
```

`board.peek()` returns the last move without removing it.

---

## Game Trees and Analysis

### Using `copy()` for Exploration

When you need to explore variations without corrupting the original board, use
`board.copy()`. The copy has its own independent grid and move stack.

```python
board = reversi.Board()

for move in board.legal_moves:
    child = board.copy(stack=False)   # no history needed for analysis
    child.push(move)
    black, white = child.score()
    print(f"{move}: disc diff = {black - white}")
```

`copy(stack=False)` is cheaper than the default `copy(stack=True)` because it skips
copying the move history. Use `stack=False` whenever you are only evaluating positions and
do not need to trace the path back.

### Walking a Game Tree

The push/pop pair lets you walk a game tree in place without allocating child boards.
This is faster and uses less memory than copying for every node.

```python
import reversi

def perft(board: reversi.Board, depth: int) -> int:
    """Count leaf nodes at exactly `depth` plies from the current position."""
    if depth == 0:
        return 1

    moves = list(board.legal_moves)
    if not moves:
        # Forced pass
        pass_move = reversi.Move.pass_move()
        board.push(pass_move)
        nodes = perft(board, depth - 1) if not board.is_game_over() else 1
        board.pop()
        return nodes

    nodes = 0
    for move in moves:
        board.push(move)
        nodes += perft(board, depth - 1)
        board.pop()
    return nodes

board = reversi.Board()
print(perft(board, 1))   # 4  (four legal moves from the start)
print(perft(board, 2))   # 12
```

### Simple Minimax Evaluation

The following minimax uses disc-difference as a static evaluation: positive favors Black,
negative favors White.

```python
import reversi

def disc_diff(board: reversi.Board) -> int:
    black, white = board.score()
    return black - white

def minimax(board: reversi.Board, depth: int, maximising: bool) -> int:
    if depth == 0 or board.is_game_over():
        return disc_diff(board)

    moves = list(board.legal_moves)

    if not moves:
        # No move available — push a pass and keep searching
        board.push(reversi.Move.pass_move())
        score = minimax(board, depth - 1, not maximising)
        board.pop()
        return score

    if maximising:
        best = -64
        for move in moves:
            board.push(move)
            best = max(best, minimax(board, depth - 1, False))
            board.pop()
        return best
    else:
        best = 64
        for move in moves:
            board.push(move)
            best = min(best, minimax(board, depth - 1, True))
            board.pop()
        return best

def best_move_minimax(board: reversi.Board, depth: int = 3) -> reversi.Move:
    """Return the best move for the current player using minimax."""
    maximising = board.turn == reversi.BLACK
    best_score = -65 if maximising else 65
    best = None

    for move in board.legal_moves:
        board.push(move)
        score = minimax(board, depth - 1, not maximising)
        board.pop()

        if maximising and score > best_score:
            best_score, best = score, move
        elif not maximising and score < best_score:
            best_score, best = score, move

    return best  # type: ignore[return-value]
```

---

## Working with FEN

### Saving and Loading Positions

```python
import reversi

board = reversi.Board()
board.push(reversi.Move.from_str("c4"))
board.push(reversi.Move.from_str("c3"))

fen = board.fen()
print(fen)   # e.g. '8/8/8/3OX3/2XXX3/2O5/8/8 b'

# Save to a file
with open("position.fen", "w") as f:
    f.write(fen)

# Restore from a file
restored = reversi.Board(setup=False)
with open("position.fen") as f:
    restored.set_fen(f.read().strip())

assert board == restored
```

### Setting Up Custom Positions for Analysis

`set_fen` completely replaces the board state. This is useful for loading known endgame
positions or puzzles without replaying all the moves.

```python
import reversi

# An almost-full board — White to move with one square left
board = reversi.Board(setup=False)
board.set_fen("XXXXXXXO/XXXXXXOO/XXXXXXOO/XXXXXXOO/XXXXXXOO/XXXXXXOO/XXXXXXOO/XXXXXXX1 w")

print(list(board.legal_moves))   # check what White can still play
print(board.score())
```

Note that `set_fen` clears `move_stack`. If you need history before setting a FEN, build
it by pushing moves after the FEN is loaded.

---

## Patterns from python-chess

The `reversi` API deliberately mirrors [python-chess](https://github.com/niklasf/python-chess)
conventions. If you have used python-chess, most patterns transfer directly.

| Pattern                     | python-chess                     | reversi                              |
|-----------------------------|----------------------------------|--------------------------------------|
| Current player              | `board.turn` (`chess.WHITE/BLACK`) | `board.turn` (`reversi.BLACK/WHITE`) |
| Flip color                  | `not board.turn`                 | `not board.turn`                     |
| Iterate legal moves         | `for m in board.legal_moves`     | `for m in board.legal_moves`         |
| Count legal moves           | `board.legal_moves.count()`      | `len(board.legal_moves)`             |
| Membership test             | `move in board.legal_moves`      | `move in board.legal_moves`          |
| Any legal move?             | `bool(board.legal_moves)`        | `bool(board.legal_moves)`            |
| Apply move                  | `board.push(move)`               | `board.push(move)`                   |
| Undo move                   | `board.pop()`                    | `board.pop()`                        |
| Copy board                  | `board.copy()`                   | `board.copy()`                       |
| FEN string                  | `board.fen()`                    | `board.fen()`                        |
| Load FEN                    | `board.set_fen(fen)`             | `board.set_fen(fen)`                 |
| Game over?                  | `board.is_game_over()`           | `board.is_game_over()`               |
| Game outcome                | `board.outcome()`                | `board.outcome()`                    |
| Jupyter SVG display         | `board._repr_svg_()`             | `board._repr_svg_()`                 |

### Key Differences from python-chess

- **Pass moves exist.** Chess has no passing; reversi does. Always handle the no-legal-moves
  case in game loops by pushing `Move.pass_move()`.
- **`board.turn` is `bool`.** `BLACK = True`, `WHITE = False`. The `not` operator flips it,
  which is the same pattern as python-chess but with opposite truth values.
- **`len(board.legal_moves)`** is used instead of `.count()` — the generator is a custom
  class that implements `__len__` directly.
- **No check, castling, or en passant.** Reversi has none of these; the `Board` class is
  correspondingly simpler.

---

## Example: Random Game with Statistics

This example plays a complete random game, prints every move with the running score, and
displays final statistics.

```python
import random
import reversi

def play_random_game(seed: int | None = None) -> None:
    rng = random.Random(seed)
    board = reversi.Board()
    move_number = 1

    print("Starting position:")
    print(board)
    print()

    while not board.is_game_over():
        color_name = reversi.COLOR_NAMES[board.turn]
        moves = list(board.legal_moves)

        if moves:
            move = rng.choice(moves)
        else:
            move = reversi.Move.pass_move()

        board.push(move)

        black, white = board.score()
        print(f"Move {move_number:>3}: {color_name:<5} plays {str(move):<4}  "
              f"score B={black} W={white}")
        move_number += 1

    print()
    print("Final board:")
    print(board)
    print()

    black, white = board.score()
    outcome = board.outcome()
    print(f"Final score  — Black: {black}  White: {white}")
    print(f"Total moves  : {len(board.move_stack)}")
    print(f"Result       : {board.result()}")

    if outcome.winner is None:
        print("Game drawn.")
    else:
        print(f"Winner       : {reversi.COLOR_NAMES[outcome.winner]}")


if __name__ == "__main__":
    play_random_game(seed=42)
```

Sample output (seed 42):

```
Starting position:
8 . . . . . . . .
7 . . . . . . . .
6 . . . . . . . .
5 . . . X O . . .
4 . . . O X . . .
3 . . . . . . . .
2 . . . . . . . .
1 . . . . . . . .
  a b c d e f g h

Move   1: black plays c4    score B=4 W=1
Move   2: white plays c3    score B=3 W=3
...
```

---

## Example: Simple AI (Greedy Strategy)

A **greedy** player picks whichever legal move leaves the most discs of its own color on
the board immediately after the move. It makes no look-ahead. The example pits the greedy
player (Black) against a random opponent (White) and reports results over multiple games.

```python
import random
import reversi

def greedy_move(board: reversi.Board) -> reversi.Move:
    """Return the move that maximises the current player's disc count."""
    best_move = None
    best_score = -1

    for move in board.legal_moves:
        board.push(move)
        black, white = board.score()
        score = black if board.turn == reversi.WHITE else white
        # board.turn has already flipped, so we check the opponent's turn
        # to identify which count belongs to the player who just moved.
        board.pop()

        if score > best_score:
            best_score = score
            best_move = move

    return best_move  # type: ignore[return-value]


def play_greedy_vs_random(seed: int | None = None, verbose: bool = False) -> str:
    """Play one game: Black=greedy, White=random. Returns result string."""
    rng = random.Random(seed)
    board = reversi.Board()

    while not board.is_game_over():
        moves = list(board.legal_moves)

        if not moves:
            move = reversi.Move.pass_move()
        elif board.turn == reversi.BLACK:
            move = greedy_move(board)
        else:
            move = rng.choice(moves)

        if verbose:
            color_name = reversi.COLOR_NAMES[board.turn]
            print(f"{color_name}: {move}")

        board.push(move)

    if verbose:
        print(board)
        black, white = board.score()
        print(f"Score — Black: {black}  White: {white}")

    return board.result()


def run_tournament(games: int = 100, seed: int = 0) -> None:
    results = {"1-0": 0, "0-1": 0, "1/2-1/2": 0}
    for i in range(games):
        result = play_greedy_vs_random(seed=seed + i)
        results[result] += 1

    print(f"Results over {games} games (Black=greedy, White=random):")
    print(f"  Black wins : {results['1-0']}")
    print(f"  White wins : {results['0-1']}")
    print(f"  Draws      : {results['1/2-1/2']}")


if __name__ == "__main__":
    # Single verbose game
    play_greedy_vs_random(seed=7, verbose=True)
    print()

    # Tournament
    run_tournament(games=200, seed=0)
```

### How the Greedy Evaluation Works

Inside `greedy_move`, note the score extraction after pushing:

```python
board.push(move)
black, white = board.score()
# After push, board.turn has flipped to the opponent.
# So the player who just moved is NOT board.turn.
score = black if board.turn == reversi.WHITE else white
board.pop()
```

Because `push` flips the turn immediately, the player who just moved has color
`not board.turn`. If it is now White's turn (`board.turn == WHITE`), the move was made by
Black, so we want `black`. Conversely, if it is now Black's turn, the move was made by
White and we want `white`.

This is a common source of off-by-one errors when evaluating positions from within a loop
that uses push/pop — always account for the turn having already advanced.
