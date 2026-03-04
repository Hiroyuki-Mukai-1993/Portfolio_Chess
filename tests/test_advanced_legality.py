from portfolio_chess.core.board import Board
from portfolio_chess.core.move import Move
from portfolio_chess.core.rules import Rules
from portfolio_chess.core.types import Color, Piece, PieceType


def test_pinned_piece_cannot_leave_pin_line() -> None:
    b = Board()
    r = Rules()

    b.set_piece("e1", Piece(Color.WHITE, PieceType.KING))
    b.set_piece("e2", Piece(Color.WHITE, PieceType.ROOK))
    b.set_piece("e8", Piece(Color.BLACK, PieceType.ROOK))
    b.set_piece("a8", Piece(Color.BLACK, PieceType.KING))
    b.side_to_move = Color.WHITE

    legal = {(m.from_sq, m.to_sq) for m in r.legal_moves(b)}

    assert (Move.from_uci("e2f2").from_sq, Move.from_uci("e2f2").to_sq) not in legal
    assert (Move.from_uci("e2e3").from_sq, Move.from_uci("e2e3").to_sq) in legal


def test_cannot_castle_when_destination_square_attacked() -> None:
    b = Board()
    r = Rules()

    b.set_piece("e1", Piece(Color.WHITE, PieceType.KING))
    b.set_piece("h1", Piece(Color.WHITE, PieceType.ROOK))
    b.set_piece("c5", Piece(Color.BLACK, PieceType.BISHOP))
    b.set_piece("e8", Piece(Color.BLACK, PieceType.KING))
    b.castlingRights.wk = True
    b.side_to_move = Color.WHITE

    illegal = Move.from_uci("e1g1")
    assert r.is_legal(b, illegal) is False


def test_en_passant_illegal_if_it_exposes_own_king() -> None:
    b = Board.from_fen("k3r3/8/8/3pP3/8/8/8/4K3 w - d6 0 1")
    r = Rules()

    ep = Move.from_uci("e5d6")
    assert r.is_legal(b, ep) is False
