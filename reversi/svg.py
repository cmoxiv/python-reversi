"""SVG rendering for reversi boards."""

from __future__ import annotations

from typing import Optional, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from .core import Board, Color, Square

from .core import BLACK, WHITE, square_file, square_rank, SQUARES

DEFAULT_SIZE = 400
MARGIN = 20

DEFAULT_COLORS = {
    "board": "#2e8b57",
    "grid": "#1a5c38",
    "black_disc": "#1a1a1a",
    "white_disc": "#f0f0f0",
    "black_stroke": "#000000",
    "white_stroke": "#cccccc",
    "coords": "#f0f0f0",
    "lastmove": "rgba(255, 255, 0, 0.4)",
    "legal": "rgba(0, 0, 0, 0.15)",
}


def board(
    board: Optional[Board] = None,
    *,
    size: int = DEFAULT_SIZE,
    coordinates: bool = True,
    lastmove: Optional[Square] = None,
    show_legal: bool = False,
    colors: Optional[Dict[str, str]] = None,
) -> str:
    """Render a board as an SVG string."""
    c = dict(DEFAULT_COLORS)
    if colors:
        c.update(colors)

    cell = (size - 2 * MARGIN) / 8 if coordinates else size / 8
    margin = MARGIN if coordinates else 0
    total = size

    parts: list[str] = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {total} {total}" '
        f'width="{total}" height="{total}">'
    )

    # Background
    parts.append(
        f'<rect x="{margin}" y="{margin}" '
        f'width="{cell * 8}" height="{cell * 8}" '
        f'fill="{c["board"]}"/>'
    )

    # Grid lines
    for i in range(9):
        x = margin + i * cell
        parts.append(
            f'<line x1="{x}" y1="{margin}" x2="{x}" y2="{margin + cell * 8}" '
            f'stroke="{c["grid"]}" stroke-width="1"/>'
        )
        y = margin + i * cell
        parts.append(
            f'<line x1="{margin}" y1="{y}" x2="{margin + cell * 8}" y2="{y}" '
            f'stroke="{c["grid"]}" stroke-width="1"/>'
        )

    # Coordinates
    if coordinates:
        for i, letter in enumerate("abcdefgh"):
            x = margin + (i + 0.5) * cell
            parts.append(
                f'<text x="{x}" y="{total - 4}" '
                f'text-anchor="middle" font-size="11" '
                f'fill="{c["coords"]}" font-family="sans-serif">{letter}</text>'
            )
        for i in range(8):
            y = margin + (7.5 - i) * cell
            parts.append(
                f'<text x="{8}" y="{y + 4}" '
                f'text-anchor="middle" font-size="11" '
                f'fill="{c["coords"]}" font-family="sans-serif">{i + 1}</text>'
            )

    # Last move highlight
    if lastmove is not None:
        lf, lr = square_file(lastmove), square_rank(lastmove)
        lx = margin + lf * cell
        ly = margin + (7 - lr) * cell
        parts.append(
            f'<rect x="{lx}" y="{ly}" width="{cell}" height="{cell}" '
            f'fill="{c["lastmove"]}"/>'
        )

    # Legal move markers
    if show_legal and board is not None:
        for move in board.legal_moves:
            if move.square is not None:
                mf, mr = square_file(move.square), square_rank(move.square)
                mx = margin + (mf + 0.5) * cell
                my = margin + (7 - mr + 0.5) * cell
                parts.append(
                    f'<circle cx="{mx}" cy="{my}" r="{cell * 0.15}" '
                    f'fill="{c["legal"]}"/>'
                )

    # Discs
    if board is not None:
        r = cell * 0.42
        for sq in SQUARES:
            disc = board.disc_at(sq)
            if disc is None:
                continue
            f, rk = square_file(sq), square_rank(sq)
            cx = margin + (f + 0.5) * cell
            cy = margin + (7 - rk + 0.5) * cell
            if disc.color == BLACK:
                fill, stroke = c["black_disc"], c["black_stroke"]
            else:
                fill, stroke = c["white_disc"], c["white_stroke"]
            parts.append(
                f'<circle cx="{cx}" cy="{cy}" r="{r}" '
                f'fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
            )

    parts.append("</svg>")
    return "\n".join(parts)
