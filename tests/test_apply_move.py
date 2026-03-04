from portfolio_chess.core.board import Board
from portfolio_chess.core.move import Move
from portfolio_chess.core.types import Color, PieceType


def test_apply_move_e2e4_moves_pawn_and_switches_turn() -> None:
    b = Board.from_start_position()
    assert b.side_to_move == Color.WHITE

    move = Move.from_uci("e2e4")
    b.apply_move(move)

    # Pawn moved
    p = b.piece_at("e4")
    assert p is not None
    assert p.color == Color.WHITE
    assert p.kind == PieceType.PAWN

    # Source square emptied
    assert b.piece_at("e2") is None

    # Turn switched
    assert b.side_to_move == Color.BLACK


def test_apply_move_captures_by_overwrite() -> None:
    b = Board()
    # Minimal position: white rook on a1, black pawn on a8
    from portfolio_chess.core.types import Piece

    b.set_piece("a1", Piece(Color.WHITE, PieceType.ROOK))
    b.set_piece("a8", Piece(Color.BLACK, PieceType.PAWN))
    b.side_to_move = Color.WHITE

    b.apply_move(Move.from_uci("a1a8"))

    captured_square = b.piece_at("a8")
    assert captured_square is not None
    assert captured_square.color == Color.WHITE
    assert captured_square.kind == PieceType.ROOK
    assert b.piece_at("a1") is None
