from bitboard import State
from constants import PieceType, Square, Color ,RANK_1, RANK_2, RANK_7, RANK_8, FILE_A, FILE_H, KNIGHT_OFFSETS
from move import Move
from bit_ops import get_bit, clear_bit, lsb_index
from utils import *

def pawnMoves(state: State) -> list[Move]:
    color: Color = state.toMove
    moves = []

    if color == Color.WHITE:
        forward_one = 8
        forward_two = 16
        attack_left = 7
        attack_right = 9
        start_rank_bb = RANK_2
        ep_capture_rank_bb = 0x00000000FF000000  # Rank 5
        promotion_rank_bb = RANK_8
    else:
        forward_one = -8
        forward_two = -16
        attack_left = -9
        attack_right = -7
        start_rank_bb = RANK_7
        ep_capture_rank_bb = 0x000000FF00000000  # Rank 4
        promotion_rank_bb = RANK_1

    current_pawns_bb = state.boards[color][PieceType.PAWN]
    opponent_occupied_bb = state.get_occupied_by_color(color ^ 1)
    all_occupied_bb = state.get_all_occupied_squares()

    temp_pawns_bb = current_pawns_bb
    while temp_pawns_bb:
        from_sq_idx = lsb_index(temp_pawns_bb)
        from_sq = Square(from_sq_idx)
        temp_pawns_bb = clear_bit(temp_pawns_bb, from_sq)

        # --- 1. Single Forward Push ---
        target_sq_push_one_idx = from_sq_idx + forward_one
        if 0 <= target_sq_push_one_idx <= 63 and not get_bit(all_occupied_bb, target_sq_push_one_idx):
            if (1 << target_sq_push_one_idx) & promotion_rank_bb:
                for pt_promo in [PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT]:
                    moves.append(Move(color, PieceType.PAWN, from_sq, Square(target_sq_push_one_idx), promotion_type=pt_promo, is_capture=False))
            else:
                moves.append(Move(color, PieceType.PAWN, from_sq, Square(target_sq_push_one_idx)))
                # --- 2. Double Forward Push ---
                if (1 << from_sq_idx) & start_rank_bb:
                    target_sq_push_two_idx = from_sq_idx + forward_two
                    if 0 <= target_sq_push_two_idx <= 63 and not get_bit(all_occupied_bb, target_sq_push_two_idx):
                        moves.append(Move(color, PieceType.PAWN, from_sq, Square(target_sq_push_two_idx)))

        # --- 3. Diagonal Captures ---
        for offset in [attack_left, attack_right]:
            target_sq_idx = from_sq_idx + offset
            if 0 <= target_sq_idx <= 63:
                same_rank = abs((from_sq_idx % 8) - (target_sq_idx % 8)) == 1
                if same_rank and get_bit(opponent_occupied_bb, target_sq_idx):
                    to_sq = Square(target_sq_idx)
                    if (1 << target_sq_idx) & promotion_rank_bb:
                        for pt_promo in [PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT]:
                            moves.append(Move(color, PieceType.PAWN, from_sq, to_sq, is_capture=True, promotion_type=pt_promo))
                    else:
                        moves.append(Move(color, PieceType.PAWN, from_sq, to_sq, is_capture=True))

        # --- 4. En Passant ---
        if state.en_passant != Square.NO_SQUARE:
            ep_target_idx = state.en_passant.value
            if from_sq_idx // 8 == (4 if color == Color.WHITE else 3):
                for offset in [attack_left, attack_right]:
                    if from_sq_idx + offset == ep_target_idx:
                        moves.append(Move(color, PieceType.PAWN, from_sq, Square(ep_target_idx), is_capture=True, is_en_passant=True))

    return moves


def knightMoves(state: State) -> list[Move]:
    """
    Generates all legal knight moves for the current player.
    Knights can jump over pieces and move in an L-shape.
    """
    color: Color = state.toMove
    moves = []

    knight_bb = state.boards[color][PieceType.KNIGHT]
    own_occupied_bb = state.get_occupied_by_color(color) # Cant jump to square with player's piece on it

    temp_knights_bb = knight_bb
    while temp_knights_bb:
        from_sq_idx = lsb_index(temp_knights_bb)
        from_sq = Square(from_sq_idx)
        temp_knights_bb = clear_bit(temp_knights_bb, from_sq)

        from_rank = from_sq_idx // 8
        from_file = from_sq_idx % 8

        for offset in KNIGHT_OFFSETS:
            target_sq_idx = from_sq_idx + offset

            if not (0 <= target_sq_idx < 64):
                continue  # Skip if off-board numerically

            to_rank = target_sq_idx // 8
            to_file = target_sq_idx % 8

            if abs(to_rank - from_rank) + abs(to_file - from_file) != 3:
                continue  # Invalid wraparound or off-board move

            if get_bit(own_occupied_bb, target_sq_idx):
                continue  

            moves.append(Move(color, PieceType.KNIGHT, from_sq, Square(target_sq_idx)))

    return moves

