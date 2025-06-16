from bitboard import State
from constants import Color, PieceType, Square
from bit_ops import *
from move import Move
from legal_moves import *
from legal_king_moves import castleMoves, is_in_check


def make_move(state: State, move: Move) -> bool:
    if state.piece_on_square(move.from_sq) == PieceType.PAWN:
        state.fifty_move = 0

    if move.is_castle:
        king_moves = castleMoves(state)

        if move not in king_moves:
            return False
        
        state.fifty_move = 0        
        state.castle(move.to_sq)

        return True
    
    opp_tot_bb = state.get_occupied_by_color(state.toMove ^ 1)

    move.is_capture = get_bit(opp_tot_bb, move.to_sq)
    
    if move.promotion_type != PieceType.PAWN:
        pawn_moves = pawnMoves(state)

        if move not in pawn_moves:
            state.printBoard()
            print([move_ex.notation() for move_ex in pawn_moves])
            return False
        
        state.fifty_move = 0
        state.promote(move.from_sq, move.to_sq, move.promotion_type)
        return True
    if move.is_en_passant:
        pawn_moves = pawnMoves(state)
        state.printBoard()
        print([move_ex.notation() for move_ex in pawn_moves])
        if move not in pawn_moves:
            return False
        
        state.fifty_move = 0
        state.en_passant(move.from_sq, move.to_sq)
        return True
    
    moves = legal_moves(state)
    if move not in moves:
        print([move_ex.notation() for move_ex in moves])
        return False
    
    if move.is_capture:
        state.fifty_move = 0
        state.capture(move.piece_type, move.from_sq, move.to_sq)
        return True
    
    state.move_piece(move.piece_type, move.from_sq, move.to_sq)
    
    return True 

def turn(state: State, move: Move):
    # Save current state before making the move
    old_castling = state.castling
    old_en_passant = state.en_passant
    old_fifty = state.fifty_move

    # Determine captured piece (only needed if it's a capture or en passant)
    captured_piece = None
    if move.is_capture:
        if move.is_en_passant:
            captured_sq = move.to_sq - 8 if move.color == Color.WHITE else move.to_sq + 8
            captured_piece = state.piece_on_square(captured_sq)
        else:
            captured_piece = state.piece_on_square(move.to_sq)

    if make_move(state, move):
        state.toMove ^= 1

        if is_in_check(state):
            move.is_check = True

        state.moves.append((move, captured_piece, old_castling, old_en_passant, old_fifty))
        return True
    else:
        
        state.printBoard()
        print(f'Invalid Move : {move.notation()}')
        print(f'Move From_sq: {move.from_sq}, Move To_sq: {move.to_sq}, Promotion: {move.promotion_type}, is_capture: {move.is_capture}')
        return False


if __name__ == '__main__':
    state = State()
    move = Move(state.toMove, PieceType.PAWN, Square.E2, Square.E4)
    turn(state, move)
    state.printBoard()
    state.unmake_move()
    state.printBoard()