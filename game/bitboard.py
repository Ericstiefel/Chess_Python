from constants import PieceType, PIECE_SYMBOLS, Color
from bit_ops import *
from constants import Square
from move import Move
import time
from edge_cases import PROMOTION

class State:
    def __init__(self):
        """
        Attributes of toMove and boards   
        """
        self.toMove = 0 # 0: White, 1: Black
        self.boards: list[list[int]] = [[0] * 6, [0] * 6]
        self.reset()

        self.moves: list[tuple] = []

        self.castling: int = 0b1111 # Each of the last 4 bits represent if the side is capable of castling to either side

        self.en_passant: Square = Square.NO_SQUARE # Pawns may only capture to one square in the case of en passant

        self.fifty_move = 0


    def reset(self):
        self.boards[0][PieceType.PAWN] = 0x000000000000FF00
        self.boards[1][PieceType.PAWN] = 0x00FF000000000000
        self.boards[0][PieceType.KNIGHT] = 0x0000000000000042
        self.boards[1][PieceType.KNIGHT] = 0x4200000000000000
        self.boards[0][PieceType.BISHOP] = 0x0000000000000024
        self.boards[1][PieceType.BISHOP] = 0x2400000000000000
        self.boards[0][PieceType.ROOK]   = 0x0000000000000081
        self.boards[1][PieceType.ROOK]   = 0x8100000000000000
        self.boards[0][PieceType.QUEEN]  = 0x0000000000000008
        self.boards[1][PieceType.QUEEN]  = 0x0800000000000000
        self.boards[0][PieceType.KING]   = 0x0000000000000010
        self.boards[1][PieceType.KING]   = 0x1000000000000000
    
    def __str__(self):
        return self.printBoard()
    
    def __repr__(self):
        return self.printBoard()
    
    def __eq__(self, other):
        return (
            self.toMove == other.toMove and
            self.boards == other.boards and
            self.castling == other.castling and
            self.en_passant == other.en_passant
        )

    def __hash__(self):
        boards_tuple = tuple(
            self.boards[color][piece] for color in (0, 1) for piece in range(6)
        )
        return hash((self.toMove, boards_tuple, self.castling, self.en_passant))


    def printBoard(self):
        board = [['.' for _ in range(8)] for _ in range(8)]

        for color in (0, 1):
            for piece_type in range(6):
                bb = self.boards[color][piece_type]
                for sq in range(64):
                    if get_bit(bb, sq):
                        row = 7 - (sq // 8)  # Rank 8 → 0
                        col = sq % 8
                        board[row][col] = PIECE_SYMBOLS[color][piece_type]

        print("  +------------------------+")
        for i, row in enumerate(board):
            print(f"{8 - i} | {' '.join(row)} |")
        print("  +------------------------+")
        print("    a b c d e f g h")

    def printBitBoard(self, color: Color, piece: PieceType):
        bb = self.boards[color][piece]
        print(f"\nBitboard for {PIECE_SYMBOLS[color][piece]} ({'White' if color == 0 else 'Black'}):")
        print("  +------------------------+")
        for rank in range(8):
            row_str = f"{8 - rank} | "
            for file in range(8):
                sq = (7 - rank) * 8 + file  # ranks printed top-down
                row_str += f"{'1' if get_bit(bb, sq) else '.'} "
            row_str += "|"
            print(row_str)
        print("  +------------------------+")
        print("    a b c d e f g h")

    def get_all_occupied_squares(self) -> int:
        occupied = 0
        for pt in PieceType:
            occupied |= self.boards[Color.WHITE][pt]
            occupied |= self.boards[Color.BLACK][pt]

        return occupied
    
    def get_occupied_by_color(self, color: Color) -> int:
        occupied_bb = 0
        for pt in PieceType:
            occupied_bb |= self.boards[color][pt]
        return occupied_bb
    
    def piece_on_square(self, square: Square) -> PieceType | None:
        mask = 1 << square
        for pt in PieceType:
            if (self.boards[0][pt] | self.boards[1][pt]) & mask:
                return pt
        return None
    
    def piece_on_square_by_color(self, square: Square, color: Color) -> PieceType | None:
        mask = 1 << square
        for pt in PieceType:
            if (self.boards[color][pt]) & mask:
                return pt
        return None

    
    def color_on_square(self, sq: Square) -> Color | None:
        mask = 1 << sq
        for color in range(2):
            combined_bb = self.boards[color][PieceType.PAWN] | self.boards[color][PieceType.KNIGHT] | self.boards[color][PieceType.BISHOP] | self.boards[color][PieceType.ROOK] | self.boards[color][PieceType.QUEEN] | self.boards[color][PieceType.KING]
            if mask & combined_bb:
                return color
        return None
    
    def move_piece(self, move: Move):
        old_castling = self.castling
        old_en_passant = self.en_passant
        old_fifty = self.fifty_move
        self.moves.append((move, None, old_castling, old_en_passant, old_fifty))

        self.boards[self.toMove][move.piece_type] = set_bit(clear_bit(self.boards[self.toMove][move.piece_type], move.from_sq), move.to_sq)  
    
    def capture(self, move: Move) -> None:
        old_castling = self.castling
        old_en_passant = self.en_passant
        old_fifty = self.fifty_move
        captured_piece = None
        if move.is_en_passant:
            captured_sq = move.to_sq - 8 if move.color == Color.WHITE else move.to_sq + 8
            captured_piece = self.piece_on_square(captured_sq)
        else:
            captured_piece = self.piece_on_square(move.to_sq)

        self.moves.append((move, captured_piece, old_castling, old_en_passant, old_fifty))

        curr_player = self.toMove 

        self.boards[curr_player ^ 1][captured_piece] = clear_bit(self.boards[curr_player ^ 1][captured_piece], move.to_sq)

        self.boards[curr_player][move.piece_type] = set_bit(
            clear_bit(self.boards[curr_player][move.piece_type], move.from_sq), move.to_sq
        )

    
    def castle(self, move: Move) -> None:
        old_castling = self.castling
        old_en_passant = self.en_passant
        old_fifty = self.fifty_move
        captured_piece = None

        self.moves.append((move, captured_piece, old_castling, old_en_passant, old_fifty))

        color = self.toMove
        k_b = self.boards[color][PieceType.KING]
        r_b = self.boards[color][PieceType.ROOK]
        to_sq = move.to_sq

        if color == Color.WHITE:
            if to_sq == Square.G1:  # Kingside
                k_b = set_bit(clear_bit(k_b, Square.E1), Square.G1)
                r_b = set_bit(clear_bit(r_b, Square.H1), Square.F1)
                self.castling &= ~0b0001  # Clear White kingside
            elif to_sq == Square.C1:  # Queenside
                k_b = set_bit(clear_bit(k_b, Square.E1), Square.C1)
                r_b = set_bit(clear_bit(r_b, Square.A1), Square.D1)
                self.castling &= ~0b0010  # Clear White queenside
        else:
            if to_sq == Square.G8:  # Kingside
                k_b = set_bit(clear_bit(k_b, Square.E8), Square.G8)
                r_b = set_bit(clear_bit(r_b, Square.H8), Square.F8)
                self.castling &= ~0b0100  # Clear Black kingside
            elif to_sq == Square.C8:  # Queenside
                k_b = set_bit(clear_bit(k_b, Square.E8), Square.C8)
                r_b = set_bit(clear_bit(r_b, Square.A8), Square.D8)
                self.castling &= ~0b1000  # Clear Black queenside

        self.boards[color][PieceType.KING] = k_b
        self.boards[color][PieceType.ROOK] = r_b

    def promote(self, move: Move):
        old_castling = self.castling
        old_en_passant = self.en_passant
        old_fifty = self.fifty_move
        captured_piece = None
        if move.is_capture:
            captured_piece = self.piece_on_square(move.to_sq)

        self.moves.append((move, captured_piece, old_castling, old_en_passant, old_fifty))

        piece_on_square: PieceType | None = self.piece_on_square_by_color(move.to_sq, move.color)

        if piece_on_square:
            clear_bit(self.boards[self.toMove ^ 1][piece_on_square], move.to_sq)

        self.boards[self.toMove][PieceType.PAWN] = clear_bit(self.boards[self.toMove][PieceType.PAWN], move.from_sq)
        self.boards[self.toMove][move.promotion_type] = set_bit(self.boards[self.toMove][move.promotion_type], move.to_sq)

    def en_passant(self, move: Move):
        old_castling = self.castling
        old_en_passant = self.en_passant
        old_fifty = self.fifty_move
        captured_piece = self.piece_on_square(move.to_sq)
        captured_sq = move.to_sq - 8 if self.toMove == Color.WHITE else move.to_sq + 8

    
        self.moves.append((move, captured_piece, old_castling, old_en_passant, old_fifty))


        self.boards[self.toMove][PieceType.PAWN] = set_bit(clear_bit(self.boards[self.toMove][PieceType.PAWN], move.from_sq), move.to_sq)

        self.boards[self.toMove ^ 1][PieceType.PAWN] = clear_bit(self.boards[self.toMove ^ 1][PieceType.PAWN], captured_sq)

        self.en_passant = Square.NO_SQUARE

    def unmake_move(self):
        if not self.moves:
            return

        move, captured_piece, old_castling, old_en_passant, old_fifty = self.moves.pop()

        self.toMove = move.color
        self.castling = old_castling
        self.en_passant = old_en_passant
        self.fifty_move = old_fifty

        color = move.color
        opp_color = color ^ 1
        from_sq = move.from_sq
        to_sq = move.to_sq

        if move.is_castle:
            # Reverse castling move
            if color == Color.WHITE:
                if to_sq == Square.G1:  # Kingside
                    self.boards[color][PieceType.KING] = set_bit(clear_bit(self.boards[color][PieceType.KING], Square.G1), Square.E1)
                    self.boards[color][PieceType.ROOK] = set_bit(clear_bit(self.boards[color][PieceType.ROOK], Square.F1), Square.H1)
                elif to_sq == Square.C1:  # Queenside
                    self.boards[color][PieceType.KING] = set_bit(clear_bit(self.boards[color][PieceType.KING], Square.C1), Square.E1)
                    self.boards[color][PieceType.ROOK] = set_bit(clear_bit(self.boards[color][PieceType.ROOK], Square.D1), Square.A1)
            else:
                if to_sq == Square.G8:
                    self.boards[color][PieceType.KING] = set_bit(clear_bit(self.boards[color][PieceType.KING], Square.G8), Square.E8)
                    self.boards[color][PieceType.ROOK] = set_bit(clear_bit(self.boards[color][PieceType.ROOK], Square.F8), Square.H8)
                elif to_sq == Square.C8:
                    self.boards[color][PieceType.KING] = set_bit(clear_bit(self.boards[color][PieceType.KING], Square.C8), Square.E8)
                    self.boards[color][PieceType.ROOK] = set_bit(clear_bit(self.boards[color][PieceType.ROOK], Square.D8), Square.A8)

        elif move.is_en_passant:
            self.boards[color][PieceType.PAWN] = set_bit(clear_bit(self.boards[color][PieceType.PAWN], to_sq), from_sq)
            captured_sq = to_sq - 8 if color == Color.WHITE else to_sq + 8
            self.boards[opp_color][PieceType.PAWN] = set_bit(self.boards[opp_color][PieceType.PAWN], captured_sq)
            self.en_passant = captured_sq

        elif move.promotion_type != PieceType.PAWN:
            self.boards[color][move.promotion_type] = clear_bit(self.boards[color][move.promotion_type], to_sq)
            self.boards[color][PieceType.PAWN] = set_bit(self.boards[color][PieceType.PAWN], from_sq)

        else:
            self.boards[color][move.piece_type] = clear_bit(self.boards[color][move.piece_type], to_sq)
            self.boards[color][move.piece_type] = set_bit(self.boards[color][move.piece_type], from_sq)

        if move.is_capture and captured_piece is not None and not move.is_en_passant:
            self.boards[opp_color][captured_piece] = set_bit(self.boards[opp_color][captured_piece], to_sq)



if __name__ == '__main__':
    game = State()

    game.move_piece(Move(Color.WHITE, PieceType.PAWN, Square.E2, Square.E4))
    game.move_piece(Move(Color.BLACK, PieceType.PAWN, Square.H7, Square.H5))
    game.move_piece(Move(Color.WHITE, PieceType.PAWN, Square.E4, Square.E5))
    game.move_piece(Move(Color.BLACK, PieceType.PAWN, Square.D7, Square.D5))
    game.en_passant = Square.D6
    sum = 0
    # computer warmup
    for i in range(1000):
        sum += i

    begin_time = time.time()

    for _ in range(10000):
        game.en_passant(Move(Color.WHITE, PieceType.PAWN, Square.E5, Square.D6, is_en_passant=True))

    end_time = time.time()

    print('Results: ', (end_time - begin_time) / (10000), 'seconds')
