from portfolio_chess.core.board import Board
from portfolio_chess.core.move import Move
from portfolio_chess.core.rules import Rules
from portfolio_chess.core.types import Color, Piece, PieceType


def test_rook_from_center_on_empty_board_moves_along_ranks_and_files() -> None:
    b = Board()
    r = Rules()

    b.set_piece("d4", Piece(Color.WHITE, PieceType.ROOK))
    b.side_to_move = Color.WHITE

    pairs = {(m.from_sq, m.to_sq) for m in r.legal_moves(b)}
    frm = Move.from_uci("d4d5").from_sq

    expected_squares = [
        "d5", "d6", "d7", "d8",
        "d3", "d2", "d1",
        "e4", "f4", "g4", "h4",
        "c4", "b4", "a4",
    ]

    expected = {(frm, Move.from_uci(f"d4{sq}").to_sq) for sq in expected_squares}
    actual = {(f, t) for (f, t) in pairs if f == frm}
    assert actual == expected


def test_rook_is_blocked_by_own_piece_and_can_capture_enemy() -> None:
    b = Board()
    r = Rules()

    b.set_piece("d4", Piece(Color.WHITE, PieceType.ROOK))
    b.set_piece("d6", Piece(Color.WHITE, PieceType.PAWN))
    b.set_piece("f4", Piece(Color.BLACK, PieceType.PAWN))

    b.side_to_move = Color.WHITE

    pairs = {(m.from_sq, m.to_sq) for m in r.legal_moves(b)}
    frm = Move.from_uci("d4d5").from_sq

    assert (frm, Move.from_uci("d4d5").to_sq) in pairs
    assert (frm, Move.from_uci("d4d6").to_sq) not in pairs
    assert (frm, Move.from_uci("d4d7").to_sq) not in pairs

    assert (frm, Move.from_uci("d4e4").to_sq) in pairs
    assert (frm, Move.from_uci("d4f4").to_sq) in pairs
    assert (frm, Move.from_uci("d4g4").to_sq) not in pairs
