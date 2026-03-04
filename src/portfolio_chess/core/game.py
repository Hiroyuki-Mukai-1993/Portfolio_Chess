from __future__ import annotations

from dataclasses import dataclass, field

from .board import Board
from .move import Move
from .notation import move_to_san, san_moves_to_pgn
from .rules import Rules
from .types import Color


@dataclass(slots=True)
class Game:
    board: Board = field(default_factory=Board.from_start_position)
    rules: Rules = field(default_factory=Rules)
    san_history: list[str] = field(default_factory=list)
    uci_history: list[str] = field(default_factory=list)
    position_counts: dict[str, int] = field(default_factory=dict)
    result: str | None = None
    termination: str | None = None
    draw_offer_by: Color | None = None
    next_game_starts: Color = Color.WHITE
    initial_fen: str = field(default_factory=lambda: Board.from_start_position().to_fen())

    def __post_init__(self) -> None:
        self.initial_fen = self.board.to_fen()
        self.position_counts[self.board.position_key()] = 1

    @property
    def is_over(self) -> bool:
        return self.result is not None

    def new_game(self, fen: str | None = None) -> None:
        if fen is None:
            self.board = Board.from_start_position()
            self.board.side_to_move = self.next_game_starts
        else:
            self.board = Board.from_fen(fen)

        self.initial_fen = self.board.to_fen()
        self.san_history.clear()
        self.uci_history.clear()
        self.position_counts = {self.board.position_key(): 1}
        self.result = None
        self.termination = None
        self.draw_offer_by = None

    def reset(self) -> None:
        self.new_game()

    def swap_first_player_for_next_game(self) -> None:
        self.next_game_starts = Color.BLACK if self.next_game_starts == Color.WHITE else Color.WHITE

    def make_move(self, move: Move) -> str:
        if self.is_over:
            raise ValueError("Game is already finished.")
        if not self.rules.is_legal(self.board, move):
            raise ValueError("Illegal move.")

        san = move_to_san(self.board, move, self.rules)

        self.board.apply_move(move)
        self.draw_offer_by = None

        self.san_history.append(san)
        self.uci_history.append(self._move_to_uci(move))

        key = self.board.position_key()
        self.position_counts[key] = self.position_counts.get(key, 0) + 1

        self._update_terminal_state()
        return san

    def _update_terminal_state(self) -> None:
        if self.rules.is_checkmate(self.board):
            self.result = "1-0" if self.board.side_to_move == Color.BLACK else "0-1"
            self.termination = "checkmate"
            return

        if self.rules.is_stalemate(self.board):
            self.result = "1/2-1/2"
            self.termination = "stalemate"
            return

        if self.position_counts.get(self.board.position_key(), 0) >= 3:
            self.result = "1/2-1/2"
            self.termination = "threefold repetition"
            return

        if self.board.halfmove_clock >= 100:
            self.result = "1/2-1/2"
            self.termination = "50-move rule"
            return

        if self.rules.is_insufficient_material(self.board):
            self.result = "1/2-1/2"
            self.termination = "insufficient material"

    def resign(self, color: Color | None = None) -> None:
        if self.is_over:
            raise ValueError("Game is already finished.")

        loser = self.board.side_to_move if color is None else color
        self.result = "0-1" if loser == Color.WHITE else "1-0"
        self.termination = "resignation"

    def offer_draw(self, color: Color | None = None) -> None:
        if self.is_over:
            raise ValueError("Game is already finished.")
        self.draw_offer_by = self.board.side_to_move if color is None else color

    def accept_draw(self, color: Color | None = None) -> None:
        if self.is_over:
            raise ValueError("Game is already finished.")
        if self.draw_offer_by is None:
            raise ValueError("No draw offer to accept.")

        if color is None:
            accepter = Color.BLACK if self.draw_offer_by == Color.WHITE else Color.WHITE
        else:
            accepter = color

        if accepter == self.draw_offer_by:
            raise ValueError("Offering side cannot accept its own draw offer.")

        self.result = "1/2-1/2"
        self.termination = "draw by agreement"

    def decline_draw(self) -> None:
        if self.is_over:
            raise ValueError("Game is already finished.")
        self.draw_offer_by = None

    def current_fen(self) -> str:
        return self.board.to_fen()

    def load_fen(self, fen: str) -> None:
        self.new_game(fen)

    def to_pgn(self, event: str = "Casual Game", site: str = "Local") -> str:
        result = self.result or "*"
        tags = [
            f"[Event \"{event}\"]",
            f"[Site \"{site}\"]",
            "[White \"White\"]",
            "[Black \"Black\"]",
            f"[Result \"{result}\"]",
            f"[FEN \"{self.initial_fen}\"]",
        ]
        if self.termination:
            tags.append(f"[Termination \"{self.termination}\"]")

        movetext = san_moves_to_pgn(self.san_history, result)
        return "\n".join(tags) + "\n\n" + movetext

    def _move_to_uci(self, move: Move) -> str:
        from_sq = self._sq_name(move.from_sq)
        to_sq = self._sq_name(move.to_sq)
        promo = move.promotion or ""
        return f"{from_sq}{to_sq}{promo}"

    def _sq_name(self, sq: int) -> str:
        file = "abcdefgh"[sq % 8]
        rank = str((sq // 8) + 1)
        return f"{file}{rank}"
