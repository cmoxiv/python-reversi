"""Core classes for the reversi library."""

from __future__ import annotations

import enum
import copy
from typing import Iterator, Optional, Union

# --- Colors ---

Color = bool
BLACK = True
WHITE = False

COLOR_NAMES = {BLACK: "black", WHITE: "white"}


# --- Squares ---

Square = int

# 8x8 square constants for backward compatibility
SQUARES = [
    A1, B1, C1, D1, E1, F1, G1, H1,
    A2, B2, C2, D2, E2, F2, G2, H2,
    A3, B3, C3, D3, E3, F3, G3, H3,
    A4, B4, C4, D4, E4, F4, G4, H4,
    A5, B5, C5, D5, E5, F5, G5, H5,
    A6, B6, C6, D6, E6, F6, G6, H6,
    A7, B7, C7, D7, E7, F7, G7, H7,
    A8, B8, C8, D8, E8, F8, G8, H8,
] = range(64)

SQUARE_NAMES = [
    f"{f}{r}"
    for r in range(1, 9)
    for f in "abcdefgh"
]

FILE_NAMES = "abcdefgh"
RANK_NAMES = "12345678"


def square_name(square: Square, size: int = 8) -> str:
    file = square % size
    rank = square // size
    return f"{chr(ord('a') + file)}{rank + 1}"


def square_file(square: Square, size: int = 8) -> int:
    return square % size


def square_rank(square: Square, size: int = 8) -> int:
    return square // size


def parse_square(name: str, size: int = 8) -> Square:
    if len(name) < 2:
        raise ValueError(f"invalid square name: {name!r}")
    file_ch = name[0].lower()
    rank_str = name[1:]
    file_idx = ord(file_ch) - ord('a')
    if file_idx < 0 or file_idx >= size:
        raise ValueError(f"invalid square name: {name!r}")
    try:
        rank_idx = int(rank_str) - 1
    except ValueError:
        raise ValueError(f"invalid square name: {name!r}")
    if rank_idx < 0 or rank_idx >= size:
        raise ValueError(f"invalid square name: {name!r}")
    return rank_idx * size + file_idx


# --- Directions ---

DIRECTIONS = [
    (-1, -1), (-1, 0), (-1, 1),
    ( 0, -1),          ( 0, 1),
    ( 1, -1), ( 1, 0), ( 1, 1),
]


# --- Disc ---

class Disc:
    """A disc on the board with a color."""

    def __init__(self, color: Color) -> None:
        self.color = color

    def symbol(self) -> str:
        return "X" if self.color == BLACK else "O"

    def __repr__(self) -> str:
        return f"Disc({COLOR_NAMES[self.color]})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Disc):
            return self.color == other.color
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.color)


# --- Move ---

class Move:
    """A move in reversi is placing a disc on a square, or passing."""

    def __init__(self, square: Optional[Square] = None) -> None:
        self.square = square

    @classmethod
    def pass_move(cls) -> Move:
        return cls(square=None)

    @classmethod
    def from_str(cls, s: str, size: int = 8) -> Move:
        s = s.strip().lower()
        if s in ("pass", "pa", "--"):
            return cls.pass_move()
        return cls(parse_square(s, size))

    def is_pass(self) -> bool:
        return self.square is None

    def __str__(self) -> str:
        if self.is_pass():
            return "--"
        return square_name(self.square)  # type: ignore[arg-type]

    def __repr__(self) -> str:
        if self.is_pass():
            return "Move.pass_move()"
        return f"Move({square_name(self.square)})"  # type: ignore[arg-type]

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Move):
            return self.square == other.square
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.square)

    def __bool__(self) -> bool:
        return not self.is_pass()


# --- Termination ---

class Termination(enum.Enum):
    COMPLETED = enum.auto()


# --- Outcome ---

class Outcome:
    """Information about the outcome of a finished game."""

    def __init__(self, termination: Termination, winner: Optional[Color]) -> None:
        self.termination = termination
        self.winner = winner

    def result(self) -> str:
        if self.winner is None:
            return "1/2-1/2"
        return "1-0" if self.winner == BLACK else "0-1"

    def __repr__(self) -> str:
        winner_str = (
            "None" if self.winner is None else COLOR_NAMES[self.winner]
        )
        return f"Outcome(termination={self.termination!r}, winner={winner_str})"


# --- LegalMoveGenerator ---

class LegalMoveGenerator:
    """Generates legal moves for the current position. Supports iteration,
    counting, and membership testing, mirroring python-chess."""

    def __init__(self, board: Board) -> None:
        self._board = board

    def __iter__(self) -> Iterator[Move]:
        return iter(self._generate())

    def __contains__(self, move: object) -> bool:
        if not isinstance(move, Move):
            return False
        return move in self._generate()

    def __len__(self) -> int:
        return len(self._generate())

    def __bool__(self) -> bool:
        return len(self) > 0

    def __repr__(self) -> str:
        moves = list(self)
        sans = ", ".join(str(m) for m in moves)
        return f"LegalMoveGenerator([{sans}])"

    def _generate(self) -> list[Move]:
        moves = []
        for sq in range(self._board.size * self._board.size):
            if self._board._is_legal(sq, self._board.turn):
                moves.append(Move(sq))
        return moves


