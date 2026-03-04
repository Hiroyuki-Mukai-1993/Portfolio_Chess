from portfolio_chess.core.board import Board


def test_start_position_fen() -> None:
    b = Board.from_start_position()
    assert b.to_fen() == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


def test_fen_round_trip() -> None:
    fen = "r3k2r/8/8/3pP3/8/8/8/R3K2R w KQkq d6 14 23"
    b = Board.from_fen(fen)

    assert b.to_fen() == fen
