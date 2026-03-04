from portfolio_chess.core.board import Board
from portfolio_chess.core.move import Move
from portfolio_chess.core.rules import Rules
from portfolio_chess.core.types import Color, Piece, PieceType


def test_white_pawn_can_capture_diagonally() -> None:
    b = Board()
    r = Rules()

    # White pawn on e4, black pawn on d5 and f5
    b.set_piece("e4", Piece(Color.WHITE, PieceType.PAWN))
    b.set_piece("d5", Piece(Color.BLACK, PieceType.PAWN))
    b.set_piece("f5", Piece(Color.BLACK, PieceType.PAWN))
    b.side_to_move = Color.WHITE

    moves = r.legal_moves(b)
    pairs = {(m.from_sq, m.to_sq) for m in moves}

    assert (Move.from_uci("e4d5").from_sq, Move.from_uci("e4d5").to_sq) in pairs
    assert (Move.from_uci("e4f5").from_sq, Move.from_uci("e4f5").to_sq) in pairs


def test_white_pawn_cannot_capture_own_piece() -> None:
    b = Board()
    r = Rules()

    b.set_piece("e4", Piece(Color.WHITE, PieceType.PAWN))
    b.set_piece("d5", Piece(Color.WHITE, PieceType.KNIGHT))  # own piece
    b.side_to_move = Color.WHITE

    moves = r.legal_moves(b)
    pairs = {(m.from_sq, m.to_sq) for m in moves}

    assert (Move.from_uci("e4d5").from_sq, Move.from_uci("e4d5").to_sq) not in pairs


def test_pawn_diagonal_move_without_capture_is_not_legal() -> None:
    b = Board()
    r = Rules()

    b.set_piece("e4", Piece(Color.WHITE, PieceType.PAWN))
    # d5 is empty
    b.side_to_move = Color.WHITE

    moves = r.legal_moves(b)
    pairs = {(m.from_sq, m.to_sq) for m in moves}

    assert (Move.from_uci("e4d5").from_sq, Move.from_uci("e4d5").to_sq) not in pairs


def test_black_pawn_can_capture_diagonally() -> None:
    b = Board()
    r = Rules()

    # Black pawn on e5, white pawn on d4 and f4
    b.set_piece("e5", Piece(Color.BLACK, PieceType.PAWN))
    b.set_piece("d4", Piece(Color.WHITE, PieceType.PAWN))
    b.set_piece("f4", Piece(Color.WHITE, PieceType.PAWN))
    b.side_to_move = Color.BLACK

    moves = r.legal_moves(b)
    pairs = {(m.from_sq, m.to_sq) for m in moves}

    assert (Move.from_uci("e5d4").from_sq, Move.from_uci("e5d4").to_sq) in pairs
    assert (Move.from_uci("e5f4").from_sq, Move.from_uci("e5f4").to_sq) in pairs
