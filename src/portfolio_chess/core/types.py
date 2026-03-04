from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Final


class Color(Enum):
    WHITE = "white"
    BLACK = "black"


class PieceType(Enum):
    KING = "king"
    QUEEN = "queen"
    ROOK = "rook"
    BISHOP = "bishop"
    KNIGHT = "knight"
    PAWN = "pawn"


@dataclass(frozen=True, slots=True)
class Piece:
    color: Color
    kind: PieceType

    def short(self) -> str:
        mapping: dict[PieceType, str] = {
            PieceType.KING: "K",
            PieceType.QUEEN: "Q",
            PieceType.ROOK: "R",
            PieceType.BISHOP: "B",
            PieceType.KNIGHT: "N",
            PieceType.PAWN: "P",
        }
        s = mapping[self.kind]
        return s if self.color == Color.WHITE else s.lower()


FILES: Final[str] = "abcdefgh"
RANKS: Final[str] = "12345678"


@dataclass(slots=True)
class CastlingRights:
    wk: bool = False
    wq: bool = False
    bk: bool = False
    bq: bool = False

    def copy(self) -> "CastlingRights":
        return CastlingRights(self.wk, self.wq, self.bk, self.bq)

    def to_fen(self) -> str:
        s = ""
        s += "K" if self.wk else ""
        s += "Q" if self.wq else ""
        s += "k" if self.bk else ""
        s += "q" if self.bq else ""
        return s or "-"

    @classmethod
    def from_fen(cls, token: str) -> "CastlingRights":
        if token == "-":
            return cls()
        return cls(
            wk="K" in token,
            wq="Q" in token,
            bk="k" in token,
            bq="q" in token,
        )


def square_to_index(square: str) -> int:
    if len(square) != 2:
        raise ValueError(f"Invalid square: {square!r}")
    file_char = square[0].lower()
    rank_char = square[1]
    if file_char not in FILES or rank_char not in RANKS:
        raise ValueError(f"Invalid square: {square!r}")
    file_idx = FILES.index(file_char)
    rank_idx = RANKS.index(rank_char)
    return rank_idx * 8 + file_idx


def index_to_square(index: int) -> str:
    if not (0 <= index < 64):
        raise ValueError(f"Invalid index: {index}")
    rank_idx, file_idx = divmod(index, 8)
    return f"{FILES[file_idx]}{RANKS[rank_idx]}"
