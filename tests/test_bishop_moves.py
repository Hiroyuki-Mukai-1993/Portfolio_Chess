from portfolio_chess.core.board import Board
from portfolio_chess.core.move import Move
from portfolio_chess.core.rules import Rules
from portfolio_chess.core.types import Color, Piece, PieceType


def test_bishop_from_center_on_empty_board_moves_along_diagonals() -> None:
    b = Board()
    r = Rules()

    b.set_piece("d4", Piece(Color.WHITE, PieceType.BISHOP))
    b.side_to_move = Color.WHITE

    pairs = {(m.from_sq, m.to_sq) for m in r.legal_moves(b)}
    frm = Move.from_uci("d4c5").from_sq

    # Expected squares on diagonals from d4:
    expected_squares = [
        # NE: e5 f6 g7 h8
        "e5", "f6", "g7", "h8",
        # NW: c5 b6 a7
        "c5", "b6", "a7",
        # SE: e3 f2 g1
        "e3", "f2", "g1",
        # SW: c3 b2 a1
        "c3", "b2", "a1",
    ]
    expected = {(frm, Move.from_uci(f"d4{sq}").to_sq) for sq in expected_squares}

    actual = {(f, t) for (f, t) in pairs if f == frm}
    assert actual == expected


def test_bishop_is_blocked_by_own_piece_and_can_capture_enemy() -> None:
    b = Board()
    r = Rules()

    # Bishop on d4
    b.set_piece("d4", Piece(Color.WHITE, PieceType.BISHOP))
    # Own piece blocks NE at f6 (so e5 is allowed, f6 is not, beyond is not)
    b.set_piece("f6", Piece(Color.WHITE, PieceType.PAWN))
    # Enemy piece blocks NW at b6 and is capturable (so c5 allowed, b6 capturable, a7 not)
    b.set_piece("b6", Piece(Color.BLACK, PieceType.PAWN))

    b.side_to_move = Color.WHITE

    pairs = {(m.from_sq, m.to_sq) for m in r.legal_moves(b)}
    frm = Move.from_uci("d4c5").from_sq

    # NE: e5 allowed, f6 not allowed, g7/h8 not allowed
    assert (frm, Move.from_uci("d4e5").to_sq) in pairs
    assert (frm, Move.from_uci("d4f6").to_sq) not in pairs
    assert (frm, Move.from_uci("d4g7").to_sq) not in pairs

    # NW: c5 allowed, b6 capturable, a7 not allowed
    assert (frm, Move.from_uci("d4c5").to_sq) in pairs
    assert (frm, Move.from_uci("d4b6").to_sq) in pairs
    assert (frm, Move.from_uci("d4a7").to_sq) not in pairs
