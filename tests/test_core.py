"""Comprehensive tests for the reversi library."""

from __future__ import annotations

import pytest

import reversi
from reversi.core import (
    BLACK, WHITE, COLOR_NAMES,
    SQUARES, SQUARE_NAMES,
    A1, B1, C1, D1, E1, F1, G1, H1,
    A2, B2, C2, D2, E2, F2, G2, H2,
    A3, B3, C3, D3, E3, F3, G3, H3,
    A4, B4, C4, D4, E4, F4, G4, H4,
    A5, B5, C5, D5, E5, F5, G5, H5,
    A6, B6, C6, D6, E6, F6, G6, H6,
    A7, B7, C7, D7, E7, F7, G7, H7,
    A8, B8, C8, D8, E8, F8, G8, H8,
    square_name, square_file, square_rank, parse_square,
    Disc, Move, Board, Outcome, Termination, LegalMoveGenerator,
)
from reversi import svg as reversi_svg


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _full_board_black_wins() -> Board:
    """63 black discs, 1 white disc at a1 — game is over."""
    b = Board(setup=False)
    for sq in SQUARES:
        b._grid[sq] = Disc(BLACK)
    b._grid[A1] = Disc(WHITE)
    return b


def _pass_position() -> Board:
    """All squares WHITE except a8 (empty) and a7 (BLACK).
    It is BLACK's turn but BLACK has no legal moves; WHITE can play a8.
    """
    b = Board(setup=False)
    b.turn = BLACK
    for sq in SQUARES:
        b._grid[sq] = Disc(WHITE)
    b._grid[A8] = None
    b._grid[A7] = Disc(BLACK)
    return b


# ===========================================================================
# 1. Board initialisation
# ===========================================================================

class TestBoardInit:
    def test_starting_position_has_four_discs(self):
        b = Board()
        occupied = [sq for sq in SQUARES if b.disc_at(sq) is not None]
        assert len(occupied) == 4

    def test_starting_disc_colors(self):
        b = Board()
        assert b.disc_at(D4) == Disc(WHITE)
        assert b.disc_at(E4) == Disc(BLACK)
        assert b.disc_at(D5) == Disc(BLACK)
        assert b.disc_at(E5) == Disc(WHITE)

    def test_starting_turn_is_black(self):
        b = Board()
        assert b.turn == BLACK

    def test_empty_board_has_no_discs(self):
        b = Board(setup=False)
        assert all(b.disc_at(sq) is None for sq in SQUARES)

    def test_move_stack_is_empty_on_init(self):
        b = Board()
        assert b.move_stack == []

    def test_clear_resets_board(self):
        b = Board()
        b.push(Move.from_str("d3"))
        b.clear()
        assert all(b.disc_at(sq) is None for sq in SQUARES)
        assert b.turn == BLACK
        assert b.move_stack == []


# ===========================================================================
# 2. Square utilities
# ===========================================================================

class TestSquareUtilities:
    def test_parse_square_a1(self):
        assert parse_square("a1") == A1

    def test_parse_square_h8(self):
        assert parse_square("h8") == H8

    def test_parse_square_d4(self):
        assert parse_square("d4") == D4

    def test_parse_square_e5(self):
        assert parse_square("e5") == E5

    def test_parse_square_invalid_raises(self):
        with pytest.raises(ValueError, match="invalid square name"):
            parse_square("z9")

    def test_parse_square_wrong_length_raises(self):
        with pytest.raises(ValueError, match="invalid square name"):
            parse_square("a")

    def test_square_name_a1(self):
        assert square_name(A1) == "a1"

    def test_square_name_h8(self):
        assert square_name(H8) == "h8"

    def test_square_name_d4(self):
        assert square_name(D4) == "d4"

    def test_square_name_round_trip(self):
        for sq in SQUARES:
            assert parse_square(square_name(sq)) == sq

    def test_square_file_a_column(self):
        assert square_file(A1) == 0
        assert square_file(A8) == 0

    def test_square_file_h_column(self):
        assert square_file(H1) == 7
        assert square_file(H8) == 7

    def test_square_file_d_column(self):
        assert square_file(D4) == 3

    def test_square_rank_rank_1(self):
        assert square_rank(A1) == 0
        assert square_rank(H1) == 0

    def test_square_rank_rank_8(self):
        assert square_rank(A8) == 7
        assert square_rank(H8) == 7

    def test_square_rank_rank_4(self):
        assert square_rank(D4) == 3

    def test_total_squares(self):
        assert len(SQUARES) == 64

    def test_square_names_count(self):
        assert len(SQUARE_NAMES) == 64


