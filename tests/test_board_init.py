from portfolio_chess.core.board import Board
from portfolio_chess.core.types import Color, PieceType


def test_start_position_key_squares() -> None:
    b = Board.from_start_position()

    # White major pieces
    assert b.piece_at("a1") is not None
    assert b.piece_at("a1").color == Color.WHITE
    assert b.piece_at("a1").kind == PieceType.ROOK

    assert b.piece_at("e1") is not None
    assert b.piece_at("e1").color == Color.WHITE
    assert b.piece_at("e1").kind == PieceType.KING

    # Black major pieces
    assert b.piece_at("a8") is not None
    assert b.piece_at("a8").color == Color.BLACK
    assert b.piece_at("a8").kind == PieceType.ROOK

    assert b.piece_at("e8") is not None
    assert b.piece_at("e8").color == Color.BLACK
    assert b.piece_at("e8").kind == PieceType.KING

    # Pawns
    assert b.piece_at("a2") is not None
    assert b.piece_at("a2").color == Color.WHITE
    assert b.piece_at("a2").kind == PieceType.PAWN

    assert b.piece_at("h7") is not None
    assert b.piece_at("h7").color == Color.BLACK
    assert b.piece_at("h7").kind == PieceType.PAWN


def test_start_position_piece_count() -> None:
    b = Board.from_start_position()
    assert len(b.pieces) == 32
