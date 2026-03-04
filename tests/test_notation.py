from portfolio_chess.core.game import Game
from portfolio_chess.core.move import Move


def test_san_basic_and_capture() -> None:
    g = Game()

    assert g.make_move(Move.from_uci("e2e4")) == "e4"
    assert g.make_move(Move.from_uci("d7d5")) == "d5"
    assert g.make_move(Move.from_uci("e4d5")) == "exd5"


def test_san_knight_and_castling() -> None:
    g = Game()
    g.load_fen("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")

    assert g.make_move(Move.from_uci("e1g1")) == "O-O"


def test_pgn_output_contains_san_and_result() -> None:
    g = Game()

    g.make_move(Move.from_uci("f2f3"))
    g.make_move(Move.from_uci("e7e5"))
    g.make_move(Move.from_uci("g2g4"))
    g.make_move(Move.from_uci("d8h4"))

    pgn = g.to_pgn()
    assert "[Result \"0-1\"]" in pgn
    assert "1. f3 e5 2. g4 Qh4# 0-1" in pgn