# ===========================================================================
# 3. Move creation and string representation
# ===========================================================================

class TestMove:
    def test_move_from_square(self):
        m = Move(D3)
        assert m.square == D3
        assert not m.is_pass()

    def test_pass_move_factory(self):
        m = Move.pass_move()
        assert m.is_pass()
        assert m.square is None

    def test_move_from_str_normal(self):
        m = Move.from_str("d3")
        assert m.square == D3
        assert not m.is_pass()

    def test_move_from_str_pass_keyword(self):
        assert Move.from_str("pass").is_pass()

    def test_move_from_str_pass_short(self):
        assert Move.from_str("pa").is_pass()

    def test_move_from_str_pass_dashes(self):
        assert Move.from_str("--").is_pass()

    def test_move_from_str_case_insensitive(self):
        assert Move.from_str("D3") == Move.from_str("d3")

    def test_move_str_normal(self):
        assert str(Move.from_str("d3")) == "d3"

    def test_move_str_pass(self):
        assert str(Move.pass_move()) == "--"

    def test_move_repr_normal(self):
        assert repr(Move.from_str("d3")) == "Move(d3)"

    def test_move_repr_pass(self):
        assert repr(Move.pass_move()) == "Move.pass_move()"

    def test_move_equality(self):
        assert Move.from_str("d3") == Move.from_str("d3")
        assert Move.from_str("d3") != Move.from_str("e6")

    def test_pass_moves_are_equal(self):
        assert Move.pass_move() == Move.pass_move()

    def test_move_hash_consistency(self):
        assert hash(Move.from_str("d3")) == hash(Move.from_str("d3"))

    def test_move_bool_true_for_normal(self):
        assert bool(Move.from_str("d3")) is True

    def test_move_bool_false_for_pass(self):
        assert bool(Move.pass_move()) is False

    def test_move_eq_non_move_returns_not_implemented(self):
        result = Move.from_str("d3").__eq__("d3")
        assert result is NotImplemented


# ===========================================================================
# 4. Legal move generation from starting position
# ===========================================================================

class TestLegalMoveGeneration:
    def test_starting_position_has_four_legal_moves(self):
        b = Board()
        assert len(b.legal_moves) == 4

    def test_starting_legal_moves_are_correct_squares(self):
        b = Board()
        legal_squares = {m.square for m in b.legal_moves}
        expected = {parse_square(s) for s in ("d3", "c4", "f5", "e6")}
        assert legal_squares == expected

    def test_legal_moves_membership_true(self):
        b = Board()
        assert Move.from_str("d3") in b.legal_moves

    def test_legal_moves_membership_false(self):
        b = Board()
        assert Move.from_str("a1") not in b.legal_moves

    def test_legal_moves_pass_not_in_starting_position(self):
        b = Board()
        assert Move.pass_move() not in b.legal_moves

    def test_legal_moves_is_iterable(self):
        b = Board()
        moves = list(b.legal_moves)
        assert len(moves) == 4

    def test_legal_moves_bool_true_when_moves_exist(self):
        b = Board()
        assert bool(b.legal_moves) is True

    def test_legal_moves_repr(self):
        b = Board()
        r = repr(b.legal_moves)
        assert r.startswith("LegalMoveGenerator([")

    def test_non_move_not_in_legal_moves(self):
        b = Board()
        assert ("d3" in b.legal_moves) is False


# ===========================================================================
# 5. Push a move and verify board state
# ===========================================================================

