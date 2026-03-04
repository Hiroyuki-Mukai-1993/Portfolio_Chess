from portfolio_chess.core.board import Board
from portfolio_chess.core.move import Move
from portfolio_chess.core.rules import Rules
from portfolio_chess.core.types import CastlingRights, Color, Piece, PieceType


def test_white_can_castle_kingside_and_rook_moves() -> None:
    b = Board()
    r = Rules()

    # Minimal position for white king-side castling
    b.set_piece("e1", Piece(Color.WHITE, PieceType.KING))
    b.set_piece("h1", Piece(Color.WHITE, PieceType.ROOK))
    b.set_piece("e8", Piece(Color.BLACK, PieceType.KING))  # keep kings on board
    b.castlingRights = CastlingRights(wk=True, wq=False, bk=False, bq=False)
    b.side_to_move = Color.WHITE

    b.apply_legal_move(Move.from_uci("e1g1"), r)

    assert b.piece_at("g1") is not None and b.piece_at("g1").kind == PieceType.KING
    assert b.piece_at("f1") is not None and b.piece_at("f1").kind == PieceType.ROOK
    assert b.piece_at("h1") is None


def test_white_cannot_castle_through_attacked_square() -> None:
    b = Board()
    r = Rules()

    b.set_piece("e1", Piece(Color.WHITE, PieceType.KING))
    b.set_piece("h1", Piece(Color.WHITE, PieceType.ROOK))
    b.set_piece("e8", Piece(Color.BLACK, PieceType.KING))
    # Black rook attacks f1 (square king passes through) along f-file
    b.set_piece("f8", Piece(Color.BLACK, PieceType.ROOK))

    b.castlingRights = CastlingRights(wk=True, wq=False, bk=False, bq=False)
    b.side_to_move = Color.WHITE

    # e1g1 should be illegal
    try:
        b.apply_legal_move(Move.from_uci("e1g1"), r)
        assert False, "Expected ValueError for illegal castling"
    except ValueError:
        pass


def test_castling_rights_removed_after_king_moves() -> None:
    b = Board()
    r = Rules()

    b.set_piece("e1", Piece(Color.WHITE, PieceType.KING))
    b.set_piece("h1", Piece(Color.WHITE, PieceType.ROOK))
    b.set_piece("e8", Piece(Color.BLACK, PieceType.KING))
    b.castlingRights = CastlingRights(wk=True, wq=False, bk=False, bq=False)
    b.side_to_move = Color.WHITE

    # King moves normally -> rights should be removed
    b.apply_legal_move(Move.from_uci("e1e2"), r)

    # Back to white
    b.apply_legal_move(Move.from_uci("e8e7"), r)  # black king dummy move
    b.apply_legal_move(Move.from_uci("e2e1"), r)

    # Now castling must be illegal (rights lost)
    try:
        b.apply_legal_move(Move.from_uci("e1g1"), r)
        assert False, "Expected ValueError because castling rights are gone"
    except ValueError:
        pass
