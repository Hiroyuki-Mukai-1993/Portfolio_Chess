from __future__ import annotations

from dataclasses import dataclass

from .board import Board
from .move import Move
from .types import Color, PieceType, square_to_index


@dataclass(frozen=True, slots=True)
class Rules:
    def legal_moves(self, board: Board) -> list[Move]:
        pseudo = self._pseudo_legal_moves(board)
        return [m for m in pseudo if self._is_king_safe_after_move(board, m)]

    def is_legal(self, board: Board, move: Move) -> bool:
        return any(
            m.from_sq == move.from_sq and m.to_sq == move.to_sq and m.promotion == move.promotion
            for m in self.legal_moves(board)
        )

    def _pseudo_legal_moves(self, board: Board) -> list[Move]:
        moves: list[Move] = []
        stm = board.side_to_move

        for from_sq, piece in board.pieces.items():
            if piece.color != stm:
                continue

            if piece.kind == PieceType.PAWN:
                moves.extend(self._pawn_forward_moves(board, from_sq, stm))
            elif piece.kind == PieceType.KNIGHT:
                moves.extend(self._knight_moves(board, from_sq, stm))
            elif piece.kind == PieceType.BISHOP:
                moves.extend(self._bishop_moves(board, from_sq, stm))
            elif piece.kind == PieceType.ROOK:
                moves.extend(self._rook_moves(board, from_sq, stm))
            elif piece.kind == PieceType.QUEEN:
                moves.extend(self._queen_moves(board, from_sq, stm))
            elif piece.kind == PieceType.KING:
                moves.extend(self._king_moves(board, from_sq, stm))

        return moves

    def _pawn_forward_moves(self, board: Board, from_sq: int, color: Color) -> list[Move]:
        moves: list[Move] = []

        direction = 8 if color == Color.WHITE else -8
        start_rank = 1 if color == Color.WHITE else 6
        promotion_rank = 7 if color == Color.WHITE else 0
        rank = from_sq // 8

        def add_pawn_move(to_sq: int) -> None:
            if (to_sq // 8) == promotion_rank:
                moves.extend(self._promotion_moves(from_sq, to_sq))
            else:
                moves.append(Move(from_sq=from_sq, to_sq=to_sq))

        one_step = from_sq + direction
        if 0 <= one_step < 64 and one_step not in board.pieces:
            add_pawn_move(one_step)
            if rank == start_rank:
                two_step = from_sq + 2 * direction
                if 0 <= two_step < 64 and two_step not in board.pieces:
                    moves.append(Move(from_sq=from_sq, to_sq=two_step))

        deltas = (7, 9) if color == Color.WHITE else (-9, -7)
        file = from_sq % 8

        for d in deltas:
            to_sq = from_sq + d
            if not (0 <= to_sq < 64):
                continue
            if d in (7, -9) and file == 0:
                continue
            if d in (9, -7) and file == 7:
                continue

            target = board.pieces.get(to_sq)
            if target is not None:
                if target.color == color:
                    continue
                add_pawn_move(to_sq)
                continue

            if board.en_passant_target is not None and to_sq == board.en_passant_target:
                moves.append(Move(from_sq=from_sq, to_sq=to_sq))

        return moves

    def _knight_moves(self, board: Board, from_sq: int, color: Color) -> list[Move]:
        moves: list[Move] = []
        deltas = (
            (2, 1),
            (2, -1),
            (-2, 1),
            (-2, -1),
            (1, 2),
            (1, -2),
            (-1, 2),
            (-1, -2),
        )
        from_rank = from_sq // 8
        from_file = from_sq % 8

        for dr, df in deltas:
            to_rank = from_rank + dr
            to_file = from_file + df
            if not (0 <= to_rank <= 7 and 0 <= to_file <= 7):
                continue
            to_sq = to_rank * 8 + to_file
            target = board.pieces.get(to_sq)
            if target is None or target.color != color:
                moves.append(Move(from_sq=from_sq, to_sq=to_sq))

        return moves

    def _bishop_moves(self, board: Board, from_sq: int, color: Color) -> list[Move]:
        return self._slide_moves(board, from_sq, color, ((1, 1), (1, -1), (-1, 1), (-1, -1)))

    def _rook_moves(self, board: Board, from_sq: int, color: Color) -> list[Move]:
        return self._slide_moves(board, from_sq, color, ((1, 0), (-1, 0), (0, 1), (0, -1)))

    def _queen_moves(self, board: Board, from_sq: int, color: Color) -> list[Move]:
        return self._slide_moves(
            board,
            from_sq,
            color,
            ((1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)),
        )

    def _slide_moves(
        self,
        board: Board,
        from_sq: int,
        color: Color,
        directions: tuple[tuple[int, int], ...],
    ) -> list[Move]:
        moves: list[Move] = []
        from_rank = from_sq // 8
        from_file = from_sq % 8

        for dr, df in directions:
            r = from_rank + dr
            f = from_file + df
            while 0 <= r <= 7 and 0 <= f <= 7:
                to_sq = r * 8 + f
                target = board.pieces.get(to_sq)
                if target is None:
                    moves.append(Move(from_sq=from_sq, to_sq=to_sq))
                else:
                    if target.color != color:
                        moves.append(Move(from_sq=from_sq, to_sq=to_sq))
                    break
                r += dr
                f += df

        return moves

    def _king_moves(self, board: Board, from_sq: int, color: Color) -> list[Move]:
        moves: list[Move] = []
        deltas = (
            (1, 0),
            (-1, 0),
            (0, 1),
            (0, -1),
            (1, 1),
            (1, -1),
            (-1, 1),
            (-1, -1),
        )
        from_rank = from_sq // 8
        from_file = from_sq % 8

        for dr, df in deltas:
            r = from_rank + dr
            f = from_file + df
            if not (0 <= r <= 7 and 0 <= f <= 7):
                continue
            to_sq = r * 8 + f
            target = board.pieces.get(to_sq)
            if target is None or target.color != color:
                moves.append(Move(from_sq=from_sq, to_sq=to_sq))

        opponent = Color.BLACK if color == Color.WHITE else Color.WHITE

        def attacked(sq: int) -> bool:
            return self.is_square_attacked(board, sq, by_color=opponent)

        if color == Color.WHITE and from_sq == square_to_index("e1"):
            if board.castling_rights.wk:
                if (
                    board.pieces.get(square_to_index("f1")) is None
                    and board.pieces.get(square_to_index("g1")) is None
                ):
                    rook = board.pieces.get(square_to_index("h1"))
                    if rook is not None and rook.kind == PieceType.ROOK and rook.color == color:
                        if not attacked(square_to_index("e1")) and not attacked(square_to_index("f1")) and not attacked(square_to_index("g1")):
                            moves.append(Move(from_sq=from_sq, to_sq=square_to_index("g1")))

            if board.castling_rights.wq:
                if (
                    board.pieces.get(square_to_index("d1")) is None
                    and board.pieces.get(square_to_index("c1")) is None
                    and board.pieces.get(square_to_index("b1")) is None
                ):
                    rook = board.pieces.get(square_to_index("a1"))
                    if rook is not None and rook.kind == PieceType.ROOK and rook.color == color:
                        if not attacked(square_to_index("e1")) and not attacked(square_to_index("d1")) and not attacked(square_to_index("c1")):
                            moves.append(Move(from_sq=from_sq, to_sq=square_to_index("c1")))

        elif color == Color.BLACK and from_sq == square_to_index("e8"):
            if board.castling_rights.bk:
                if (
                    board.pieces.get(square_to_index("f8")) is None
                    and board.pieces.get(square_to_index("g8")) is None
                ):
                    rook = board.pieces.get(square_to_index("h8"))
                    if rook is not None and rook.kind == PieceType.ROOK and rook.color == color:
                        if not attacked(square_to_index("e8")) and not attacked(square_to_index("f8")) and not attacked(square_to_index("g8")):
                            moves.append(Move(from_sq=from_sq, to_sq=square_to_index("g8")))

            if board.castling_rights.bq:
                if (
                    board.pieces.get(square_to_index("d8")) is None
                    and board.pieces.get(square_to_index("c8")) is None
                    and board.pieces.get(square_to_index("b8")) is None
                ):
                    rook = board.pieces.get(square_to_index("a8"))
                    if rook is not None and rook.kind == PieceType.ROOK and rook.color == color:
                        if not attacked(square_to_index("e8")) and not attacked(square_to_index("d8")) and not attacked(square_to_index("c8")):
                            moves.append(Move(from_sq=from_sq, to_sq=square_to_index("c8")))

        return moves

    def _is_king_safe_after_move(self, board: Board, move: Move) -> bool:
        b2 = board.clone()
        b2.apply_move(move)
        king_sq = self._find_king_square(b2, color=board.side_to_move)
        if king_sq is None:
            return True
        return not self.is_square_attacked(b2, king_sq, by_color=b2.side_to_move)

    def _find_king_square(self, board: Board, color: Color) -> int | None:
        for sq, piece in board.pieces.items():
            if piece.color == color and piece.kind == PieceType.KING:
                return sq
        return None

    def is_square_attacked(self, board: Board, square: int, by_color: Color) -> bool:
        for from_sq, piece in board.pieces.items():
            if piece.color != by_color:
                continue

            if piece.kind == PieceType.PAWN:
                if self._pawn_attacks_square(from_sq, by_color, square):
                    return True
            elif piece.kind == PieceType.KNIGHT:
                if self._knight_attacks_square(from_sq, square):
                    return True
            elif piece.kind == PieceType.BISHOP:
                if self._ray_attacks_square(board, from_sq, square, ((1, 1), (1, -1), (-1, 1), (-1, -1))):
                    return True
            elif piece.kind == PieceType.ROOK:
                if self._ray_attacks_square(board, from_sq, square, ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    return True
            elif piece.kind == PieceType.QUEEN:
                if self._ray_attacks_square(
                    board,
                    from_sq,
                    square,
                    ((1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)),
                ):
                    return True
            elif piece.kind == PieceType.KING:
                if self._king_attacks_square(from_sq, square):
                    return True

        return False

    def _pawn_attacks_square(self, from_sq: int, color: Color, target_sq: int) -> bool:
        fr, ff = divmod(from_sq, 8)
        tr, tf = divmod(target_sq, 8)
        dr = 1 if color == Color.WHITE else -1
        return tr == fr + dr and abs(tf - ff) == 1

    def _knight_attacks_square(self, from_sq: int, target_sq: int) -> bool:
        fr, ff = divmod(from_sq, 8)
        tr, tf = divmod(target_sq, 8)
        return (abs(tr - fr), abs(tf - ff)) in ((2, 1), (1, 2))

    def _king_attacks_square(self, from_sq: int, target_sq: int) -> bool:
        fr, ff = divmod(from_sq, 8)
        tr, tf = divmod(target_sq, 8)
        return max(abs(tr - fr), abs(tf - ff)) == 1

    def _ray_attacks_square(
        self,
        board: Board,
        from_sq: int,
        target_sq: int,
        directions: tuple[tuple[int, int], ...],
    ) -> bool:
        fr, ff = divmod(from_sq, 8)
        for dr, df in directions:
            r, f = fr + dr, ff + df
            while 0 <= r <= 7 and 0 <= f <= 7:
                sq = r * 8 + f
                if sq == target_sq:
                    return True
                if sq in board.pieces:
                    break
                r += dr
                f += df
        return False

    def _promotion_moves(self, from_sq: int, to_sq: int) -> list[Move]:
        return [
            Move(from_sq=from_sq, to_sq=to_sq, promotion="q"),
            Move(from_sq=from_sq, to_sq=to_sq, promotion="r"),
            Move(from_sq=from_sq, to_sq=to_sq, promotion="b"),
            Move(from_sq=from_sq, to_sq=to_sq, promotion="n"),
        ]

    def is_in_check(self, board: Board, color: Color) -> bool:
        king_sq = self._find_king_square(board, color=color)
        if king_sq is None:
            return True
        opponent = Color.BLACK if color == Color.WHITE else Color.WHITE
        return self.is_square_attacked(board, king_sq, by_color=opponent)

    def is_checkmate(self, board: Board) -> bool:
        stm = board.side_to_move
        return (not self.legal_moves(board)) and self.is_in_check(board, stm)

    def is_stalemate(self, board: Board) -> bool:
        stm = board.side_to_move
        return (not self.legal_moves(board)) and (not self.is_in_check(board, stm))

    def is_insufficient_material(self, board: Board) -> bool:
        non_king = [(sq, p) for sq, p in board.pieces.items() if p.kind != PieceType.KING]
        if not non_king:
            return True

        if len(non_king) == 1:
            _, piece = non_king[0]
            return piece.kind in (PieceType.BISHOP, PieceType.KNIGHT)

        if len(non_king) == 2:
            (sq1, p1), (sq2, p2) = non_king
            if p1.kind == PieceType.BISHOP and p2.kind == PieceType.BISHOP:
                c1 = (sq1 // 8 + sq1 % 8) % 2
                c2 = (sq2 // 8 + sq2 % 8) % 2
                return c1 == c2

        return False