class TestPush:
    def test_push_places_disc_on_target_square(self):
        b = Board()
        b.push(Move.from_str("d3"))
        assert b.disc_at(D3) == Disc(BLACK)

    def test_push_flips_captured_discs(self):
        # d3 brackets the white disc at d4
        b = Board()
        b.push(Move.from_str("d3"))
        assert b.disc_at(D4) == Disc(BLACK)

    def test_push_updates_score(self):
        b = Board()
        b.push(Move.from_str("d3"))
        black, white = b.score()
        assert black == 4
        assert white == 1

    def test_push_changes_turn_to_white(self):
        b = Board()
        b.push(Move.from_str("d3"))
        assert b.turn == WHITE

    def test_push_adds_to_move_stack(self):
        b = Board()
        b.push(Move.from_str("d3"))
        assert len(b.move_stack) == 1

    def test_push_occupied_square_raises(self):
        b = Board()
        with pytest.raises(ValueError, match="occupied"):
            b.push(Move(D4))

    def test_push_illegal_move_raises(self):
        b = Board()
        with pytest.raises(ValueError, match="not a legal move"):
            b.push(Move.from_str("a1"))

    def test_push_pass_when_legal_moves_exist_raises(self):
        b = Board()
        with pytest.raises(ValueError, match="cannot pass"):
            b.push(Move.pass_move())

    def test_push_sequence_alternates_turns(self):
        b = Board()
        b.push(Move.from_str("d3"))
        assert b.turn == WHITE
        # find a legal white move and push it
        white_move = next(iter(b.legal_moves))
        b.push(white_move)
        assert b.turn == BLACK


# ===========================================================================
# 6. Pop a move and verify board restored
# ===========================================================================

class TestPop:
    def test_pop_returns_pushed_move(self):
        b = Board()
        m = Move.from_str("d3")
        b.push(m)
        assert b.pop() == m

    def test_pop_removes_placed_disc(self):
        b = Board()
        b.push(Move.from_str("d3"))
        b.pop()
        assert b.disc_at(D3) is None

    def test_pop_restores_flipped_discs(self):
        b = Board()
        b.push(Move.from_str("d3"))
        b.pop()
        assert b.disc_at(D4) == Disc(WHITE)

    def test_pop_restores_turn(self):
        b = Board()
        b.push(Move.from_str("d3"))
        b.pop()
        assert b.turn == BLACK

    def test_pop_removes_from_stack(self):
        b = Board()
        b.push(Move.from_str("d3"))
        b.pop()
        assert b.move_stack == []

    def test_pop_empty_stack_raises(self):
        b = Board(setup=False)
        with pytest.raises(IndexError, match="pop from empty move stack"):
            b.pop()

    def test_pop_fully_restores_board_state(self):
        b_original = Board()
        b = Board()
        b.push(Move.from_str("d3"))
        b.pop()
        assert b == b_original

    def test_peek_returns_last_move_without_removing(self):
        b = Board()
        m = Move.from_str("d3")
        b.push(m)
        peeked = b.peek()
        assert peeked == m
        assert len(b.move_stack) == 1

    def test_peek_empty_stack_raises(self):
        b = Board(setup=False)
        with pytest.raises(IndexError, match="peek on empty move stack"):
            b.peek()


# ===========================================================================
# 7. Pass move
# ===========================================================================

class TestPassMove:
    def test_pass_switches_turn(self):
        b = _pass_position()
        assert b.turn == BLACK
        b.push(Move.pass_move())
        assert b.turn == WHITE

    def test_pass_adds_to_move_stack(self):
        b = _pass_position()
        b.push(Move.pass_move())
        assert len(b.move_stack) == 1

    def test_pass_does_not_change_grid(self):
        b = _pass_position()
        grid_before = list(b._grid)
        b.push(Move.pass_move())
        assert b._grid == grid_before

    def test_pop_pass_restores_turn(self):
        b = _pass_position()
        b.push(Move.pass_move())
        popped = b.pop()
        assert popped.is_pass()
        assert b.turn == BLACK

    def test_has_no_legal_move_for_current_player(self):
        b = _pass_position()
        assert not b.has_legal_move(BLACK)
        assert b.has_legal_move(WHITE)

    def test_pass_not_allowed_when_legal_moves_exist(self):
        b = Board()
        with pytest.raises(ValueError):
            b.push(Move.pass_move())


# ===========================================================================
# 8. Game over detection
# ===========================================================================

