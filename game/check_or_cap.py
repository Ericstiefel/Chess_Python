from utils import is_square_attacked
from constants import Square, Color, PieceType
from bitboard import State
from move import Move
from bit_ops import *
import sys

def is_capture(state: State, move: Move) -> bool:
    # 1. En passant capture
    if move.is_en_passant:
        return True

    # 2. Normal capture (destination square occupied by opponent's piece)
    opponent_occupied_bb = state.get_occupied_by_color(state.toMove ^ 1)
    return get_bit(opponent_occupied_bb, move.to_sq.value)

def is_check(state: State, move: Move) -> bool:
    state.toMove ^= 1
    king_sq = lsb_index(state.boards[state.toMove][PieceType.KING])
    in_check = is_square_attacked(state, Square(king_sq))

    state.toMove ^= 1
    return in_check

def annotate_moves_with_check_and_capture(state: State, moves: list[Move]):
    
    annotated_moves = []
    for move in moves:
        
        target_piece = state.piece_on_square(move.to_sq)
        
        move.is_capture = target_piece is not None or move.is_en_passant
        if move.is_capture and move.promotion_type == PieceType.PAWN:
            if move.is_en_passant:
                state.en_passant()
            else:
                state.capture(move)
        elif move.promotion_type != PieceType.PAWN:
            state.promote(move)

        elif move.is_castle:
            state.castle(move)

        else:
            state.move_piece(move)

        move.is_check = is_check(state, move)

        state.unmake_move()

        annotated_moves.append(move)

    return annotated_moves
