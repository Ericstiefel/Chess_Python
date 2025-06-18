from move import Move
from constants import *
THREEFOLD =  [
    Move(Color.WHITE, PieceType.PAWN, Square.A2, Square.A4),
    Move(Color.BLACK, PieceType.PAWN, Square.A7, Square.A5),  
    Move(Color.WHITE, PieceType.KNIGHT, Square.G1, Square.F3),
    Move(Color.BLACK, PieceType.KNIGHT, Square.G8, Square.F6),  
    Move(Color.WHITE, PieceType.KNIGHT, Square.F3, Square.G1),
    Move(Color.BLACK, PieceType.KNIGHT, Square.F6, Square.G8),  
    Move(Color.WHITE, PieceType.KNIGHT, Square.G1, Square.F3),
    Move(Color.BLACK, PieceType.KNIGHT, Square.G8, Square.F6),
    Move(Color.WHITE, PieceType.KNIGHT, Square.F3, Square.G1),
    Move(Color.BLACK, PieceType.KNIGHT, Square.F6, Square.G8)

]

PROMOTION = [
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

CASTLING = [
    Move(Color.WHITE, PieceType.PAWN, Square.E2, Square.E4),
    Move(Color.BLACK, PieceType.PAWN, Square.E7, Square.E5),  
    Move(Color.WHITE, PieceType.KNIGHT, Square.G1, Square.F3),
    Move(Color.BLACK, PieceType.KNIGHT, Square.G8, Square.F6),  
    Move(Color.WHITE, PieceType.BISHOP, Square.F1, Square.C4),
    Move(Color.BLACK, PieceType.BISHOP, Square.F8, Square.C5),  
    Move(Color.WHITE, PieceType.KING, Square.E1, Square.G1, is_castle = True),
    Move(Color.BLACK, PieceType.KING, Square.E8, Square.G8, is_castle = True)
]
