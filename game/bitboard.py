from constants import PieceType, PIECE_SYMBOLS, Color
from bit_ops import *
from constants import Square
from move import Move

class State:
    def __init__(self):
        """
        Attributes of toMove and boards   
        """
        self.toMove = 0 # 0: White, 1: Black
        self.boards: list[list[int]] = [[0] * 6, [0] * 6]
        self.reset()

        self.moves: list[tuple] = []

        self.castling: int = 0 # Each of the last 4 bits represent if the side is capable of castling to either side

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
        white_occupied = 0
        for pt in PieceType:
            white_occupied |= self.boards[Color.WHITE][pt.value]
        black_occupied = 0
        for pt in PieceType:
            black_occupied |= self.boards[Color.BLACK][pt.value]
        return white_occupied | black_occupied
    

    def get_occupied_by_color(self, color: Color) -> int:
        occupied_bb = 0
        for pt in PieceType:
            occupied_bb |= self.boards[color][pt]
        return occupied_bb
    
    def piece_on_square(self, square: Square):
        mask = 1 << square
        for color in [Color.WHITE, Color.BLACK]:
            for piece_type in PieceType:
                if self.boards[color][piece_type] & mask:
                    return piece_type
        return None
    def color_on_square(self, sq: int) -> Color | None:
        for color in (Color.WHITE, Color.BLACK):
            for piece in range(6):  # 0 to 5 for PieceType
                if get_bit(self.boards[color][piece], sq):
                    return color
        return None

    
    def move_piece(self, piece: PieceType, from_sq: Square, to_sq: Square):
        u_bb = self.boards[self.toMove][piece]

        u_bb = clear_bit(u_bb, from_sq)

        u_bb = set_bit(u_bb, to_sq)

        self.boards[self.toMove][piece] = u_bb        
    
    def capture(self, piece: PieceType, from_sq: Square, to_sq: Square) -> None:
        curr_player = self.toMove 

        # Handle capture
        for piece_board_idx in range(6):
            op_bb = self.boards[curr_player ^ 1][piece_board_idx]
            if get_bit(op_bb, to_sq):
                self.boards[curr_player ^ 1][piece_board_idx] = clear_bit(op_bb, to_sq)
                break

        # Move piece
        self.boards[curr_player][piece] = clear_bit(self.boards[curr_player][piece], from_sq)
        self.boards[curr_player][piece] = set_bit(self.boards[curr_player][piece], to_sq)

    
    def castle(self, to_sq: Square) -> None:
        color = self.toMove
        k_b = self.boards[color][PieceType.KING]
        r_b = self.boards[color][PieceType.ROOK]

        if color == Color.WHITE:
            # King always starts at E1 (4)
            if to_sq == Square.G1:  # Kingside
                k_b = set_bit(clear_bit(k_b, Square.E1), Square.G1)
                r_b = set_bit(clear_bit(r_b, Square.H1), Square.F1)
            elif to_sq == Square.C1:  # Queenside
                k_b = set_bit(clear_bit(k_b, Square.E1), Square.C1)
                r_b = set_bit(clear_bit(r_b, Square.A1), Square.D1)
        else:
            # King always starts at E8 (60)
            if to_sq == Square.G8:  # Kingside
                k_b = set_bit(clear_bit(k_b, Square.E8), Square.G8)
                r_b = set_bit(clear_bit(r_b, Square.H8), Square.F8)
            elif to_sq == Square.C8:  # Queenside
                k_b = set_bit(clear_bit(k_b, Square.E8), Square.C8)
                r_b = set_bit(clear_bit(r_b, Square.A8), Square.D8)

        self.boards[color][PieceType.KING] = k_b
        self.boards[color][PieceType.ROOK] = r_b


    def promote(self, from_sq: Square, to_sq: Square, promotion_piece: PieceType):

        for pt in range(6):
            if get_bit(self.boards[self.toMove ^ 1][pt], to_sq):
                self.boards[self.toMove ^ 1][pt] = clear_bit(self.boards[self.toMove ^ 1][pt], to_sq)
                break

        self.boards[self.toMove][PieceType.PAWN] = clear_bit(self.boards[self.toMove][PieceType.PAWN], from_sq)
        self.boards[self.toMove][promotion_piece] = set_bit(self.boards[self.toMove][promotion_piece], to_sq)


    def en_passant(self, from_sq: Square, to_sq: Square):
        color = self.toMove
        opp_color = color ^ 1

        self.boards[color][PieceType.PAWN] = set_bit(clear_bit(self.boards[color][PieceType.PAWN], from_sq), to_sq)

        if color == Color.WHITE:
            captured_sq = to_sq - 8
        else:
            captured_sq = to_sq + 8

        self.boards[opp_color][PieceType.PAWN] = clear_bit(self.boards[opp_color][PieceType.PAWN], captured_sq)

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


    def save_state(self):
        return {
            "boards": [piece_map.copy() for piece_map in self.boards],
            "toMove": self.toMove,
            "castling": self.castling,
            "en_passant": self.en_passant,
            "fifty_move": self.fifty_move
        }

    def load_state(self, saved):
        self.boards = [piece_map.copy() for piece_map in saved["boards"]]
        self.toMove = saved["toMove"]
        self.castling = saved["castling"]
        self.en_passant = saved["en_passant"]
        self.fifty_move = saved["fifty_move"]



if __name__ == '__main__':
    game = State()
    move = Move(Color.WHITE, PieceType.PAWN, Square.E2, Square.E4)
    game.printBitBoard(Color.WHITE, PieceType.KNIGHT)