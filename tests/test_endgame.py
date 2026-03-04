from portfolio_chess.core.board import Board
from portfolio_chess.core.rules import Rules
from portfolio_chess.core.types import Color, Piece, PieceType


def test_checkmate_simple_king_and_queen() -> None:
    """
    Black to move is checkmated.
    Position (one of the simplest):
      Black king: a8
      White king: c6
      White queen: b7
    It's black to move and has no legal moves; king is in check.
    """
    b = Board()
    r = Rules()

    b.set_piece("a8", Piece(Color.BLACK, PieceType.KING))
    b.set_piece("c6", Piece(Color.WHITE, PieceType.KING))
    b.set_piece("b7", Piece(Color.WHITE, PieceType.QUEEN))
    b.side_to_move = Color.BLACK

    assert r.is_in_check(b, Color.BLACK) is True
    assert r.is_checkmate(b) is True
    assert r.is_stalemate(b) is False


def test_stalemate_simple_king_and_queen() -> None:
    """
    Black to move is stalemated.
    Classic stalemate pattern:
      Black king: a8
      White king: c6
      White queen: c7
    Black has no legal moves, but is NOT in check.
    """
    b = Board()
    r = Rules()

    b.set_piece("a8", Piece(Color.BLACK, PieceType.KING))
    b.set_piece("c6", Piece(Color.WHITE, PieceType.KING))
    b.set_piece("c7", Piece(Color.WHITE, PieceType.QUEEN))
    b.side_to_move = Color.BLACK

    assert r.is_in_check(b, Color.BLACK) is False
    assert r.is_checkmate(b) is False
    assert r.is_stalemate(b) is True