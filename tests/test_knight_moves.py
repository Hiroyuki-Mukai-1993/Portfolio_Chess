from portfolio_chess.core.board import Board
from portfolio_chess.core.move import Move
from portfolio_chess.core.rules import Rules
from portfolio_chess.core.types import Color, Piece, PieceType


def test_knight_from_center_has_8_moves_on_empty_board() -> None:
    b = Board()
    r = Rules()

    # White knight on d4 (center-ish)
    b.set_piece("d4", Piece(Color.WHITE, PieceType.KNIGHT))
    b.side_to_move = Color.WHITE

    moves = r.legal_moves(b)
    tos = {m.to_sq for m in moves if m.from_sq == Move.from_uci("d4d4").from_sq}  # dummy from_sq

    # Easier: compute expected by explicit UCI pairs
    expected = {
        Move.from_uci("d4b3").to_sq,
        Move.from_uci("d4b5").to_sq,
        Move.from_uci("d4c2").to_sq,
        Move.from_uci("d4c6").to_sq,
        Move.from_uci("d4e2").to_sq,
        Move.from_uci("d4e6").to_sq,
        Move.from_uci("d4f3").to_sq,
        Move.from_uci("d4f5").to_sq,
    }

    # Filter only moves that start at d4
    from_d4 = Move.from_uci("d4b3").from_sq
    tos = {m.to_sq for m in moves if m.from_sq == from_d4}

    assert tos == expected


def test_knight_can_capture_enemy_but_not_own_piece() -> None:
    b = Board()
    r = Rules()

    b.set_piece("d4", Piece(Color.WHITE, PieceType.KNIGHT))
    b.set_piece("f5", Piece(Color.BLACK, PieceType.PAWN))   # enemy
    b.set_piece("b5", Piece(Color.WHITE, PieceType.PAWN))   # own piece
    b.side_to_move = Color.WHITE

    pairs = {(m.from_sq, m.to_sq) for m in r.legal_moves(b)}

    assert (Move.from_uci("d4f5").from_sq, Move.from_uci("d4f5").to_sq) in pairs
    assert (Move.from_uci("d4b5").from_sq, Move.from_uci("d4b5").to_sq) not in pairs


def test_knight_from_corner_has_2_moves() -> None:
    b = Board()
    r = Rules()

    b.set_piece("a1", Piece(Color.WHITE, PieceType.KNIGHT))
    b.side_to_move = Color.WHITE

    pairs = {(m.from_sq, m.to_sq) for m in r.legal_moves(b)}

    # From a1, only b3 and c2
    assert (Move.from_uci("a1b3").from_sq, Move.from_uci("a1b3").to_sq) in pairs
    assert (Move.from_uci("a1c2").from_sq, Move.from_uci("a1c2").to_sq) in pairs

    # And nothing else for that knight
    from_a1 = Move.from_uci("a1b3").from_sq
    tos = {to for (frm, to) in pairs if frm == from_a1}
    assert tos == {Move.from_uci("a1b3").to_sq, Move.from_uci("a1c2").to_sq}
