from portfolio_chess.core.board import Board
from portfolio_chess.core.move import Move
from portfolio_chess.core.rules import Rules
from portfolio_chess.core.types import Color, Piece, PieceType


def test_white_pawn_promotion_requires_suffix() -> None:
    b = Board()
    r = Rules()

    b.set_piece("e7", Piece(Color.WHITE, PieceType.PAWN))
    b.set_piece("e1", Piece(Color.WHITE, PieceType.KING))
    b.set_piece("a8", Piece(Color.BLACK, PieceType.KING))  # e8を空ける
    b.side_to_move = Color.WHITE

    # Missing promotion suffix should be illegal
    try:
        b.apply_legal_move(Move.from_uci("e7e8"), r)
        assert False, "Expected ValueError for missing promotion suffix"
    except ValueError:
        pass


def test_white_pawn_promotes_to_queen() -> None:
    b = Board()
    r = Rules()

    b.set_piece("e7", Piece(Color.WHITE, PieceType.PAWN))
    b.set_piece("e1", Piece(Color.WHITE, PieceType.KING))
    b.set_piece("a8", Piece(Color.BLACK, PieceType.KING))  # e8を空ける
    b.side_to_move = Color.WHITE

    b.apply_legal_move(Move.from_uci("e7e8q"), r)

    p = b.piece_at("e8")
    assert p is not None
    assert p.color == Color.WHITE
    assert p.kind == PieceType.QUEEN


def test_black_pawn_promotes_to_knight() -> None:
    b = Board()
    r = Rules()

    b.set_piece("d2", Piece(Color.BLACK, PieceType.PAWN))
    b.set_piece("e1", Piece(Color.WHITE, PieceType.KING))
    b.set_piece("e8", Piece(Color.BLACK, PieceType.KING))
    b.side_to_move = Color.BLACK

    b.apply_legal_move(Move.from_uci("d2d1n"), r)

    p = b.piece_at("d1")
    assert p is not None
    assert p.color == Color.BLACK
    assert p.kind == PieceType.KNIGHT

def test_white_capture_promotion_to_queen() -> None:
    """
    White pawn captures on last rank and promotes (e7xf8=Q).
    UCI-like: e7f8q
    """
    b = Board()
    r = Rules()

    b.set_piece("e7", Piece(Color.WHITE, PieceType.PAWN))
    b.set_piece("f8", Piece(Color.BLACK, PieceType.ROOK))  # capture target
    b.set_piece("e1", Piece(Color.WHITE, PieceType.KING))
    b.set_piece("a8", Piece(Color.BLACK, PieceType.KING))
    b.side_to_move = Color.WHITE

    b.apply_legal_move(Move.from_uci("e7f8q"), r)

    p = b.piece_at("f8")
    assert p is not None
    assert p.color == Color.WHITE
    assert p.kind == PieceType.QUEEN
    # captured piece should be gone
    assert b.piece_at("e7") is None


def test_black_capture_promotion_to_knight() -> None:
    """
    Black pawn captures on last rank and promotes (d2xc1=N).
    UCI-like: d2c1n
    """
    b = Board()
    r = Rules()

    b.set_piece("d2", Piece(Color.BLACK, PieceType.PAWN))
    b.set_piece("c1", Piece(Color.WHITE, PieceType.BISHOP))  # capture target
    b.set_piece("e1", Piece(Color.WHITE, PieceType.KING))
    b.set_piece("e8", Piece(Color.BLACK, PieceType.KING))
    b.side_to_move = Color.BLACK

    b.apply_legal_move(Move.from_uci("d2c1n"), r)

    p = b.piece_at("c1")
    assert p is not None
    assert p.color == Color.BLACK
    assert p.kind == PieceType.KNIGHT
    assert b.piece_at("d2") is None


def test_promotion_rejects_invalid_suffix() -> None:
    """
    Invalid promotion suffix should be rejected by Move.from_uci.
    """
    try:
        Move.from_uci("e7e8x")
        assert False, "Expected ValueError for invalid promotion suffix"
    except ValueError:
        pass


def test_promotion_move_requires_suffix_for_capture_to_last_rank() -> None:
    """
    If a pawn captures to the last rank, promotion suffix should be required.
    (e7xf8 without suffix is illegal)
    """
    b = Board()
    r = Rules()

    b.set_piece("e7", Piece(Color.WHITE, PieceType.PAWN))
    b.set_piece("f8", Piece(Color.BLACK, PieceType.ROOK))
    b.set_piece("e1", Piece(Color.WHITE, PieceType.KING))
    b.set_piece("a8", Piece(Color.BLACK, PieceType.KING))
    b.side_to_move = Color.WHITE

    try:
        b.apply_legal_move(Move.from_uci("e7f8"), r)  # missing promotion suffix
        assert False, "Expected ValueError for missing promotion suffix on capture promotion"
    except ValueError:
        pass