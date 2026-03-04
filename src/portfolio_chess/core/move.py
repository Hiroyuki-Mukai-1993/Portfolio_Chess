from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .types import square_to_index

PromotionCode = Literal["q", "r", "b", "n"]


@dataclass(frozen=True, slots=True)
class Move:
    from_sq: int
    to_sq: int
    promotion: PromotionCode | None = None

    @classmethod
    def from_uci(cls, uci: str) -> "Move":
        if len(uci) not in (4, 5):
            raise ValueError(f"Invalid move string: {uci!r}")

        from_sq = square_to_index(uci[0:2])
        to_sq = square_to_index(uci[2:4])

        promo: PromotionCode | None = None
        if len(uci) == 5:
            p = uci[4].lower()
            if p not in ("q", "r", "b", "n"):
                raise ValueError(f"Invalid promotion piece: {uci!r}")
            promo = p

        return cls(from_sq=from_sq, to_sq=to_sq, promotion=promo)
