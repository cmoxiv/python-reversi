# Outcome and Termination

`Outcome` and `Termination` represent the result of a finished game. A `Board` returns
`None` from `Board.outcome()` while the game is still in progress, and an `Outcome`
instance once the game is over.

---

## Termination

```python
class Termination(enum.Enum):
    COMPLETED = enum.auto()
```

An enumeration describing how a game ended.

| Member      | Description                                           |
|-------------|-------------------------------------------------------|
| `COMPLETED` | Both players passed consecutively; the board is full. |

Additional members may be added in future releases. For example, `RESIGNATION` could be
introduced to represent a player resigning before the board is full. Code that switches on
`Termination` should handle unexpected members gracefully (e.g., with a default branch).

---

## Outcome

```python
class Outcome:
    def __init__(self, termination: Termination, winner: Optional[Color]) -> None
```

Holds the final result of a completed game. Instances are produced by `Board.outcome()`
and are not normally constructed directly.

### Constructor

| Parameter     | Type                  | Description                                                     |
|---------------|-----------------------|-----------------------------------------------------------------|
| `termination` | `Termination`         | The reason the game ended.                                      |
| `winner`      | `Optional[Color]`     | `BLACK`, `WHITE`, or `None` when the disc count is equal (draw).|

### Attributes

| Attribute     | Type                  | Description                                                     |
|---------------|-----------------------|-----------------------------------------------------------------|
| `termination` | `Termination`         | The reason the game ended.                                      |
| `winner`      | `Optional[Color]`     | `BLACK`, `WHITE`, or `None` for a draw.                         |

### Methods

#### `result() -> str`

Returns a standard result string.

| Return value | Meaning      |
|--------------|--------------|
| `"1-0"`      | Black wins.  |
| `"0-1"`      | White wins.  |
| `"1/2-1/2"`  | Draw.        |

#### `__repr__() -> str`

Returns a developer-readable string, for example:

```
Outcome(termination=<Termination.COMPLETED: 1>, winner=<Color.BLACK: True>)
```

---

## Board integration

`Board.outcome()` is the primary way to obtain an `Outcome`.

| `Board.outcome()` return value | Meaning                  |
|-------------------------------|--------------------------|
| `None`                        | Game is still in progress.|
| `Outcome`                     | Game is over.             |

---

## Examples

Check whether the game is over and inspect the result:

```python
import reversi

board = reversi.Board()

# Play moves until the game ends ...
while board.outcome() is None:
    legal = list(board.legal_moves)
    if legal:
        board.push(legal[0])
    else:
        board.push(reversi.Move.null())  # pass

outcome = board.outcome()
print(outcome.termination)  # Termination.COMPLETED
print(outcome.winner)       # Color.BLACK, Color.WHITE, or None
print(outcome.result())     # "1-0", "0-1", or "1/2-1/2"
```

Branch on the winner:

```python
outcome = board.outcome()

if outcome is None:
    print("Game still in progress.")
elif outcome.winner is reversi.BLACK:
    print("Black wins!")
elif outcome.winner is reversi.WHITE:
    print("White wins!")
else:
    print("Draw.")
```

Check the termination reason (future-proof style):

```python
outcome = board.outcome()

if outcome is not None:
    if outcome.termination is reversi.Termination.COMPLETED:
        print("Game completed normally.")
    else:
        print(f"Game ended by: {outcome.termination}")
```
