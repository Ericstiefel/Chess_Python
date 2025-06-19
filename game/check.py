from bitboard import State
from constants import Color, Square
from utils import *
from bit_ops import bitScanForward


def is_in_check(state: State, color: Color) -> int:
    king_square = bitScanForward(state.boards[color][PieceType.KING])

    return is_square_attacked(state, king_square)


def pinned(state: State, piece_sq: Square, king_sq: Square) -> bool:
    ray_directions = [-8, -7, 1, 9, 8, 7, -1, -9]
    own_color = state.toMove
    all_pieces = state.get_all_occupied_squares()

    for direction in ray_directions:
        current = king_sq + direction
        found_piece = False

        while 0 <= current < 64 and is_along_ray(king_sq, current, piece_sq):
            if get_bit(all_pieces, current):
                if not found_piece:
                    if current != piece_sq:
                        break  # not our piece on ray
                    found_piece = True
                else:
                    attacker_piece = state.piece_on_square(current)
                    attacker_color = state.color_on_square(current)
                    if attacker_color != own_color:
                        if direction in [-8, 8, -1, 1]:
                            if attacker_piece in (PieceType.ROOK, PieceType.QUEEN):
                                return True
                        elif direction in [-9, -7, 7, 9]:
                            if attacker_piece in (PieceType.BISHOP, PieceType.QUEEN):
                                return True
                    break  # Not a pin
            current += direction
    return False
