from constants import Square, PieceType, Color, SQUARE_NAMES, PIECE_SYMBOLS 

class Move:
    def __init__(self, 
                 color: Color, 
                 piece: PieceType, 
                 from_square: Square, 
                 to_square: Square,
                 is_capture: bool = False,
                 promotion_type: PieceType = PieceType.PAWN, 
                 is_castle: bool = False,
                 is_check: bool = False,
                 is_en_passant: bool = False,
                ):
        self.color = color
        self.piece_type = piece 
        self.from_sq = from_square
        self.to_sq = to_square
        self.is_capture = is_capture
        self.promotion_type = promotion_type
        self.is_castle = is_castle
        self.is_check = is_check
        self.is_en_passant = is_en_passant

    def __str__(self):
        return self.notation()
    
    def __repr__(self):
        return str(self.full_details())
    
    def __eq__(self, other):
        return self.notation() == other.notation()
    
    def __hash__(self):
        return self.notation()
    
    def full_details(self):
        return (
            self.color,
            self.piece_type,
            self.from_sq,
            self.to_sq,
            self.is_capture,
            self.promotion_type,
            self.is_castle,
            self.is_check,
            self.is_en_passant,
        )
        

    def notation(self) -> str:
        from_square_name = SQUARE_NAMES[self.from_sq]
        to_square_name = SQUARE_NAMES[self.to_sq]

        piece_char = ""
        if self.piece_type != PieceType.PAWN:
            piece_char = PIECE_SYMBOLS[self.color][self.piece_type]
            if self.piece_type == PieceType.KNIGHT: piece_char = 'N'
            elif self.piece_type == PieceType.BISHOP: piece_char = 'B'
            elif self.piece_type == PieceType.ROOK: piece_char = 'R'
            elif self.piece_type == PieceType.QUEEN: piece_char = 'Q'
            elif self.piece_type == PieceType.KING: piece_char = 'K'

        # --- Castling ---
        if self.is_castle:
            if self.to_sq == Square.G1 or self.to_sq == Square.G8: 
                return "O-O" + ("#" if self.is_mate else ("+" if self.is_check else ""))
            elif self.to_sq == Square.C1 or self.to_sq == Square.C8: 
                return "O-O-O" + ("#" if self.is_mate else ("+" if self.is_check else ""))
            
        result = piece_char

    
        if self.is_capture:
            if self.piece_type == PieceType.PAWN:
                result += from_square_name[0] 
            result += 'x'

        result += to_square_name

        # --- Promotion ---
        if self.promotion_type != PieceType.PAWN: 
            result += '=' + PIECE_SYMBOLS[self.color][self.promotion_type] 

        # --- Check / Checkmate ---
        # if self.is_mate:
        #     result += '#'
        if self.is_check:
            result += '+'

        return result
    


if __name__ == '__main__':
    ex_move = Move(Color.WHITE, PieceType.KING, Square.E1, Square.G1, is_castle=True)
    print(ex_move)
