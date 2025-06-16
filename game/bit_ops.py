from constants import Square


def get_bit(bb: int, square: int) -> int:
    return (bb >> square) & 1

def set_bit(bb: int, square: int) -> int:
    return bb | (1 << square)

def clear_bit(bb: int, square: int) -> int:
    return bb & ~(1 << square)


def lsb_index(bitboard: int) -> int:
    if bitboard == 0:
        return -1
    return (bitboard & -bitboard).bit_length() - 1 # Faster way using 2's complement properties

def popcount(bb: int) -> int:
    return bin(bb).count('1')


def msb_index(bitboard: int) -> int:

    if bitboard == 0:
        return -1
    return bitboard.bit_length() - 1 

def bitScanForward(bb: int) -> int:
    return (bb & -bb).bit_length() - 1

def bitboard_to_squares(bb: int):
    return [Square(i) for i in range(64) if (bb >> i) & 1]

def bitscan(bb: int) -> list[int]:
    """Returns a list of indices of bits set to 1 in the bitboard."""
    indices = []
    while bb:
        lsb = bb & -bb
        idx = (lsb).bit_length() - 1
        indices.append(idx)
        bb &= bb - 1
    return indices

def bitboard_to_squares(bb: int) -> list[Square]:
    """
    Returns a list of Square enum members for all set bits in the bitboard.
    Efficiently iterates by repeatedly finding and clearing the LSB.
    """
    squares = []
    temp_bb = bb
    while temp_bb:
        sq_idx = lsb_index(temp_bb)  # Find the index of the least significant set bit
        squares.append(Square(sq_idx)) # Convert to Square enum and add to list
        temp_bb = clear_bit(temp_bb, sq_idx) # Clear that bit to find the next LSB
    return squares