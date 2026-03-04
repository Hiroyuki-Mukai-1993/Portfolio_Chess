from portfolio_chess.core.board import Board
from portfolio_chess.core.move import Move
from portfolio_chess.core.rules import Rules
from portfolio_chess.core.types import Color, Piece, PieceType


def test_king_from_center_has_8_moves_on_empty_board() -> None:
    b = Board()
    r = Rules()

    b.set_piece("d4", Piece(Color.WHITE, PieceType.KING))
    b.side_to_move = Color.WHITE

    pairs = {(m.from_sq, m.to_sq) for m in r.legal_moves(b)}
    frm = Move.from_uci("d4d5").from_sq

    expected = {
        Move.from_uci("d4c3").to_sq,
        Move.from_uci("d4c4").to_sq,
        Move.from_uci("d4c5").to_sq,
        Move.from_uci("d4d3").to_sq,
        Move.from_uci("d4d5").to_sq,
        Move.from_uci("d4e3").to_sq,
        Move.from_uci("d4e4").to_sq,
        Move.from_uci("d4e5").to_sq,
    }

    actual = {t for (f, t) in pairs if f == frm}
    assert actual == expected


def test_king_cannot_move_onto_own_piece_but_can_capture_enemy() -> None:
    b = Board()
    r = Rules()

    b.set_piece("d4", Piece(Color.WHITE, PieceType.KING))
    b.set_piece("e5", Piece(Color.WHITE, PieceType.PAWN))  # own piece
    b.set_piece("c5", Piece(Color.BLACK, PieceType.PAWN))  # enemy

    b.side_to_move = Color.WHITE

    pairs = {(m.from_sq, m.to_sq) for m in r.legal_moves(b)}
    frm = Move.from_uci("d4d5").from_sq

    assert (frm, Move.from_uci("d4e5").to_sq) not in pairs
    assert (frm, Move.from_uci("d4c5").to_sq) in pairs


def test_king_from_corner_has_3_moves() -> None:
    b = Board()
    r = Rules()

    b.set_piece("a1", Piece(Color.WHITE, PieceType.KING))
    b.side_to_move = Color.WHITE

    pairs = {(m.from_sq, m.to_sq) for m in r.legal_moves(b)}
    frm = Move.from_uci("a1a2").from_sq

    expected = {
        Move.from_uci("a1a2").to_sq,
        Move.from_uci("a1b1").to_sq,
        Move.from_uci("a1b2").to_sq,
    }
    actual = {t for (f, t) in pairs if f == frm}
    assert actual == expected
