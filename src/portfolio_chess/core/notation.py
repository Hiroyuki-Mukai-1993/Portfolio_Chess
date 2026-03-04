from __future__ import annotations

from .board import Board
from .move import Move
from .rules import Rules
from .types import PieceType, index_to_square


def move_to_san(board_before: Board, move: Move, rules: Rules) -> str:
    piece = board_before.pieces.get(move.from_sq)
    if piece is None:
        raise ValueError("No piece on from_sq for SAN generation.")

    from_file = move.from_sq % 8
    to_sq_name = index_to_square(move.to_sq)

    target = board_before.pieces.get(move.to_sq)
    is_ep_capture = (
        piece.kind == PieceType.PAWN
        and board_before.en_passant_target is not None
        and move.to_sq == board_before.en_passant_target
        and target is None
        and (move.from_sq % 8) != (move.to_sq % 8)
    )
    is_capture = target is not None or is_ep_capture

    if piece.kind == PieceType.KING and abs((move.to_sq % 8) - (move.from_sq % 8)) == 2:
        san = "O-O" if (move.to_sq % 8) > (move.from_sq % 8) else "O-O-O"
    else:
        piece_letter = {
            PieceType.KING: "K",
            PieceType.QUEEN: "Q",
            PieceType.ROOK: "R",
            PieceType.BISHOP: "B",
            PieceType.KNIGHT: "N",
            PieceType.PAWN: "",
        }[piece.kind]

        disambiguation = ""
        if piece.kind != PieceType.PAWN:
            alternatives = []
            for cand in rules.legal_moves(board_before):
                if cand.to_sq != move.to_sq or cand.from_sq == move.from_sq:
                    continue
                cand_piece = board_before.pieces.get(cand.from_sq)
                if cand_piece is None:
                    continue
                if cand_piece.color == piece.color and cand_piece.kind == piece.kind:
                    alternatives.append(cand)

            if alternatives:
                same_file_exists = any((a.from_sq % 8) == (move.from_sq % 8) for a in alternatives)
                same_rank_exists = any((a.from_sq // 8) == (move.from_sq // 8) for a in alternatives)

                from_sq_name = index_to_square(move.from_sq)
                if not same_file_exists:
                    disambiguation = from_sq_name[0]
                elif not same_rank_exists:
                    disambiguation = from_sq_name[1]
                else:
                    disambiguation = from_sq_name

        if piece.kind == PieceType.PAWN and is_capture:
            disambiguation = "abcdefgh"[from_file]

        capture_token = "x" if is_capture else ""
        promotion = ""
        if move.promotion is not None:
            promotion = f"={move.promotion.upper()}"

        san = f"{piece_letter}{disambiguation}{capture_token}{to_sq_name}{promotion}"

    b2 = board_before.clone()
    b2.apply_move(move)
    if rules.is_checkmate(b2):
        san += "#"
    elif rules.is_in_check(b2, b2.side_to_move):
        san += "+"

    return san


def san_moves_to_pgn(san_moves: list[str], result: str) -> str:
    chunks: list[str] = []
    for i in range(0, len(san_moves), 2):
        turn = i // 2 + 1
        if i + 1 < len(san_moves):
            chunks.append(f"{turn}. {san_moves[i]} {san_moves[i + 1]}")
        else:
            chunks.append(f"{turn}. {san_moves[i]}")

    moves_text = " ".join(chunks).strip()
    if moves_text:
        moves_text = f"{moves_text} {result}"
    else:
        moves_text = result
    return moves_text
