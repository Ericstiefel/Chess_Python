from bitboard import State
from constants import *
from bit_ops import *
from possible_piece_moves import knightMoves, bishopMoves, rookMoves, queenMoves

def is_square_attacked(state: State, target_sq: Square) -> bool:
    """
    Returns True if target_sq is attacked by opponent (not necessarily legal move, just attacked).
    """

    def knight_attack_indices(square: int) -> list[int]:
        rank, file = divmod(square, 8)
        deltas = [(-2, -1), (-2, +1), (-1, -2), (-1, +2),
                (+1, -2), (+1, +2), (+2, -1), (+2, +1)]
        attacks = []
        for dr, df in deltas:
            r, f = rank + dr, file + df
            if 0 <= r < 8 and 0 <= f < 8:
                attacks.append(r * 8 + f)
        return attacks

    def king_attack_indices(square: int) -> list[int]:
        rank, file = divmod(square, 8)
        deltas = [(-1, -1), (-1, 0), (-1, +1),
                (0, -1),          (0, +1),
                (+1, -1), (+1, 0), (+1, +1)]
        attacks = []
        for dr, df in deltas:
            r, f = rank + dr, file + df
            if 0 <= r < 8 and 0 <= f < 8:
                attacks.append(r * 8 + f)
        return attacks
    def bishop_attacks(square: int, occupancy: int) -> int:
        return sliding_attacks(square, occupancy, [(-1, -1), (-1, +1), (+1, -1), (+1, +1)])

    def rook_attacks(square: int, occupancy: int) -> int:
        return sliding_attacks(square, occupancy, [(-1, 0), (+1, 0), (0, -1), (0, +1)])

    def sliding_attacks(square: int, occupancy: int, directions: list[tuple[int, int]]) -> int:
        """Generalized sliding attack generator."""
        attacks = 0
        rank, file = divmod(square, 8)

        for dr, df in directions:
            r, f = rank + dr, file + df
            while 0 <= r < 8 and 0 <= f < 8:
                idx = r * 8 + f
                attacks |= (1 << idx)
                if occupancy & (1 << idx):  # Blocked
                    break
                r += dr
                f += df

        return attacks


    by_color = state.toMove ^ 1
    target_idx = target_sq

    # 1. Pawn attacks
    pawn_bb = state.boards[by_color][PieceType.PAWN]
    if by_color == Color.WHITE:
        left_attack = (1 << target_idx) >> 9 & ~FILE_H
        right_attack = (1 << target_idx) >> 7 & ~FILE_A
    else:
        left_attack = (1 << target_idx) << 7 & ~FILE_H
        right_attack = (1 << target_idx) << 9 & ~FILE_A
    if pawn_bb & (left_attack | right_attack):
        return True

    # 2. Knight attacks
    for knight_sq in bitscan(state.boards[by_color][PieceType.KNIGHT]):
        if target_idx in knight_attack_indices(knight_sq):
            return True

    # 3. King attacks
    for king_sq in bitscan(state.boards[by_color][PieceType.KING]):
        if target_idx in king_attack_indices(king_sq):
            return True

    # 4. Sliding attacks (bishop, rook, queen)
    occupancy = state.get_all_occupied_squares()
    for piece_type, attack_func in [
        (PieceType.BISHOP, bishop_attacks),
        (PieceType.ROOK, rook_attacks),
        (PieceType.QUEEN, lambda sq, occ: bishop_attacks(sq, occ) | rook_attacks(sq, occ))
    ]:
        attacker_bb = state.boards[by_color][piece_type]
        for from_sq in bitscan(attacker_bb):
            if (1 << target_idx) & attack_func(from_sq, occupancy):
                return True

    return False


def attackers_to_square(state: State, target_sq: Square) -> int:
    by_color = state.toMove ^ 1
    attackers = 0

    # Check pawn attacks
    pawn_bb = state.boards[by_color][PieceType.PAWN]
    if by_color == Color.WHITE:
        if target_sq >= 9 and target_sq % 8 != 0:
            bit = (1 << (target_sq - 9)) & pawn_bb
            attackers |= bit
        if target_sq >= 7 and target_sq % 8 != 7:
            bit = (1 << (target_sq - 7)) & pawn_bb
            attackers |= bit
    else:
        if target_sq <= 55 and target_sq % 8 != 0:
            bit = (1 << (target_sq + 7)) & pawn_bb
            attackers |= bit
        if target_sq <= 54 and target_sq % 8 != 7:
            bit = (1 << (target_sq + 9)) & pawn_bb
            attackers |= bit

    saved_turn = state.toMove
    state.toMove = by_color

    # Check knights
    for move in knightMoves(state):
        if move.to_sq == target_sq:
            attackers |= (1 << move.from_sq)

    # Check bishops
    for move in bishopMoves(state):
        if move.to_sq == target_sq:
            attackers |= (1 << move.from_sq)

    # Check rooks
    for move in rookMoves(state):
        if move.to_sq == target_sq:
            attackers |= (1 << move.from_sq)

    # Check queens
    for move in queenMoves(state):
        if move.to_sq == target_sq:
            attackers |= (1 << move.from_sq)

    # Reset the turn
    state.toMove = saved_turn

    return attackers


def squares_between(from_sq: int, to_sq: int) -> int:
    """
    Generates a bitboard of all squares strictly between from_sq and to_sq.
    Does NOT include from_sq or to_sq.
    Only supports aligned squares: same rank, file, or diagonal.
    """
    from_rank, from_file = divmod(from_sq, 8)
    to_rank, to_file = divmod(to_sq, 8)

    dr = to_rank - from_rank
    df = to_file - from_file

    # Check alignment: must be same rank, file, or diagonal
    if dr != 0 and df != 0 and abs(dr) != abs(df):
        return 0  # Not aligned, so no squares between

    if dr != 0: dr //= abs(dr)
    if df != 0: df //= abs(df)

    direction = dr * 8 + df

    bb = 0
    current_sq = from_sq + direction
    while current_sq != to_sq:
        if not (0 <= current_sq < 64):
            break  # Prevent overflow or infinite loop
        bb |= 1 << current_sq
        current_sq += direction

    return bb

def is_along_ray(origin: int, from_sq: int, to_sq: int) -> bool:
    # True if origin, from_sq, and to_sq lie in a straight line
    dr1, df1 = divmod(from_sq, 8)
    dr0, df0 = divmod(origin, 8)
    dr2, df2 = divmod(to_sq, 8)

    # Check if slopes are equal (avoiding div by 0)
    vec1 = (dr1 - dr0, df1 - df0)
    vec2 = (dr2 - dr1, df2 - df1)

    return vec1[0] * vec2[1] == vec1[1] * vec2[0]  # cross product == 0

