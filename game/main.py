from collections import defaultdict
from bitboard import State
from move_piece import turn
from game_over import fifty_move_rule, check_or_stale_mate, is_insufficient_material, num_pieces
from legal_moves import legal_moves
import random
from constants import *
from move import Move
import time
from edge_cases import EN_PASSANT
from bit_ops import *

def get_random_move(moves: list[Move]):
    move = random.choice(moves)
    return move


def selected_moves(idx):
    moves = EN_PASSANT
    return moves[idx]


def game(state: State) -> float:
    seen_boards = defaultdict(int)

    while True:
        moves = legal_moves(state)
        check_or_stale = check_or_stale_mate(state, moves)
        if check_or_stale:
            if check_or_stale == 0.5:
                return 0.5
            return check_or_stale
        
        move = get_random_move(moves) 

        turn(state, move)

        if num_pieces(state) < 5:
            if is_insufficient_material(state):
                return 0.5

        position_key = hash(state)
        if seen_boards[position_key] == 2:
            return 0.5

        seen_boards[position_key] += 1

        
        if fifty_move_rule(state):
            return 0.5


if __name__ == '__main__':

    state = State()
    game(state)
    state.printBoard()

    # begin_time = time.time()

    # #Time Trials

    # for _ in range(100):
    #     state = State()
    #     for move in moves:
    #         turn(state, move)
    
    # end_time = time.time()

    # print('Avg time: ', (end_time - begin_time) / 100)

    # begin_time = time.time()

    # for _ in range(100):
    #     state = State()
    #     game(state)

    # end_time = time.time()

    # print('Avg Game Time : ', (end_time - begin_time) / 100)
        

