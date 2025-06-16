from enum import IntEnum, auto


class Square(IntEnum):
    A1 = 0; B1 = 1; C1 = 2; D1 = 3; E1 = 4; F1 = 5; G1 = 6; H1 = 7
    A2 = 8; B2 = 9; C2 = 10; D2 = 11; E2 = 12; F2 = 13; G2 = 14; H2 = 15
    A3 = 16; B3 = 17; C3 = 18; D3 = 19; E3 = 20; F3 = 21; G3 = 22; H3 = 23
    A4 = 24; B4 = 25; C4 = 26; D4 = 27; E4 = 28; F4 = 29; G4 = 30; H4 = 31
    A5 = 32; B5 = 33; C5 = 34; D5 = 35; E5 = 36; F5 = 37; G5 = 38; H5 = 39
    A6 = 40; B6 = 41; C6 = 42; D6 = 43; E6 = 44; F6 = 45; G6 = 46; H6 = 47
    A7 = 48; B7 = 49; C7 = 50; D7 = 51; E7 = 52; F7 = 53; G7 = 54; H7 = 55
    A8 = 56; B8 = 57; C8 = 58; D8 = 59; E8 = 60; F8 = 61; G8 = 62; H8 = 63
    NO_SQUARE = auto()

class PieceType(IntEnum):
    PAWN = 0
    KNIGHT = 1
    BISHOP = 2
    ROOK = 3
    QUEEN = 4
    KING = 5

class Color(IntEnum):
    WHITE = 0
    BLACK = 1

PIECE_SYMBOLS = [
    ['P', 'N', 'B', 'R', 'Q', 'K'],   # White
    ['p', 'n', 'b', 'r', 'q', 'k'],   # Black
]

SQUARE_NAMES = [
    "a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1", # Rank 1
    "a2", "b2", "c2", "d2", "e2", "f2", "g2", "h2", # Rank 2
    "a3", "b3", "c3", "d3", "e3", "f3", "g3", "h3", # Rank 3
    "a4", "b4", "c4", "d4", "e4", "f4", "g4", "h4", # Rank 4
    "a5", "b5", "c5", "d5", "e5", "f5", "g5", "h5", # Rank 5
    "a6", "b6", "c6", "d6", "e6", "f6", "g6", "h6", # Rank 6
    "a7", "b7", "c7", "d7", "e7", "f7", "g7", "h7", # Rank 7
    "a8", "b8", "c8", "d8", "e8", "f8", "g8", "h8", # Rank 8
]

RANK_1 = 0xFF        # 0b0000000011111111 (for index 0-7)
RANK_2 = 0xFF00      # for index 8-15
RANK_7 = 0xFF000000000000  # for index 48-55
RANK_8 = 0xFF00000000000000 # for index 56-63

FILE_A = 0x0101010101010101 # Every 8th bit starting from bit 0
FILE_H = 0x8080808080808080 # Every 8th bit starting from bit 7

KNIGHT_OFFSETS = [17, 15, 10, 6, -6, -10, -15, -17]