class TestGameOver:
    def test_starting_position_is_not_game_over(self):
        assert not Board().is_game_over()

    def test_full_board_is_game_over(self):
        b = _full_board_black_wins()
        assert b.is_game_over()

    def test_game_over_returns_outcome(self):
        b = _full_board_black_wins()
        o = b.outcome()
        assert o is not None
        assert isinstance(o, Outcome)

    def test_not_game_over_returns_none_outcome(self):
        assert Board().outcome() is None

    def test_result_in_progress_is_asterisk(self):
        assert Board().result() == "*"

    def test_result_black_wins(self):
        b = _full_board_black_wins()
        assert b.result() == "1-0"

    def test_result_white_wins(self):
        b = Board(setup=False)
        for sq in SQUARES:
            b._grid[sq] = Disc(WHITE)
        b._grid[A1] = Disc(BLACK)
        assert b.result() == "0-1"

    def test_result_draw(self):
        b = Board(setup=False)
        for sq in SQUARES[:32]:
            b._grid[sq] = Disc(BLACK)
        for sq in SQUARES[32:]:
            b._grid[sq] = Disc(WHITE)
        assert b.result() == "1/2-1/2"

    def test_outcome_termination_is_completed(self):
        b = _full_board_black_wins()
        assert b.outcome().termination == Termination.COMPLETED

    def test_outcome_winner_black(self):
        b = _full_board_black_wins()
        assert b.outcome().winner == BLACK

    def test_outcome_winner_none_on_draw(self):
        b = Board(setup=False)
        for sq in SQUARES[:32]:
            b._grid[sq] = Disc(BLACK)
        for sq in SQUARES[32:]:
            b._grid[sq] = Disc(WHITE)
        assert b.outcome().winner is None


# ===========================================================================
# 9. Score counting
# ===========================================================================

class TestScore:
    def test_starting_score_is_two_two(self):
        assert Board().score() == (2, 2)

    def test_score_after_push_d3(self):
        b = Board()
        b.push(Move.from_str("d3"))
        assert b.score() == (4, 1)

    def test_score_empty_board(self):
        assert Board(setup=False).score() == (0, 0)

    def test_score_all_black(self):
        b = Board(setup=False)
        for sq in SQUARES:
            b._grid[sq] = Disc(BLACK)
        assert b.score() == (64, 0)

    def test_score_all_white(self):
        b = Board(setup=False)
        for sq in SQUARES:
            b._grid[sq] = Disc(WHITE)
        assert b.score() == (0, 64)

    def test_score_sums_to_total_discs(self):
        b = Board()
        b.push(Move.from_str("d3"))
        black, white = b.score()
        total_discs = sum(1 for sq in SQUARES if b.disc_at(sq) is not None)
        assert black + white == total_discs


# ===========================================================================
# 10. FEN round-trip
# ===========================================================================

class TestFEN:
    def test_starting_fen(self):
        assert Board().fen() == "8/8/8/3XO3/3OX3/8/8/8 b"

    def test_fen_round_trip_starting_position(self):
        b = Board()
        original_fen = b.fen()
        b.set_fen(original_fen)
        assert b.fen() == original_fen

    def test_fen_round_trip_after_moves(self):
        b = Board()
        b.push(Move.from_str("d3"))
        fen = b.fen()
        b2 = Board(setup=False)
        b2.set_fen(fen)
        assert b2.fen() == fen

    def test_set_fen_restores_turn_black(self):
        b = Board(setup=False)
        b.set_fen("8/8/8/3XO3/3OX3/8/8/8 b")
        assert b.turn == BLACK

    def test_set_fen_restores_turn_white(self):
        b = Board(setup=False)
        b.set_fen("8/8/8/3XO3/3OX3/8/8/8 w")
        assert b.turn == WHITE

    def test_set_fen_restores_disc_positions(self):
        b = Board(setup=False)
        b.set_fen("8/8/8/3XO3/3OX3/8/8/8 b")
        assert b.disc_at(D4) == Disc(WHITE)
        assert b.disc_at(E4) == Disc(BLACK)
        assert b.disc_at(D5) == Disc(BLACK)
        assert b.disc_at(E5) == Disc(WHITE)

    def test_set_fen_clears_move_stack(self):
        b = Board()
        b.push(Move.from_str("d3"))
        b.set_fen(b.fen())
        assert b.move_stack == []

    def test_set_fen_invalid_raises(self):
        b = Board()
        with pytest.raises(ValueError, match="invalid FEN"):
            b.set_fen("bad_fen")

    def test_set_fen_wrong_row_count_raises(self):
        b = Board()
        with pytest.raises(ValueError, match="expected 8 rows"):
            b.set_fen("8/8/8/8 b")

    def test_fen_encodes_side_to_move_white(self):
        b = Board()
        b.push(Move.from_str("d3"))
        assert b.fen().endswith(" w")

    def test_fen_encodes_side_to_move_black(self):
        assert Board().fen().endswith(" b")

    def test_board_repr_displays_board(self):
        b = Board()
        assert repr(b) == str(b)


