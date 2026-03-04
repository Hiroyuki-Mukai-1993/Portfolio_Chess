from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .types import (
    CastlingRights,
    Color,
    Piece,
    PieceType,
    index_to_square,
    square_to_index,
)

if TYPE_CHECKING:
    from .move import Move
    from .rules import Rules


@dataclass(slots=True)
class Board:
    pieces: dict[int, Piece] = field(default_factory=dict)
    side_to_move: Color = Color.WHITE
    castling_rights: CastlingRights = field(default_factory=CastlingRights)
    en_passant_target: int | None = None
    halfmove_clock: int = 0
    fullmove_number: int = 1

    @property
    def castlingRights(self) -> CastlingRights:
        # Backward compatibility for existing tests.
        return self.castling_rights

    @castlingRights.setter
    def castlingRights(self, value: CastlingRights) -> None:
        self.castling_rights = value

    @classmethod
    def from_start_position(cls) -> "Board":
        b = cls()
        b._set_start_position()
        b.castling_rights = CastlingRights(wk=True, wq=True, bk=True, bq=True)
        return b

    @classmethod
    def from_fen(cls, fen: str) -> "Board":
        parts = fen.strip().split()
        if len(parts) != 6:
            raise ValueError(f"Invalid FEN: {fen!r}")

        board_part, stm_part, castling_part, ep_part, halfmove_part, fullmove_part = parts
        b = cls()

        ranks = board_part.split("/")
        if len(ranks) != 8:
            raise ValueError(f"Invalid FEN board section: {board_part!r}")

        piece_map: dict[str, PieceType] = {
            "k": PieceType.KING,
            "q": PieceType.QUEEN,
            "r": PieceType.ROOK,
            "b": PieceType.BISHOP,
            "n": PieceType.KNIGHT,
            "p": PieceType.PAWN,
        }

        for rank_from_top, rank_token in enumerate(ranks):
            file_idx = 0
            board_rank = 7 - rank_from_top
            for ch in rank_token:
                if ch.isdigit():
                    file_idx += int(ch)
                    continue
                if ch.lower() not in piece_map:
                    raise ValueError(f"Invalid FEN piece: {ch!r}")
                if not (0 <= file_idx <= 7):
                    raise ValueError(f"Invalid FEN rank token: {rank_token!r}")

                color = Color.WHITE if ch.isupper() else Color.BLACK
                sq = board_rank * 8 + file_idx
                b.pieces[sq] = Piece(color=color, kind=piece_map[ch.lower()])
                file_idx += 1

            if file_idx != 8:
                raise ValueError(f"Invalid FEN rank width: {rank_token!r}")

        if stm_part == "w":
            b.side_to_move = Color.WHITE
        elif stm_part == "b":
            b.side_to_move = Color.BLACK
        else:
            raise ValueError(f"Invalid FEN active color: {stm_part!r}")

        b.castling_rights = CastlingRights.from_fen(castling_part)
        b.en_passant_target = None if ep_part == "-" else square_to_index(ep_part)
        b.halfmove_clock = int(halfmove_part)
        b.fullmove_number = int(fullmove_part)
        return b

    def to_fen(self) -> str:
        rows: list[str] = []
        for rank in range(7, -1, -1):
            empties = 0
            row = ""
            for file in range(8):
                sq = rank * 8 + file
                piece = self.pieces.get(sq)
                if piece is None:
                    empties += 1
                    continue
                if empties:
                    row += str(empties)
                    empties = 0
                row += piece.short()
            if empties:
                row += str(empties)
            rows.append(row)

        stm = "w" if self.side_to_move == Color.WHITE else "b"
        ep = "-" if self.en_passant_target is None else index_to_square(self.en_passant_target)
        return " ".join(
            [
                "/".join(rows),
                stm,
                self.castling_rights.to_fen(),
                ep,
                str(self.halfmove_clock),
                str(self.fullmove_number),
            ]
        )

    def piece_at(self, square: str) -> Piece | None:
        return self.pieces.get(square_to_index(square))

    def set_piece(self, square: str, piece: Piece | None) -> None:
        idx = square_to_index(square)
        if piece is None:
            self.pieces.pop(idx, None)
        else:
            self.pieces[idx] = piece

    def clone(self) -> "Board":
        return Board(
            pieces=dict(self.pieces),
            side_to_move=self.side_to_move,
            castling_rights=self.castling_rights.copy(),
            en_passant_target=self.en_passant_target,
            halfmove_clock=self.halfmove_clock,
            fullmove_number=self.fullmove_number,
        )

    def position_key(self) -> str:
        ep = "-"
        if self.en_passant_target is not None and self._ep_capture_available(self.side_to_move):
            ep = index_to_square(self.en_passant_target)

        return " ".join(
            [
                self.to_fen().split()[0],
                "w" if self.side_to_move == Color.WHITE else "b",
                self.castling_rights.to_fen(),
                ep,
            ]
        )

    def _ep_capture_available(self, side: Color) -> bool:
        target = self.en_passant_target
        if target is None:
            return False

        tf = target % 8
        if side == Color.WHITE:
            candidates = [target - 9, target - 7]
            pawn_rank = (target // 8) - 1
        else:
            candidates = [target + 7, target + 9]
            pawn_rank = (target // 8) + 1

        for sq in candidates:
            if not (0 <= sq < 64):
                continue
            sf = sq % 8
            sr = sq // 8
            if abs(sf - tf) != 1 or sr != pawn_rank:
                continue
            piece = self.pieces.get(sq)
            if piece is not None and piece.color == side and piece.kind == PieceType.PAWN:
                return True
        return False

    def apply_move(self, move: Move) -> None:
        piece = self.pieces.get(move.from_sq)
        if piece is None:
            raise ValueError("No piece on from_sq.")

        moving_side = self.side_to_move
        captured = self.pieces.get(move.to_sq)
        prev_ep = self.en_passant_target

        is_ep_capture = (
            piece.kind == PieceType.PAWN
            and prev_ep is not None
            and move.to_sq == prev_ep
            and captured is None
            and (move.from_sq % 8) != (move.to_sq % 8)
        )

        if is_ep_capture:
            captured_sq = move.to_sq - 8 if piece.color == Color.WHITE else move.to_sq + 8
            captured = self.pieces.pop(captured_sq, None)

        if piece.kind == PieceType.KING:
            if piece.color == Color.WHITE:
                self.castling_rights.wk = False
                self.castling_rights.wq = False
            else:
                self.castling_rights.bk = False
                self.castling_rights.bq = False

        if piece.kind == PieceType.ROOK:
            if piece.color == Color.WHITE:
                if move.from_sq == square_to_index("h1"):
                    self.castling_rights.wk = False
                elif move.from_sq == square_to_index("a1"):
                    self.castling_rights.wq = False
            else:
                if move.from_sq == square_to_index("h8"):
                    self.castling_rights.bk = False
                elif move.from_sq == square_to_index("a8"):
                    self.castling_rights.bq = False

        if captured is not None and captured.kind == PieceType.ROOK:
            if captured.color == Color.WHITE:
                if move.to_sq == square_to_index("h1"):
                    self.castling_rights.wk = False
                elif move.to_sq == square_to_index("a1"):
                    self.castling_rights.wq = False
            else:
                if move.to_sq == square_to_index("h8"):
                    self.castling_rights.bk = False
                elif move.to_sq == square_to_index("a8"):
                    self.castling_rights.bq = False

        placed_piece = piece
        if piece.kind == PieceType.PAWN and move.promotion is not None:
            promo_map = {
                "q": PieceType.QUEEN,
                "r": PieceType.ROOK,
                "b": PieceType.BISHOP,
                "n": PieceType.KNIGHT,
            }
            placed_piece = Piece(piece.color, promo_map[move.promotion])

        self.pieces[move.to_sq] = placed_piece
        self.pieces.pop(move.from_sq)

        if piece.kind == PieceType.KING:
            from_file = move.from_sq % 8
            to_file = move.to_sq % 8
            from_rank = move.from_sq // 8
            to_rank = move.to_sq // 8

            if from_rank == to_rank and abs(to_file - from_file) == 2:
                if to_file > from_file:
                    rook_from = to_rank * 8 + 7
                    rook_to = to_rank * 8 + 5
                else:
                    rook_from = to_rank * 8 + 0
                    rook_to = to_rank * 8 + 3

                rook = self.pieces.get(rook_from)
                if rook is None or rook.kind != PieceType.ROOK:
                    raise ValueError("Castling rook missing.")
                self.pieces[rook_to] = rook
                self.pieces.pop(rook_from)

        is_capture = captured is not None
        if piece.kind == PieceType.PAWN or is_capture:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        self.en_passant_target = None
        if piece.kind == PieceType.PAWN:
            from_rank = move.from_sq // 8
            to_rank = move.to_sq // 8
            if abs(to_rank - from_rank) == 2:
                self.en_passant_target = (move.from_sq + move.to_sq) // 2

        if moving_side == Color.BLACK:
            self.fullmove_number += 1

        self.side_to_move = Color.BLACK if moving_side == Color.WHITE else Color.WHITE

    def apply_legal_move(self, move: Move, rules: Rules) -> None:
        if not rules.is_legal(self, move):
            raise ValueError("Illegal move.")
        self.apply_move(move)

    def _set_start_position(self) -> None:
        self.pieces.clear()
        self.side_to_move = Color.WHITE
        self.en_passant_target = None
        self.halfmove_clock = 0
        self.fullmove_number = 1

        self._place_back_rank(Color.WHITE, rank="1")
        self._place_pawns(Color.WHITE, rank="2")

        self._place_back_rank(Color.BLACK, rank="8")
        self._place_pawns(Color.BLACK, rank="7")

    def _place_pawns(self, color: Color, rank: str) -> None:
        for file_char in "abcdefgh":
            self.set_piece(f"{file_char}{rank}", Piece(color=color, kind=PieceType.PAWN))

    def _place_back_rank(self, color: Color, rank: str) -> None:
        order = [
            PieceType.ROOK,
            PieceType.KNIGHT,
            PieceType.BISHOP,
            PieceType.QUEEN,
            PieceType.KING,
            PieceType.BISHOP,
            PieceType.KNIGHT,
            PieceType.ROOK,
        ]
        for file_char, kind in zip("abcdefgh", order, strict=True):
            self.set_piece(f"{file_char}{rank}", Piece(color=color, kind=kind))

    def to_ascii(self) -> str:
        rows: list[str] = []
        for rank in range(7, -1, -1):
            cells: list[str] = []
            for file in range(8):
                sq = rank * 8 + file
                piece = self.pieces.get(sq)
                cells.append(piece.short() if piece else ".")
            rows.append(f"{rank + 1} " + " ".join(cells))
        rows.append("  a b c d e f g h")
        rows.append(f"Side to move: {self.side_to_move.value}")
        return "\n".join(rows)
