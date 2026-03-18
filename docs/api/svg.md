# SVG Rendering

Renders a Reversi board position as an SVG image.

```python
from reversi import svg
```

---

## Module Path

`reversi.svg`

---

## Constants

### `DEFAULT_SIZE`

```python
DEFAULT_SIZE = 400
```

Default total width and height of the rendered SVG, in pixels.

---

### `MARGIN`

```python
MARGIN = 20
```

Pixel gap between the outer edge of the SVG canvas and the board grid. When `coordinates=True` this space is used to draw file and rank labels.

---

### `DEFAULT_COLORS`

The default color palette applied to every render. Values are CSS color strings and may use any format accepted by SVG (`#rrggbb`, named colors, `rgba(…)`, etc.).

| Key             | Default value              | What it colors                             |
|-----------------|----------------------------|--------------------------------------------|
| `board`         | `"#2e8b57"`                | Board background fill                      |
| `grid`          | `"#1a5c38"`                | Grid lines between squares                 |
| `black_disc`    | `"#1a1a1a"`                | Fill of black discs                        |
| `white_disc`    | `"#f0f0f0"`                | Fill of white discs                        |
| `black_stroke`  | `"#000000"`                | Outline stroke of black discs              |
| `white_stroke`  | `"#cccccc"`                | Outline stroke of white discs              |
| `coords`        | `"#f0f0f0"`                | File and rank label text                   |
| `lastmove`      | `"rgba(255, 255, 0, 0.4)"` | Highlight overlay on the last-moved square |
| `legal`         | `"rgba(0, 0, 0, 0.15)"`    | Dot overlay indicating legal move squares  |

---

## Functions

### `board()`

```python
def board(
    board: Optional[Board] = None,
    *,
    size: int = DEFAULT_SIZE,
    coordinates: bool = True,
    lastmove: Optional[Square] = None,
    show_legal: bool = False,
    colors: Optional[Dict[str, str]] = None,
) -> str:
```

Renders a board position as an SVG string.

All parameters after `board` are keyword-only.

#### Parameters

| Parameter     | Type                    | Default        | Description                                                                            |
|---------------|-------------------------|----------------|----------------------------------------------------------------------------------------|
| `board`       | `Optional[Board]`       | `None`         | Position to render. Pass `None` to render an empty board (grid only, no discs).        |
| `size`        | `int`                   | `DEFAULT_SIZE` | Total SVG width and height in pixels.                                                  |
| `coordinates` | `bool`                  | `True`         | When `True`, draws file letters and rank numbers in the margin around the board.       |
| `lastmove`    | `Optional[Square]`      | `None`         | Square to highlight with a semi-transparent overlay, typically the most recent move.   |
| `show_legal`  | `bool`                  | `False`        | When `True`, overlays a faint dot on every square that is a legal move in `board`.     |
| `colors`      | `Optional[Dict[str, str]]` | `None`      | Color overrides merged with `DEFAULT_COLORS`. Only the keys you supply are changed.    |

#### Return Value

`str` — A complete, self-contained SVG document as a UTF-8 string. The string can be written directly to an `.svg` file, embedded in HTML, or passed to `IPython.display.SVG`.

#### Examples

Render the starting position at default size:

```python
import reversi
from reversi import svg

board = reversi.Board()
markup = svg.board(board)

with open("position.svg", "w") as f:
    f.write(markup)
```

Render an empty board (grid only):

```python
markup = svg.board()          # board=None renders just the grid
markup = svg.board(None)      # equivalent explicit form
```

Highlight the last move and show legal moves:

```python
markup = svg.board(
    board,
    lastmove=last_square,
    show_legal=True,
)
```

Render at a smaller size without coordinate labels:

```python
markup = svg.board(board, size=200, coordinates=False)
```

---

## Jupyter Integration

### Automatic rendering via `Board._repr_svg_()`

`Board` implements `_repr_svg_()`, which Jupyter notebooks call automatically when a `Board` is the last expression in a cell. No imports from `reversi.svg` are needed for this to work.

```python
board = reversi.Board()
board   # displays the SVG board inline in the notebook
```

### Custom rendering with `IPython.display.SVG`

When you need more control — a different size, a highlighted square, or legal move dots — generate the SVG string manually and wrap it with `IPython.display.SVG`:

```python
from IPython.display import SVG, display
from reversi import svg

markup = svg.board(board, size=600, show_legal=True, lastmove=last_square)
display(SVG(markup))
```

---

## Custom Themes

The `colors` dict is **merged** with `DEFAULT_COLORS`, so you only need to provide the keys you want to change. Omitted keys keep their defaults.

Dark theme example:

```python
dark_theme = {
    "board":        "#1a1a2e",
    "grid":         "#0f0f1a",
    "black_disc":   "#e0e0e0",
    "white_disc":   "#ffffff",
    "black_stroke": "#cccccc",
    "white_stroke": "#999999",
    "coords":       "#aaaaaa",
    "lastmove":     "rgba(100, 180, 255, 0.4)",
    "legal":        "rgba(255, 255, 255, 0.2)",
}

markup = svg.board(board, colors=dark_theme)
```

Changing a single color without touching the rest:

```python
# Make the board background navy while keeping all other defaults
markup = svg.board(board, colors={"board": "#001f3f"})
```

---

## Notes

- Passing `board=None` renders an empty board showing only the grid and (optionally) coordinates. No discs are drawn.
- All parameters after `board` are keyword-only and must be passed by name.
- The `colors` dict is shallow-merged with `DEFAULT_COLORS` at render time, so partial overrides are safe — you only need to specify the keys you want to change.
- `show_legal` has no visible effect when `board=None`, since there is no game state from which to compute legal moves.
- The returned string is a complete SVG document and can be embedded directly in an HTML `<img src="data:image/svg+xml;…">` data URI or served as `Content-Type: image/svg+xml`.
