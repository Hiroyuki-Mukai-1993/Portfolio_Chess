from portfolio_chess.core.game import Game
from portfolio_chess.core.move import Move
from portfolio_chess.core.types import Color


def test_threefold_repetition_draw() -> None:
    g = Game()

    seq = ["g1f3", "g8f6", "f3g1", "f6g8"]
    for _ in range(2):
        for uci in seq:
            g.make_move(Move.from_uci(uci))

    assert g.result == "1/2-1/2"
    assert g.termination == "threefold repetition"


def test_fifty_move_rule_draw() -> None:
    g = Game()
    g.load_fen("k7/8/8/8/8/8/8/K1N5 w - - 99 1")

    g.make_move(Move.from_uci("c1b3"))

    assert g.result == "1/2-1/2"
    assert g.termination == "50-move rule"


def test_insufficient_material_draw_after_move() -> None:
    g = Game()
    g.load_fen("k7/8/8/8/8/8/8/K1N5 w - - 0 1")

    g.make_move(Move.from_uci("c1b3"))

    assert g.result == "1/2-1/2"
    assert g.termination == "insufficient material"


def test_draw_by_agreement() -> None:
    g = Game()

    g.offer_draw()
    accepter = Color.BLACK if g.board.side_to_move == Color.WHITE else Color.WHITE
    g.accept_draw(color=accepter)

    assert g.result == "1/2-1/2"
    assert g.termination == "draw by agreement"
