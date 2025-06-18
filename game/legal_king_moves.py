from move import Move
from bitboard import State
from bit_ops import *
from constants import *
from utils import is_square_attacked
import copy


def is_in_check(state: State) -> bool:
    king_sq = lsb_index(state.boards[state.toMove][PieceType.KING])
    return is_square_attacked(state, Square(king_sq))


def castleMoves(state: State) -> list[Move]:
    color = state.toMove
    moves = []
    occupied = state.get_all_occupied_squares()

    if color == Color.WHITE:
        if state.castling & 0b0001:  # White kingside
            if not (get_bit(occupied, Square.F1) or get_bit(occupied, Square.G1)):
                if not is_square_attacked(state, Square.E1) and \
                   not is_square_attacked(state, Square.F1) and \
                   not is_square_attacked(state, Square.G1):
                    moves.append(Move(Color.WHITE, PieceType.KING, Square.E1, Square.G1, is_castle=True))

        if state.castling & 0b0010:  # White queenside
            if not (get_bit(occupied, Square.B1) or get_bit(occupied, Square.C1) or get_bit(occupied, Square.D1)):
                if not is_square_attacked(state, Square.E1) and \
                   not is_square_attacked(state, Square.D1) and \
                   not is_square_attacked(state, Square.C1):
                    moves.append(Move(Color.WHITE, PieceType.KING, Square.E1, Square.C1, is_castle=True))

    else:
        if state.castling & 0b0100:  # Black kingside
            if not (get_bit(occupied, Square.F8) or get_bit(occupied, Square.G8)):
                if not is_square_attacked(state, Square.E8) and \
                   not is_square_attacked(state, Square.F8) and \
                   not is_square_attacked(state, Square.G8):
                    moves.append(Move(Color.BLACK, PieceType.KING, Square.E8, Square.G8, is_castle=True))

        if state.castling & 0b1000:  # Black queenside
            if not (get_bit(occupied, Square.B8) or get_bit(occupied, Square.C8) or get_bit(occupied, Square.D8)):
                if not is_square_attacked(state, Square.E8) and \
                   not is_square_attacked(state, Square.D8) and \
                   not is_square_attacked(state, Square.C8):
                    moves.append(Move(Color.BLACK, PieceType.KING, Square.E8, Square.C8, is_castle=True))

    return moves

def kingMoves(state: State, attacker_ct: int) -> list[Move]:
    color = state.toMove
    moves = []

    king_bb = state.boards[color][PieceType.KING]
    from_sq_idx = lsb_index(king_bb)
    from_sq = Square(from_sq_idx)

    own_occ = state.get_occupied_by_color(color)
    opp_occ = state.get_occupied_by_color(color ^ 1)

    deltas = [-9, -8, -7, -1, +1, +7, +8, +9]
    for d in deltas:
        to_sq_idx = from_sq_idx + d
        if 0 <= to_sq_idx < 64:
            file_diff = abs((from_sq_idx % 8) - (to_sq_idx % 8))
            if file_diff <= 1 and not get_bit(own_occ, to_sq_idx):
                is_capture = get_bit(opp_occ, to_sq_idx)
                move = Move(color, PieceType.KING, from_sq, Square(to_sq_idx), is_capture=is_capture)
                state.move_piece(move)
                if not is_square_attacked(state, Square(to_sq_idx)):
                    moves.append(Move(color, PieceType.KING, from_sq, Square(to_sq_idx), is_capture=is_capture))
                state.unmake_move()
    if attacker_ct == 0:
        # Add castling moves
        moves.extend(castleMoves(state))
    

    return moves


if __name__ == '__main__':
    state = State()


    move = Move(Color.WHITE, pieceType.PAWN, Square.E2, Square.E4)
    state.move_piece(move)