# --- Board ---

class Board:
    """An NxN reversi board (default 8x8).

    Mirrors the python-chess Board API: push/pop moves, legal_moves generator,
    turn flag, ASCII/SVG display, game-over detection, and copy.
    """

    def __init__(self, *, size: int = 8, fen: Optional[str] = None) -> None:
        if fen is not None:
            size = len(fen.strip().split()[0].split("/"))
        if size < 4 or size > 26 or size % 2 != 0:
            raise ValueError("board size must be an even number between 4 and 26")
        self.size: int = size
        self._grid: list[Optional[Disc]] = [None] * (size * size)
        self.turn: Color = BLACK
        self.move_stack: list[tuple[Move, list[Square], Color, bool]] = []

        if fen is not None:
            self.set_fen(fen)
        else:
            self._setup()

    @classmethod
    def empty(cls, *, size: int = 8) -> Board:
        """Create a blank board with no discs placed."""
        board = cls.__new__(cls)
        if size < 4 or size > 26 or size % 2 != 0:
            raise ValueError("board size must be an even number between 4 and 26")
        board.size = size
        board._grid = [None] * (size * size)
        board.turn = BLACK
        board.move_stack = []
        return board

    def _setup(self) -> None:
        mid = self.size // 2
        self._grid[(mid - 1) * self.size + (mid - 1)] = Disc(WHITE)
        self._grid[(mid - 1) * self.size + mid] = Disc(BLACK)
        self._grid[mid * self.size + (mid - 1)] = Disc(BLACK)
        self._grid[mid * self.size + mid] = Disc(WHITE)

    def clear(self) -> None:
        self._grid = [None] * (self.size * self.size)
        self.turn = BLACK
        self.move_stack.clear()

    def disc_at(self, square: Square) -> Optional[Disc]:
        return self._grid[square]

    def set_disc_at(self, square: Square, disc: Optional[Disc]) -> None:
        self._grid[square] = disc

    # --- Move generation ---

    @property
    def legal_moves(self) -> LegalMoveGenerator:
        return LegalMoveGenerator(self)

    def _captures_in_direction(
        self, square: Square, color: Color, dr: int, dc: int
    ) -> list[Square]:
        """Return squares of opponent discs captured in one direction."""
        n = self.size
        f, r = square_file(square, n), square_rank(square, n)
        captured: list[Square] = []
        cr, cc = r + dr, f + dc
        while 0 <= cr < n and 0 <= cc < n:
            sq = cr * n + cc
            disc = self._grid[sq]
            if disc is None:
                return []
            if disc.color == color:
                return captured
            captured.append(sq)
            cr += dr
            cc += dc
        return []

    def _all_captures(self, square: Square, color: Color) -> list[Square]:
        """Return all squares captured by placing color at square."""
        captures: list[Square] = []
        for dr, dc in DIRECTIONS:
            captures.extend(self._captures_in_direction(square, color, dr, dc))
        return captures

    def _is_legal(self, square: Square, color: Color) -> bool:
        if self._grid[square] is not None:
            return False
        return len(self._all_captures(square, color)) > 0

    def has_legal_move(self, color: Optional[Color] = None) -> bool:
        if color is None:
            color = self.turn
        return any(self._is_legal(sq, color) for sq in range(self.size * self.size))

    def blocked_player(self) -> Optional[Color]:
        """Return the color of the player who has no legal moves, or
        ``None`` if both players can move.  When the game is over (neither
        player can move) returns ``None`` as well — use
        :meth:`is_game_over` for that case."""
        black_can = self.has_legal_move(BLACK)
        white_can = self.has_legal_move(WHITE)
        if black_can and white_can:
            return None
        if not black_can and not white_can:
            return None  # game over, not a single blocked player
        return BLACK if not black_can else WHITE

    # --- Push / Pop ---

    def push(self, move: Move) -> None:
        if move.is_pass():
            if self.has_legal_move():
                raise ValueError("cannot pass when legal moves are available")
            self.move_stack.append((move, [], self.turn, False))
            self.turn = not self.turn
            return

        sq = move.square
        assert sq is not None

        if self._grid[sq] is not None:
            raise ValueError(f"square {square_name(sq, self.size)} is occupied")

        captures = self._all_captures(sq, self.turn)
        if not captures:
            raise ValueError(f"{move} is not a legal move")

        self._grid[sq] = Disc(self.turn)
        for csq in captures:
            self._grid[csq] = Disc(self.turn)

        color = self.turn
        self.turn = not self.turn

        # Auto-skip: if the opponent has no legal moves but the game isn't
        # over, give the current player another turn.
        skipped = not self.has_legal_move() and not self.is_game_over()
        if skipped:
            self.turn = not self.turn

        self.move_stack.append((move, captures, color, skipped))

    def pop(self) -> Move:
        if not self.move_stack:
            raise IndexError("pop from empty move stack")

        move, captures, color, _skipped = self.move_stack.pop()
        self.turn = color

        if move.is_pass():
            return move

        sq = move.square
        assert sq is not None
        self._grid[sq] = None
        for csq in captures:
            self._grid[csq] = Disc(not color)

        return move

    def peek(self) -> Move:
        if not self.move_stack:
            raise IndexError("peek on empty move stack")
        return self.move_stack[-1][0]

    # --- Game state ---

    def is_game_over(self) -> bool:
        if self.has_legal_move(BLACK) or self.has_legal_move(WHITE):
            return False
        return True

    def outcome(self) -> Optional[Outcome]:
        if not self.is_game_over():
            return None

        black_count, white_count = self.score()

        if black_count > white_count:
            winner: Optional[Color] = BLACK
        elif white_count > black_count:
            winner = WHITE
        else:
            winner = None

        return Outcome(termination=Termination.COMPLETED, winner=winner)

    def result(self) -> str:
        o = self.outcome()
        if o is None:
            return "*"
        return o.result()

    def score(self) -> tuple[int, int]:
        """Return (black_count, white_count)."""
        black = sum(1 for d in self._grid if d is not None and d.color == BLACK)
        white = sum(1 for d in self._grid if d is not None and d.color == WHITE)
        return black, white

    # --- Copy ---

    def copy(self, *, stack: Union[bool, int] = True) -> Board:
        board = Board.empty(size=self.size)
        board._grid = [copy.copy(d) for d in self._grid]
        board.turn = self.turn

        if stack is True:
            board.move_stack = list(self.move_stack)
        elif stack is False:
            board.move_stack = []
        elif isinstance(stack, int):
            board.move_stack = list(self.move_stack[-stack:])

        return board

    # --- String representations ---

    def __str__(self) -> str:
        n = self.size
        rank_width = len(str(n))
        lines: list[str] = []
        for rank in range(n - 1, -1, -1):
            row = []
            for file in range(n):
                disc = self._grid[rank * n + file]
                if disc is None:
                    row.append(".")
                elif disc.color == BLACK:
                    row.append("X")
                else:
                    row.append("O")
            lines.append(f"{rank + 1:>{rank_width}} {' '.join(row)}")
        file_labels = " ".join(chr(ord('a') + f) for f in range(n))
        lines.append(f"{' ' * rank_width} {file_labels}")
        return "\n".join(lines)

    def __repr__(self) -> str:
        return str(self)

    # --- FEN-like representation ---

    def fen(self) -> str:
        """Return a FEN-like string: rows from top rank to rank 1, separated
        by ``/``, then a space and the side to move (``b`` or ``w``).

        Empty squares use run-length encoding (multi-digit for boards > 9).
        ``X`` = black, ``O`` = white.
        """
        n = self.size
        rows: list[str] = []
        for rank in range(n - 1, -1, -1):
            row = ""
            empty = 0
            for file in range(n):
                disc = self._grid[rank * n + file]
                if disc is None:
                    empty += 1
                else:
                    if empty:
                        row += str(empty)
                        empty = 0
                    row += "X" if disc.color == BLACK else "O"
            if empty:
                row += str(empty)
            rows.append(row)
        fen = "/".join(rows)
        fen += " b" if self.turn == BLACK else " w"
        return fen

    def set_fen(self, fen: str) -> None:
        parts = fen.strip().split()
        if len(parts) != 2:
            raise ValueError(f"invalid FEN: {fen!r}")

        rows = parts[0].split("/")
        if len(rows) != self.size:
            raise ValueError(
                f"invalid FEN: expected {self.size} rows, got {len(rows)}"
            )

        n = self.size
        self._grid = [None] * (n * n)
        self.move_stack.clear()

        for rank_idx, row in enumerate(rows):
            rank = n - 1 - rank_idx
            file = 0
            i = 0
            while i < len(row):
                ch = row[i]
                if ch.isdigit():
                    j = i + 1
                    while j < len(row) and row[j].isdigit():
                        j += 1
                    file += int(row[i:j])
                    i = j
                elif ch in ("X", "x"):
                    self._grid[rank * n + file] = Disc(BLACK)
                    file += 1
                    i += 1
                elif ch in ("O", "o"):
                    self._grid[rank * n + file] = Disc(WHITE)
                    file += 1
                    i += 1
                else:
                    raise ValueError(f"invalid FEN character: {ch!r}")

        self.turn = BLACK if parts[1] == "b" else WHITE

    # --- SVG / Jupyter ---

    def _repr_svg_(self) -> str:
        from . import svg as _svg
        return _svg.board(self)

    def _ipython_display_(self, **kwargs: object) -> None:
        from IPython.display import SVG, display
        display(SVG(self._repr_svg_()))

    # --- Equality ---

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Board):
            return (
                self.size == other.size
                and self._grid == other._grid
                and self.turn == other.turn
            )
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.fen())
