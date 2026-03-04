from portfolio_chess.core.board import Board
from portfolio_chess.core.move import Move
from portfolio_chess.core.rules import Rules
from portfolio_chess.core.types import Color, Piece, PieceType


def test_en_passant_is_generated_and_captures_pawn() -> None:
    """
    Setup:
      White pawn: e5
      Black pawn: d7
      Black plays d7d5 (two-step) -> white can capture en passant with e5d6
    """
    b = Board()
    r = Rules()

    b.set_piece("e5", Piece(Color.WHITE, PieceType.PAWN))
    b.set_piece("d7", Piece(Color.BLACK, PieceType.PAWN))
    b.set_piece("e1", Piece(Color.WHITE, PieceType.KING))
    b.set_piece("e8", Piece(Color.BLACK, PieceType.KING))
    b.side_to_move = Color.BLACK

    # Black two-step
    b.apply_legal_move(Move.from_uci("d7d5"), r)

    # White should have en passant: e5d6
    moves = r.legal_moves(b)
    pairs = {(m.from_sq, m.to_sq, m.promotion) for m in moves}
    ep = Move.from_uci("e5d6")
    assert (ep.from_sq, ep.to_sq, ep.promotion) in pairs

    # Apply en passant
    b.apply_legal_move(ep, r)

    # White pawn moved to d6
    p = b.piece_at("d6")
    assert p is not None and p.color == Color.WHITE and p.kind == PieceType.PAWN

    # The captured pawn on d5 should be removed
    assert b.piece_at("d5") is None


def test_en_passant_expires_if_not_used_immediately() -> None:
    """
    Same setup, but white plays a different move first, then en passant must not be available.
    """
    b = Board()
    r = Rules()

    b.set_piece("e5", Piece(Color.WHITE, PieceType.PAWN))
    b.set_piece("d7", Piece(Color.BLACK, PieceType.PAWN))
    b.set_piece("a2", Piece(Color.WHITE, PieceType.ROOK))
    b.set_piece("e1", Piece(Color.WHITE, PieceType.KING))
    b.set_piece("e8", Piece(Color.BLACK, PieceType.KING))
    b.side_to_move = Color.BLACK

    b.apply_legal_move(Move.from_uci("d7d5"), r)

    # White plays something else
    b.apply_legal_move(Move.from_uci("a2a3"), r)

    # Now en passant should be gone
    moves = r.legal_moves(b)
    pairs = {(m.from_sq, m.to_sq, m.promotion) for m in moves}
    ep = Move.from_uci("e5d6")
    assert (ep.from_sq, ep.to_sq, ep.promotion) not in pairs