# ===========================================================================
# 11. Board copy with stack options
# ===========================================================================

class TestBoardCopy:
    def test_copy_stack_true_preserves_full_stack(self):
        b = Board()
        b.push(Move.from_str("d3"))
        b2 = b.copy(stack=True)
        assert len(b2.move_stack) == 1

    def test_copy_stack_false_clears_stack(self):
        b = Board()
        b.push(Move.from_str("d3"))
        b2 = b.copy(stack=False)
        assert b2.move_stack == []

    def test_copy_stack_int_one(self):
        b = Board()
        b.push(Move.from_str("d3"))
        b2 = b.copy(stack=1)
        assert len(b2.move_stack) == 1

    def test_copy_stack_int_larger_than_stack_copies_all(self):
        # stack=N copies the last N entries; N > len copies everything
        b = Board()
        b.push(Move.from_str("d3"))
        b2 = b.copy(stack=10)
        assert len(b2.move_stack) == len(b.move_stack)

    def test_copy_equals_original_board_state(self):
        b = Board()
        b.push(Move.from_str("d3"))
        assert b.copy() == b

    def test_copy_is_independent(self):
        b = Board()
        b2 = b.copy()
        b2.push(Move.from_str("d3"))
        assert b != b2

    def test_copy_default_stack_is_true(self):
        b = Board()
        b.push(Move.from_str("d3"))
        b2 = b.copy()
        assert len(b2.move_stack) == len(b.move_stack)

    def test_copy_grid_is_independent(self):
        b = Board()
        b2 = b.copy()
        b._grid[A1] = Disc(BLACK)
        assert b2.disc_at(A1) is None


# ===========================================================================
# 12. ASCII string output (__str__)
# ===========================================================================

class TestASCIIOutput:
    def test_str_contains_eight_rows(self):
        lines = str(Board()).splitlines()
        # 8 board rows + 1 file label row = 9 lines
        assert len(lines) == 9

    def test_str_contains_file_labels(self):
        output = str(Board())
        assert "a b c d e f g h" in output

    def test_str_contains_rank_labels(self):
        output = str(Board())
        for rank in "12345678":
            assert rank in output

    def test_str_shows_x_for_black(self):
        output = str(Board())
        assert "X" in output

    def test_str_shows_o_for_white(self):
        output = str(Board())
        assert "O" in output

    def test_str_shows_dots_for_empty(self):
        output = str(Board())
        assert "." in output

    def test_str_empty_board_has_no_discs(self):
        output = str(Board(setup=False))
        assert "X" not in output
        assert "O" not in output

    def test_str_starting_discs_on_correct_rows(self):
        lines = str(Board()).splitlines()
        # ranks are printed 8 down to 1; rank 4 is index 4 (line "5 ..."), rank 5 is index 3 (line "4 ...")
        # line index 0 = rank 8, index 3 = rank 5, index 4 = rank 4
        rank5_line = lines[3]  # "5 . . . X O . . ."
        rank4_line = lines[4]  # "4 . . . O X . . ."
        assert "X" in rank5_line and "O" in rank5_line
        assert "O" in rank4_line and "X" in rank4_line


# ===========================================================================
# 13. SVG output
# ===========================================================================

class TestSVGOutput:
    def test_repr_svg_returns_string(self):
        b = Board()
        result = b._repr_svg_()
        assert isinstance(result, str)

    def test_repr_svg_starts_with_svg_tag(self):
        b = Board()
        assert b._repr_svg_().startswith("<svg")

    def test_repr_svg_ends_with_closing_svg_tag(self):
        b = Board()
        assert b._repr_svg_().strip().endswith("</svg>")

    def test_repr_svg_contains_xmlns(self):
        b = Board()
        assert 'xmlns="http://www.w3.org/2000/svg"' in b._repr_svg_()

    def test_svg_module_board_function_returns_string(self):
        result = reversi_svg.board(Board())
        assert isinstance(result, str)

    def test_svg_default_size_400(self):
        result = reversi_svg.board(Board())
        assert 'width="400"' in result
        assert 'height="400"' in result

    def test_svg_custom_size(self):
        result = reversi_svg.board(Board(), size=600)
        assert 'width="600"' in result

    def test_svg_show_legal_includes_markers(self):
        result = reversi_svg.board(Board(), show_legal=True)
        assert "<circle" in result

    def test_svg_no_coordinates_option(self):
        with_coords = reversi_svg.board(Board(), coordinates=True)
        without_coords = reversi_svg.board(Board(), coordinates=False)
        assert "<text" in with_coords
        assert "<text" not in without_coords

    def test_svg_custom_colors(self):
        result = reversi_svg.board(Board(), colors={"board": "#ff0000"})
        assert "#ff0000" in result

    def test_svg_lastmove_highlight(self):
        result = reversi_svg.board(Board(), lastmove=D3)
        # last move adds a rect with the lastmove fill color
        assert "rgba(255, 255, 0, 0.4)" in result

    def test_svg_none_board_renders(self):
        result = reversi_svg.board(None)
        assert isinstance(result, str)
        assert result.startswith("<svg")


