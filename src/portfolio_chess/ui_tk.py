from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from tkinter import messagebox, simpledialog

from portfolio_chess.core.game import Game
from portfolio_chess.core.move import Move
from portfolio_chess.core.types import Color, PieceType


@dataclass(slots=True)
class UiState:
    selected_sq: int | None = None
    legal_targets: set[int] | None = None


SQUARE_SIZE = 64
MARGIN = 20
BOARD_PX = SQUARE_SIZE * 8
CANVAS_W = BOARD_PX + MARGIN * 2
CANVAS_H = BOARD_PX + MARGIN * 2


def sq_to_xy(sq: int) -> tuple[int, int]:
    file = sq % 8
    rank = sq // 8
    x = MARGIN + file * SQUARE_SIZE
    y = MARGIN + (7 - rank) * SQUARE_SIZE
    return x, y


def xy_to_sq(x: int, y: int) -> int | None:
    x0 = x - MARGIN
    y0 = y - MARGIN
    if x0 < 0 or y0 < 0:
        return None
    file = x0 // SQUARE_SIZE
    rank_from_top = y0 // SQUARE_SIZE
    if not (0 <= file <= 7 and 0 <= rank_from_top <= 7):
        return None
    rank = 7 - rank_from_top
    return int(rank * 8 + file)


def piece_glyph(kind: PieceType, is_white: bool) -> str:
    mapping = {
        PieceType.KING: "K",
        PieceType.QUEEN: "Q",
        PieceType.ROOK: "R",
        PieceType.BISHOP: "B",
        PieceType.KNIGHT: "N",
        PieceType.PAWN: "P",
    }
    s = mapping[kind]
    return s if is_white else s.lower()


class ChessTkApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Portfolio Chess")

        self.game = Game()
        self.state = UiState()

        self.status_var = tk.StringVar(value="Select a piece, then choose a target square.")

        main = tk.Frame(root)
        main.pack(fill="both", expand=True)

        left = tk.Frame(main)
        left.pack(side="left")

        right = tk.Frame(main)
        right.pack(side="right", fill="y")

        self.canvas = tk.Canvas(left, width=CANVAS_W, height=CANVAS_H)
        self.canvas.pack()

        control = tk.Frame(left)
        control.pack(fill="x", pady=(6, 0))

        tk.Button(control, text="New Game", command=self.on_new_game).pack(side="left", padx=2)
        tk.Button(control, text="Reset", command=self.on_reset).pack(side="left", padx=2)
        tk.Button(control, text="Swap First (Next)", command=self.on_swap_next).pack(side="left", padx=2)
        tk.Button(control, text="Resign", command=self.on_resign).pack(side="left", padx=2)

        control2 = tk.Frame(left)
        control2.pack(fill="x", pady=(4, 0))
        tk.Button(control2, text="Offer Draw", command=self.on_offer_draw).pack(side="left", padx=2)
        tk.Button(control2, text="Accept Draw", command=self.on_accept_draw).pack(side="left", padx=2)
        tk.Button(control2, text="Load FEN", command=self.on_load_fen).pack(side="left", padx=2)
        tk.Button(control2, text="Copy FEN", command=self.on_copy_fen).pack(side="left", padx=2)
        tk.Button(control2, text="Copy PGN", command=self.on_copy_pgn).pack(side="left", padx=2)

        tk.Label(right, text="Moves (SAN)", font=("Consolas", 12, "bold")).pack(anchor="w", padx=8, pady=(8, 0))
        self.log_list = tk.Listbox(right, width=32, height=24, font=("Consolas", 11))
        self.log_list.pack(side="left", fill="y", padx=(8, 0), pady=8)

        sb = tk.Scrollbar(right, command=self.log_list.yview)
        sb.pack(side="left", fill="y", pady=8, padx=(0, 8))
        self.log_list.config(yscrollcommand=sb.set)

        self.status = tk.Label(root, textvariable=self.status_var, anchor="w")
        self.status.pack(fill="x")

        self.canvas.bind("<Button-1>", self.on_click)
        self.redraw()

    @property
    def board(self):
        return self.game.board

    @property
    def rules(self):
        return self.game.rules

    def redraw(self) -> None:
        self.canvas.delete("all")

        for sq in range(64):
            x, y = sq_to_xy(sq)
            file = sq % 8
            rank = sq // 8
            light = (file + rank) % 2 == 0
            fill = "#f0d9b5" if light else "#b58863"

            if self.state.legal_targets and sq in self.state.legal_targets:
                fill = "#a9d18e"
            if self.state.selected_sq == sq:
                fill = "#9dc3e6"

            self.canvas.create_rectangle(x, y, x + SQUARE_SIZE, y + SQUARE_SIZE, fill=fill, outline="black")

        for sq, piece in self.board.pieces.items():
            x, y = sq_to_xy(sq)
            glyph = piece_glyph(piece.kind, piece.color == Color.WHITE)
            self.canvas.create_text(
                x + SQUARE_SIZE / 2,
                y + SQUARE_SIZE / 2,
                text=glyph,
                font=("Consolas", 32, "bold"),
            )

        stm = "White" if self.board.side_to_move == Color.WHITE else "Black"
        self.canvas.create_text(CANVAS_W // 2, 10, text=f"Side to move: {stm}", font=("Consolas", 12))

        self._update_status()

    def choose_promotion(self, color: Color) -> str | None:
        win = tk.Toplevel(self.root)
        win.title("Choose promotion")
        win.transient(self.root)
        win.grab_set()

        result: dict[str, str | None] = {"p": None}

        tk.Label(win, text="Promote to:", font=("Consolas", 12)).pack(padx=10, pady=10)

        def pick(p: str) -> None:
            result["p"] = p
            win.destroy()

        frame = tk.Frame(win)
        frame.pack(padx=10, pady=10)

        for p, name in [("q", "Queen"), ("r", "Rook"), ("b", "Bishop"), ("n", "Knight")]:
            display = p.upper() if color == Color.WHITE else p.lower()
            tk.Button(frame, text=f"{display} ({name})", width=14, command=lambda pp=p: pick(pp)).pack(
                side="left", padx=4
            )

        win.protocol("WM_DELETE_WINDOW", win.destroy)
        self.root.wait_window(win)
        return result["p"]

    def on_click(self, event: tk.Event) -> None:
        if self.game.is_over:
            return

        sq = xy_to_sq(event.x, event.y)
        if sq is None:
            return

        if self.state.selected_sq is None:
            piece = self.board.pieces.get(sq)
            if piece is None:
                self.status_var.set("Empty square.")
                return
            if piece.color != self.board.side_to_move:
                self.status_var.set("Select a piece for the side to move.")
                return

            legal = self.rules.legal_moves(self.board)
            targets = {m.to_sq for m in legal if m.from_sq == sq}
            if not targets:
                self.status_var.set("No legal move for that piece.")
                return

            self.state.selected_sq = sq
            self.state.legal_targets = targets
            self.status_var.set("Select target square.")
            self.redraw()
            return

        from_sq = self.state.selected_sq
        to_sq = sq
        self.state.selected_sq = None
        self.state.legal_targets = None

        try:
            move = Move(from_sq=from_sq, to_sq=to_sq, promotion=None)
            piece = self.board.pieces.get(from_sq)
            if piece is not None and piece.kind == PieceType.PAWN:
                to_rank = to_sq // 8
                if (piece.color == Color.WHITE and to_rank == 7) or (piece.color == Color.BLACK and to_rank == 0):
                    promo = self.choose_promotion(piece.color)
                    if promo is None:
                        self.status_var.set("Promotion canceled.")
                        self.redraw()
                        return
                    move = Move(from_sq=from_sq, to_sq=to_sq, promotion=promo)

            san = self.game.make_move(move)
            self._append_move_log(san)
            self.status_var.set(san)
        except Exception as e:
            self.status_var.set(f"Illegal move: {e}")

        self.redraw()

    def _append_move_log(self, san: str) -> None:
        _ = san
        self.log_list.delete(0, "end")
        for i in range(0, len(self.game.san_history), 2):
            num = i // 2 + 1
            w = self.game.san_history[i]
            b = self.game.san_history[i + 1] if i + 1 < len(self.game.san_history) else ""
            self.log_list.insert("end", f"{num:>2}. {w:<8} {b}")
        self.log_list.yview_moveto(1.0)

    def on_new_game(self) -> None:
        self.game.new_game()
        self.state = UiState()
        self.log_list.delete(0, "end")
        self.redraw()

    def on_reset(self) -> None:
        self.on_new_game()

    def on_swap_next(self) -> None:
        self.game.swap_first_player_for_next_game()
        next_side = "White" if self.game.next_game_starts == Color.WHITE else "Black"
        self.status_var.set(f"Next game first move: {next_side}")

    def on_resign(self) -> None:
        try:
            self.game.resign()
            self.redraw()
        except Exception as e:
            self.status_var.set(str(e))

    def on_offer_draw(self) -> None:
        try:
            self.game.offer_draw()
            side = "White" if self.game.draw_offer_by == Color.WHITE else "Black"
            self.status_var.set(f"{side} offered a draw.")
        except Exception as e:
            self.status_var.set(str(e))

    def on_accept_draw(self) -> None:
        try:
            self.game.accept_draw()
            self.redraw()
        except Exception as e:
            self.status_var.set(str(e))

    def on_copy_fen(self) -> None:
        fen = self.game.current_fen()
        self.root.clipboard_clear()
        self.root.clipboard_append(fen)
        self.status_var.set("Copied FEN.")

    def on_copy_pgn(self) -> None:
        pgn = self.game.to_pgn()
        self.root.clipboard_clear()
        self.root.clipboard_append(pgn)
        self.status_var.set("Copied PGN.")

    def on_load_fen(self) -> None:
        fen = simpledialog.askstring("Load FEN", "Enter FEN:")
        if not fen:
            return
        try:
            self.game.load_fen(fen)
            self.state = UiState()
            self.log_list.delete(0, "end")
            self.status_var.set("Loaded FEN.")
            self.redraw()
        except Exception as e:
            messagebox.showerror("FEN Error", str(e))

    def _update_status(self) -> None:
        if self.game.is_over:
            text = self.game.termination or "finished"
            result = self.game.result or "*"
            self.status_var.set(f"Game over: {text} ({result})")
            return

        if self.rules.is_in_check(self.board, self.board.side_to_move):
            self.status_var.set("Check!")


def main() -> None:
    root = tk.Tk()
    ChessTkApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
