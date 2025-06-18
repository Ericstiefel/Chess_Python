from check import pinned
from possible_piece_moves import *
from utils import is_square_attacked, attackers_to_square, squares_between, is_along_ray
from bitboard import State
from move import Move
from bit_ops import *
from legal_king_moves import kingMoves
from check_or_cap import is_check, is_capture, annotate_moves_with_check_and_capture
import time


def legal_moves(state: State) -> list[Move]:
    
    total_moves: list[Move] = []

    king_loc = lsb_index(state.boards[state.toMove][PieceType.KING])
    
    
    attackers_bb = attackers_to_square(state, Square(king_loc))
    

    attackers_count = popcount(attackers_bb)  
    in_check = attackers_count > 0
    king_moves = annotate_moves_with_check_and_capture(state, kingMoves(state, attackers_count))
    # Always allow legal king moves
    for move in king_moves:
            total_moves.append(move)

    if attackers_count == 2:
        return total_moves  # Only king moves allowed

    if attackers_count == 1:
        # If in single check, pieces can only move to capture the checker or block its path.
        checker_sq = lsb_index(attackers_bb)
        valid_targets = 1 << checker_sq  # The checker's square is a valid target.

        checker_piece = state.piece_on_square(checker_sq)
        if checker_piece and checker_piece in (PieceType.BISHOP, PieceType.ROOK, PieceType.QUEEN):
            # If the checker is a slider, blocking squares are also valid targets.
            
            valid_targets |= squares_between(king_loc, checker_sq)
    else:
        # If not in check, all squares are potentially valid targets.
        valid_targets = 0xFFFFFFFFFFFFFFFF

    gen_funcs = [pawnMoves, knightMoves, bishopMoves, rookMoves, queenMoves]

    moves = [move 
         for gen_func in gen_funcs 
         for move in annotate_moves_with_check_and_capture(state, gen_func(state))]

    for move in moves:
        
        piece_pinned: bool = pinned(state, move.from_sq, king_loc)
        square_bit = 1 << move.to_sq

        if in_check:
            if ((square_bit & valid_targets) != 0) and not piece_pinned: 
                total_moves.append(move)
            continue
        if piece_pinned:
            if is_along_ray(king_loc, move.from_sq, move.to_sq):
                total_moves.append(move)
            continue  # Pinned piece moving illegally
        if ((1 << move.to_sq) & valid_targets):
            total_moves.append(move)

    return total_moves

def _filter_moves(state: State, piece_type: PieceType, move_gen_fn) -> list[Move]:
    legal = []
    king_loc = lsb_index(state.boards[state.toMove][PieceType.KING])

    attackers_bb = attackers_to_square(state, Square(king_loc))
    attackers_count = popcount(attackers_bb)
    in_check = attackers_count > 0

    if attackers_count == 1:
        checker_sq = lsb_index(attackers_bb)
        checker_mask = 1 << checker_sq
        valid_targets = checker_mask

        checker_piece = state.piece_on_square(checker_sq)
        if checker_piece and checker_piece[1] in (PieceType.BISHOP, PieceType.ROOK, PieceType.QUEEN):
            valid_targets |= squares_between(king_loc, checker_sq)
    else:
        valid_targets = 0xFFFFFFFFFFFFFFFF  # All squares

    for move in move_gen_fn(state):
        if move.from_sq == king_loc:
            continue  # Only handle non-king pieces here
        if pinned(state, piece_type, move.from_sq) and not is_along_ray(king_loc, move.from_sq, move.to_sq):
            continue
        if not in_check or ((1 << move.to_sq) & valid_targets):
            legal.append(move)

    return legal


def pawn(state: State) -> list[Move]:
    return _filter_moves(state, PieceType.PAWN, pawnMoves)

def knight(state: State) -> list[Move]:
    return _filter_moves(state, PieceType.KNIGHT, knightMoves)

def bishop(state: State) -> list[Move]:
    return _filter_moves(state, PieceType.BISHOP, bishopMoves)

def rook(state: State) -> list[Move]:
    return _filter_moves(state, PieceType.ROOK, rookMoves)

def queen(state: State) -> list[Move]:
    return _filter_moves(state, PieceType.QUEEN, queenMoves)

def king(state: State) -> list[Move]:
    return [move for move in kingMoves(state) if not is_square_attacked(state, Square(move.to_sq))]


if __name__ == '__main__':
    state = State()
    
    for _ in range(1000):
        legal_moves(state)

    start = time.time()

    for _ in range(10000):
        legal_moves(state)
    end = time.time()

    print('Avg Time Elapsed: ', (end - start) / 10000)

