from portfolio_chess.core.board import Board
from portfolio_chess.core.move import Move
from portfolio_chess.core.rules import Rules
from portfolio_chess.core.types import Color, Piece, PieceType


def test_queen_from_center_on_empty_board_moves_like_bishop_and_rook() -> None:
    b = Board()
    r = Rules()

    b.set_piece("d4", Piece(Color.WHITE, PieceType.QUEEN))
    b.side_to_move = Color.WHITE

    pairs = {(m.from_sq, m.to_sq) for m in r.legal_moves(b)}
    frm = Move.from_uci("d4d5").from_sq

    expected_squares = [
        # Rook-like
        "d5", "d6", "d7", "d8",
        "d3", "d2", "d1",
        "e4", "f4", "g4", "h4",
        "c4", "b4", "a4",
        # Bishop-like
        "e5", "f6", "g7", "h8",
        "c5", "b6", "a7",
        "e3", "f2", "g1",
        "c3", "b2", "a1",
    ]

    expected = {(frm, Move.from_uci(f"d4{sq}").to_sq) for sq in expected_squares}
    actual = {(f, t) for (f, t) in pairs if f == frm}
    assert actual == expected


def test_queen_blocking_and_capture() -> None:
    b = Board()
    r = Rules()

    b.set_piece("d4", Piece(Color.WHITE, PieceType.QUEEN))

    # Own piece blocks North at d6
    b.set_piece("d6", Piece(Color.WHITE, PieceType.PAWN))
    # Enemy piece blocks NE at f6 and is capturable
    b.set_piece("f6", Piece(Color.BLACK, PieceType.PAWN))

    b.side_to_move = Color.WHITE

    pairs = {(m.from_sq, m.to_sq) for m in r.legal_moves(b)}
    frm = Move.from_uci("d4d5").from_sq

    # North: d5 ok, d6 not, d7 not
    assert (frm, Move.from_uci("d4d5").to_sq) in pairs
    assert (frm, Move.from_uci("d4d6").to_sq) not in pairs
    assert (frm, Move.from_uci("d4d7").to_sq) not in pairs

    # NE: e5 ok, f6 capturable, g7 not
    assert (frm, Move.from_uci("d4e5").to_sq) in pairs
    assert (frm, Move.from_uci("d4f6").to_sq) in pairs
    assert (frm, Move.from_uci("d4g7").to_sq) not in pairs
