from bitboard import State
from constants import Color, PieceType, Square
from bit_ops import *
from move import Move
from legal_moves import *
from legal_king_moves import castleMoves


def make_move(state: State, move: Move) -> bool:

    state.fifty_move += 1
    if move.piece_type == PieceType.PAWN or move.is_capture:
        state.fifty_move = 0

    if move.is_castle:

        state.castle(move)

        state.fifty_move = 0

        return True

    
    opp_tot_bb = state.get_occupied_by_color(state.toMove ^ 1)

    move.is_capture = get_bit(opp_tot_bb, move.to_sq)
    
    if move.promotion_type != PieceType.PAWN:
        pawn_moves = pawnMoves(state)

        if move not in pawn_moves:

            return False

        state.promote(move)
        return True

    if move.is_en_passant:
        pawn_moves = pawnMoves(state)
        if move not in pawn_moves:
            return False

        state.en_passant(move)

        return True    
    
    moves = legal_moves(state)

    
    if move not in moves:
        return False
    
    if move.is_capture:
        state.fifty_move = 0
        state.capture(move)
        return True
    
    state.move_piece(move)
    
    return True 

def turn(state: State, move: Move):

    if make_move(state, move):
        if move.piece_type == PieceType.KING:
            if move.color == Color.WHITE:
                state.castling &= ~0b0011 
            else:
                state.castling &= ~0b1100 
        elif move.piece_type == PieceType.ROOK:
            if move.color == Color.WHITE:
                if move.from_sq == Square.H1:
                    state.castling &= ~0b0001  
                elif move.from_sq == Square.A1:
                    state.castling &= ~0b0010 
            else:
                if move.from_sq == Square.H8:
                    state.castling &= ~0b0100 
                elif move.from_sq == Square.A8:
                    state.castling &= ~0b1000  
        state.toMove ^= 1
        return True
    else:  
        return False


if __name__ == '__main__':
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