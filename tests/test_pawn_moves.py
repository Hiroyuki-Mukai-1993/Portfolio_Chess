from portfolio_chess.core.board import Board
from portfolio_chess.core.move import Move
from portfolio_chess.core.rules import Rules
from portfolio_chess.core.types import Color


def test_start_position_white_pawn_has_one_and_two_step() -> None:
    b = Board.from_start_position()
    r = Rules()

    moves = r.legal_moves(b)
    pairs = {(m.from_sq, m.to_sq) for m in moves}

    e2e3 = Move.from_uci("e2e3")
    e2e4 = Move.from_uci("e2e4")

    assert (e2e3.from_sq, e2e3.to_sq) in pairs
    assert (e2e4.from_sq, e2e4.to_sq) in pairs


def test_apply_legal_move_allows_pawn_push_and_switches_turn() -> None:
    b = Board.from_start_position()
    r = Rules()

    assert b.side_to_move == Color.WHITE
    b.apply_legal_move(Move.from_uci("e2e4"), r)
    assert b.side_to_move == Color.BLACK


def test_illegal_move_is_rejected() -> None:
    b = Board.from_start_position()
    r = Rules()

    # Knight move is not implemented as legal yet
    try:
        b.apply_legal_move(Move.from_uci("f1b5"), r)
        assert False, "Expected ValueError for illegal move"
    except ValueError:
        pass
