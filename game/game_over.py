from bitboard import State
from move import Move
from legal_moves import legal_moves
from constants import Color
from constants import PieceType
from bit_ops import lsb_index, popcount
from legal_king_moves import is_in_check


def fifty_move_rule(state: State) -> bool:
    return state.fifty_move == 50

def num_pieces(state: State):
        return popcount(state.get_all_occupied_squares())

def check_or_stale_mate(state: State, moves: list[Move]) -> float:
    if not moves:
        if is_in_check(state):
            return 1 if state.toMove == Color.BLACK else -1  # white wins if black in checkmate
        return 0.5  # stalemate
    return 0

def count_pieces(state: State, color: Color) -> dict[PieceType, int]:
    counts = {}
    for piece_type in [PieceType.PAWN, PieceType.KNIGHT, PieceType.BISHOP, PieceType.ROOK, PieceType.QUEEN]:
        piece_bitboard = state.boards[color][piece_type]
        counts[piece_type] = popcount(piece_bitboard)
    return counts

def is_insufficient_material(state: State) -> bool:
    """
    Checks for insufficient material draw conditions, such as:
    - King vs King
    - King vs King + Knight
    - King vs King + Bishop
    - King + Bishop vs King + Bishop (Bishops on same colored squares)
    - King + Bishop vs King + Knight
    - King + Knight vs King + Knight
    """
    def get_squares_from_bitboard(bb: int) -> list[int]:
        squares = []
        while bb:
            sq = lsb_index(bb)
            squares.append(sq)
            bb &= bb - 1
        return squares

    def is_light_square(sq: int) -> bool:
        # A square is light if the sum of its rank and file is even
        return ((sq // 8 + sq % 8) % 2) == 0

    white_pieces = count_pieces(state, Color.WHITE)
    black_pieces = count_pieces(state, Color.BLACK)

    # Check for pawns, rooks, or queens - if any exist, it's not a draw.
    if (white_pieces[PieceType.PAWN] > 0 or white_pieces[PieceType.ROOK] > 0 or white_pieces[PieceType.QUEEN] > 0 or
        black_pieces[PieceType.PAWN] > 0 or black_pieces[PieceType.ROOK] > 0 or black_pieces[PieceType.QUEEN] > 0):
        return False

    # At this point, only kings and minor pieces are left.
    white_knights = white_pieces[PieceType.KNIGHT]
    white_bishops = white_pieces[PieceType.BISHOP]
    black_knights = black_pieces[PieceType.KNIGHT]
    black_bishops = black_pieces[PieceType.BISHOP]

    total_minor_pieces = white_knights + white_bishops + black_knights + black_bishops

    # King vs King (0 minor pieces) or King vs King + 1 minor piece (K vs K+N or K vs K+B)
    if total_minor_pieces <= 1:
        return True

    # Scenarios with exactly two minor pieces on the board.
    if total_minor_pieces == 2:
        # King + Knight vs King + Knight
        if white_knights == 1 and black_knights == 1:
            return True

        # King + Bishop vs King + Knight
        if (white_bishops == 1 and black_knights == 1) or (black_bishops == 1 and white_knights == 1):
            return True

        # King + Bishop vs King + Bishop, with both bishops on the same color squares
        if white_bishops == 1 and black_bishops == 1:
            white_bishop_sq = get_squares_from_bitboard(state.boards[Color.WHITE][PieceType.BISHOP])[0]
            black_bishop_sq = get_squares_from_bitboard(state.boards[Color.BLACK][PieceType.BISHOP])[0]
            # Return true if both bishops are on the same color of squares
            return is_light_square(white_bishop_sq) == is_light_square(black_bishop_sq)

    # The position has enough material for a potential checkmate (e.g., K+B+N vs K or K+2B vs K)
    return False