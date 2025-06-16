from bitboard import State
from constants import Color, PieceType, Square
from bit_ops import *
from move import Move
from legal_moves import *
from legal_king_moves import castleMoves, is_in_check


def make_move(state: State, move: Move) -> bool:
    if move.piece_type == PieceType.PAWN or move.is_capture:
        state.fifty_move = 0

    if move.is_castle:
        king_moves = castleMoves(state)

        print('Castling')

        state.printBoard()
        print([move_ex.notation() for move_ex in pawn_moves])

        if move not in king_moves:
            return False

        state.castle(move)

        state.fifty_move = 0

        return True
    
    opp_tot_bb = state.get_occupied_by_color(state.toMove ^ 1)

    move.is_capture = get_bit(opp_tot_bb, move.to_sq)
    
    if move.promotion_type != PieceType.PAWN:
        pawn_moves = pawnMoves(state)

        if move not in pawn_moves:
            state.printBoard()
            print('Move not in pawn_moves')
            print([move_ex.notation() for move_ex in pawn_moves])
            return False

        state.promote(move)
        return True

    if move.is_en_passant:
        pawn_moves = pawnMoves(state)
        print('En Passant')
        state.printBoard()
        print([move_ex.notation() for move_ex in pawn_moves])
        if move not in pawn_moves:
            return False

        state.en_passant(move)

        state.printBoard()

        return True
    
    moves = legal_moves(state)
    if move not in moves:
        print([move_ex.notation() for move_ex in moves])
        return False
    
    if move.is_capture:
        state.fifty_move = 0
        state.capture(move)
        return True
    
    state.move_piece(move)
    
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
        return False


if __name__ == '__main__':
    state = State()
    state = State()
    moves = [
    Move(Color.WHITE, PieceType.PAWN, Square.A2, Square.A4),
    Move(Color.BLACK, PieceType.PAWN, Square.H7, Square.H6),  # Waiting move
    Move(Color.WHITE, PieceType.PAWN, Square.A4, Square.A5),
    Move(Color.BLACK, PieceType.PAWN, Square.H6, Square.H5),  # Waiting move
    Move(Color.WHITE, PieceType.PAWN, Square.A5, Square.A6),
    Move(Color.BLACK, PieceType.KNIGHT, Square.G8, Square.H6),  # Just getting out of the way
    Move(Color.WHITE, PieceType.ROOK, Square.A1, Square.A3),
    Move(Color.BLACK, PieceType.KNIGHT, Square.H6, Square.G8),  # Waiting
    Move(Color.WHITE, PieceType.ROOK, Square.A3, Square.F3),
    Move(Color.BLACK, PieceType.KNIGHT, Square.G8, Square.H6),
    Move(Color.WHITE, PieceType.PAWN, Square.A6, Square.B7),
    Move(Color.BLACK, PieceType.KNIGHT, Square.B8, Square.C6),
    Move(Color.WHITE, PieceType.PAWN, Square.B7, Square.B8, promotion_type=PieceType.QUEEN),
]

    for move in moves:
        state.printBoard()
        print('Legal Moves: ', [legal.notation() for legal in legal_moves(state)])
        print('Move Chosen', move.notation())
        turn(state, move)