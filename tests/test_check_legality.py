from portfolio_chess.core.board import Board
from portfolio_chess.core.move import Move
from portfolio_chess.core.rules import Rules
from portfolio_chess.core.types import Color, Piece, PieceType


def test_cannot_make_move_that_leaves_king_in_check_by_rook() -> None:
    """
    White king on e1 is protected from black rook on e8 by a white piece on e2.
    If white moves that blocker away, the king would be in check -> illegal.
    """
    b = Board()
    r = Rules()

    b.set_piece("e1", Piece(Color.WHITE, PieceType.KING))
    b.set_piece("e2", Piece(Color.WHITE, PieceType.BISHOP))  # blocker
    b.set_piece("e8", Piece(Color.BLACK, PieceType.ROOK))

    b.side_to_move = Color.WHITE

    # Moving the blocker away from the e-file exposes check -> should be illegal
    illegal = Move.from_uci("e2f3")
    try:
        b.apply_legal_move(illegal, r)
        assert False, "Expected ValueError for illegal move (exposes check)"
    except ValueError:
        pass


def test_can_block_check() -> None:
    """
    White king on e1 is in line with black rook on e8.
    A legal move is to block by moving a piece into the line.
    """
    b = Board()
    r = Rules()

    b.set_piece("e1", Piece(Color.WHITE, PieceType.KING))
    b.set_piece("a2", Piece(Color.WHITE, PieceType.ROOK))
    b.set_piece("e8", Piece(Color.BLACK, PieceType.ROOK))

    b.side_to_move = Color.WHITE

    # Block the file by moving rook to e2 (a2->e2 is rook move)
    legal = Move.from_uci("a2e2")
    b.apply_legal_move(legal, r)

    assert b.piece_at("e2") is not None
    assert b.piece_at("e2").kind == PieceType.ROOK
