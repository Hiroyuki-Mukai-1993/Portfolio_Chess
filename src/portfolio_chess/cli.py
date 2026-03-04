from __future__ import annotations

from portfolio_chess.core.game import Game
from portfolio_chess.core.move import Move


def main() -> None:
    game = Game()

    print(game.board.to_ascii())
    print("Enter UCI moves like 'e2e4'. commands: fen, pgn, resign, draw, new, quit")

    while True:
        s = input("> ").strip()
        if s.lower() in {"q", "quit", "exit"}:
            break
        if not s:
            continue

        if s.lower() == "fen":
            print(game.current_fen())
            continue
        if s.lower() == "pgn":
            print(game.to_pgn())
            continue
        if s.lower() == "resign":
            try:
                game.resign()
                print(f"Game over: {game.termination} ({game.result})")
            except Exception as e:
                print(f"Error: {e}")
            continue
        if s.lower() == "draw":
            try:
                game.offer_draw()
                game.accept_draw()
                print(f"Game over: {game.termination} ({game.result})")
            except Exception as e:
                print(f"Error: {e}")
            continue
        if s.lower() == "new":
            game.new_game()
            print("Started new game.")
            print(game.board.to_ascii())
            continue

        try:
            move = Move.from_uci(s)
            san = game.make_move(move)
            print(f"{san}")
            print(game.board.to_ascii())
            if game.is_over:
                print(f"Game over: {game.termination} ({game.result})")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
