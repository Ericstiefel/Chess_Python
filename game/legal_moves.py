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

    for move in king_moves:
            total_moves.append(move)

    if attackers_count == 2:
        return total_moves  

    if attackers_count == 1:
        # If in single check, pieces can only move to capture the checker or block its path.
        checker_sq = lsb_index(attackers_bb)
        valid_targets = 1 << checker_sq  # The checker's square is a valid target, assuming only attacker

        checker_piece = state.piece_on_square(checker_sq)
        if checker_piece and checker_piece in (PieceType.BISHOP, PieceType.ROOK, PieceType.QUEEN):
            
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


if __name__ == '__main__':
    state = State()
    
    for _ in range(1000):
        legal_moves(state)

    start = time.time()

    for _ in range(10000):
        legal_moves(state)
    end = time.time()

    print('Avg Time Elapsed: ', (end - start) / 10000)