# ===========================================================================
# 14. Board equality
# ===========================================================================

class TestBoardEquality:
    def test_two_fresh_boards_are_equal(self):
        assert Board() == Board()

    def test_board_not_equal_after_push(self):
        b1 = Board()
        b2 = Board()
        b2.push(Move.from_str("d3"))
        assert b1 != b2

    def test_board_equal_after_push_and_pop(self):
        b1 = Board()
        b2 = Board()
        b2.push(Move.from_str("d3"))
        b2.pop()
        assert b1 == b2

    def test_board_not_equal_different_turns(self):
        b1 = Board()
        b2 = Board()
        b2.turn = WHITE
        assert b1 != b2

    def test_board_not_equal_to_non_board(self):
        result = Board().__eq__("not a board")
        assert result is NotImplemented

    def test_board_hash_consistent_with_equality(self):
        b1 = Board()
        b2 = Board()
        assert hash(b1) == hash(b2)

    def test_board_hash_changes_after_push(self):
        b1 = Board()
        b2 = Board()
        b2.push(Move.from_str("d3"))
        assert hash(b1) != hash(b2)

    def test_boards_usable_in_set(self):
        b1 = Board()
        b2 = Board()
        b3 = Board()
        b3.push(Move.from_str("d3"))
        s = {b1, b2, b3}
        assert len(s) == 2


# ===========================================================================
# 15. Disc class
# ===========================================================================

class TestDisc:
    def test_black_disc_symbol(self):
        assert Disc(BLACK).symbol() == "X"

    def test_white_disc_symbol(self):
        assert Disc(WHITE).symbol() == "O"

    def test_disc_repr_black(self):
        assert repr(Disc(BLACK)) == "Disc(black)"

    def test_disc_repr_white(self):
        assert repr(Disc(WHITE)) == "Disc(white)"

    def test_disc_equality(self):
        assert Disc(BLACK) == Disc(BLACK)
        assert Disc(WHITE) == Disc(WHITE)
        assert Disc(BLACK) != Disc(WHITE)

    def test_disc_eq_non_disc_returns_not_implemented(self):
        result = Disc(BLACK).__eq__("X")
        assert result is NotImplemented

    def test_disc_hash_consistent(self):
        assert hash(Disc(BLACK)) == hash(Disc(BLACK))
        assert hash(Disc(WHITE)) == hash(Disc(WHITE))


# ===========================================================================
# 16. Outcome class
# ===========================================================================

class TestOutcome:
    def test_result_black_wins(self):
        o = Outcome(Termination.COMPLETED, BLACK)
        assert o.result() == "1-0"

    def test_result_white_wins(self):
        o = Outcome(Termination.COMPLETED, WHITE)
        assert o.result() == "0-1"

    def test_result_draw(self):
        o = Outcome(Termination.COMPLETED, None)
        assert o.result() == "1/2-1/2"

    def test_outcome_repr_contains_winner(self):
        o = Outcome(Termination.COMPLETED, BLACK)
        assert "black" in repr(o)

    def test_outcome_repr_no_winner(self):
        o = Outcome(Termination.COMPLETED, None)
        assert "None" in repr(o)


# ===========================================================================
# 17. Package-level imports
# ===========================================================================

class TestPackageImports:
    def test_black_constant_exported(self):
        assert reversi.BLACK is True

    def test_white_constant_exported(self):
        assert reversi.WHITE is False

    def test_board_class_exported(self):
        assert reversi.Board is Board

    def test_move_class_exported(self):
        assert reversi.Move is Move

    def test_svg_module_exported(self):
        assert hasattr(reversi, "svg")

    def test_square_constants_exported(self):
        assert reversi.A1 == 0
        assert reversi.H8 == 63