def bishopMoves(state: State) -> list[Move]:
    """
    Generates all legal bishop moves for the current player.
    Bishops move diagonally until blocked.
    """
    color: Color = state.toMove
    moves = []

    bishop_bb = state.boards[color][PieceType.BISHOP]
    own_occupied_bb = state.get_occupied_by_color(color)
    opponent_occupied_bb = state.get_occupied_by_color(color ^ 1)

    directions = [+9, -9, +7, -7]  # NE, SW, NW, SE

    temp_bishop_bb = bishop_bb
    while temp_bishop_bb:
        from_sq_idx = lsb_index(temp_bishop_bb)
        from_sq = Square(from_sq_idx)
        temp_bishop_bb = clear_bit(temp_bishop_bb, from_sq)

        for direction in directions:
            to_sq_idx = from_sq_idx
            while True:
                rank = to_sq_idx // 8
                file = to_sq_idx % 8

                to_sq_idx += direction
                if not (0 <= to_sq_idx < 64):
                    break

                new_rank = to_sq_idx // 8
                new_file = to_sq_idx % 8

                # Prevent diagonal wrapping
                if direction in [+9, -7] and new_file == 0 and file == 7:
                    break
                if direction in [-9, +7] and new_file == 7 and file == 0:
                    break
                if abs(new_file - file) > 2:
                    break

                if get_bit(own_occupied_bb, to_sq_idx):
                    break

                is_capture = get_bit(opponent_occupied_bb, to_sq_idx)
                moves.append(Move(color, PieceType.BISHOP, from_sq, Square(to_sq_idx), is_capture=is_capture))

                if is_capture:
                    break

    return moves


def rookMoves(state: State) -> list[Move]:
    """
    Generates all legal rook moves for the current player.
    Rooks move in straight lines horizontally and vertically until blocked.
    """
    color: Color = state.toMove
    moves = []

    rook_bb = state.boards[color][PieceType.ROOK]
    own_occupied_bb = state.get_occupied_by_color(color)
    opponent_occupied_bb = state.get_occupied_by_color(color ^ 1)

    directions = [+8, -8, +1, -1]  # N, S, E, W

    temp_rook_bb = rook_bb
    while temp_rook_bb:
        from_sq_idx = lsb_index(temp_rook_bb)
        from_sq = Square(from_sq_idx)
        temp_rook_bb = clear_bit(temp_rook_bb, from_sq)

        for direction in directions:
            to_sq_idx = from_sq_idx
            while True:
                rank = to_sq_idx // 8

                to_sq_idx += direction

                if not (0 <= to_sq_idx < 64):
                    break

                new_rank = to_sq_idx // 8

                # Prevent horizontal wrap (e.g., a1 to a2 is valid, but a1 to b1 is only valid if still on same rank)
                if direction == 1 and new_rank != rank: break  # East wrap
                if direction == -1 and new_rank != rank: break  # West wrap

                if get_bit(own_occupied_bb, to_sq_idx):
                    break  # Blocked by own piece

                is_capture = get_bit(opponent_occupied_bb, to_sq_idx)
                moves.append(Move(color, PieceType.ROOK, from_sq, Square(to_sq_idx), is_capture=is_capture))

                if is_capture:
                    break  
    return moves


def queenMoves(state: State) -> list[Move]:
    """
    Generates all legal queen moves for the current player.
    The queen moves in all 8 directions (like rook + bishop) until blocked.
    """
    color: Color = state.toMove
    moves = []

    queen_bb = state.boards[color][PieceType.QUEEN]
    own_occupied_bb = state.get_occupied_by_color(color)
    opponent_occupied_bb = state.get_occupied_by_color(color ^ 1)

    directions = [+8, -8, +1, -1, +9, -9, +7, -7]  # N, S, E, W, NE, SW, NW, SE

    temp_queen_bb = queen_bb
    while temp_queen_bb:
        from_sq_idx = lsb_index(temp_queen_bb)
        from_sq = Square(from_sq_idx)
        temp_queen_bb = clear_bit(temp_queen_bb, from_sq)

        for direction in directions:
            to_sq_idx = from_sq_idx
            while True:
                rank = to_sq_idx // 8
                file = to_sq_idx % 8

                to_sq_idx += direction

                # Check board bounds
                if not (0 <= to_sq_idx < 64):
                    break

                new_rank = to_sq_idx // 8
                new_file = to_sq_idx % 8

                # Prevent horizontal wrapping for diagonal and rook directions
                if direction in [+1, -1, +9, -7] and new_file == 0 and file == 7:
                    break  # wrapped from H-file to A-file
                if direction in [-1, +7, -9] and new_file == 7 and file == 0:
                    break  # wrapped from A-file to H-file
                if abs(new_file - file) > 2:  # in case of multi-wrapping
                    break

                if get_bit(own_occupied_bb, to_sq_idx):
                    break  # Blocked by own piece

                is_capture = get_bit(opponent_occupied_bb, to_sq_idx)
                moves.append(Move(color, PieceType.QUEEN, from_sq, Square(to_sq_idx), is_capture=is_capture))

                if is_capture:
                    break  # Stop after capture

    return moves



if __name__ == '__main__':
    state = State()

    print(pawnMoves(state))
    print(knightMoves(state))
    print(bishopMoves(state))
    print(rookMoves(state))
    print(queenMoves(state))