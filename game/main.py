from collections import defaultdict
from bitboard import State
from move_piece import turn
from game_over import fifty_move_rule, check_or_stale_mate, is_insufficient_material, num_pieces
from legal_moves import legal_moves
import random
from constants import *
from move import Move
import copy
import time

def get_random_move(moves: list[Move]):
    move = random.choice(moves)
    return move


def game(state: State) -> float:
    seen_boards = defaultdict(int)

    while True:
        moves = legal_moves(state)
        check_or_stale = check_or_stale_mate(state, moves)
        if check_or_stale:
            if check_or_stale == 0.5:
                print('Stalemate')
                return 0.5
            print('Checkmate')
            return check_or_stale
        
        move = get_random_move(moves)      

        turn(state, move)

        if num_pieces(state) < 5:
            if is_insufficient_material(state):
                print('Insufficent Material')
                return 0.5

        # if seen_boards[state] == 2:
        #     print('Threefold Repetition')
        #     return 0.5
        
        if fifty_move_rule(state):
            print('Fifty Move Rule')
            return 0.5

        seen_boards[copy.deepcopy(state)] += 1



if __name__ == '__main__':
    state = State()
    game(state)
    state.printBoard()
    

