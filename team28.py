import random
import sys
import copy
import time
import signal

class Player28:

    def __init__(self):
        self.available_cells = []
        self.infinity = 99999999
        self.ninfinity = -99999999
        self.timer = 0
        self.symbol = 'x'
        self.next_move = (0 , 0, 0)
        self.small_board_value = ([['-' for i in range(3)] for j in range(3)], [['-' for i in range(3)] for j in range(3)])
        
        self.STATES = [
            "BASE",
            "DRAW",
            "LOSS",
            "MIDDLE",
            "OPEN",
            "PRE_WIN",
            "PRE_LOSS",
            "WIN",
            "ULTIMATE_WIN"
        ]
        self.block_states = ['DRAW', 'WIN', 'LOSS']

        self.WIN_COMBINATIONS = [
            [(0, 0), (0, 1), (0, 2)],
            [(1, 0), (1, 1), (1, 2)],
            [(2, 0), (2, 1), (2, 2)],

            [(0, 0), (1, 0), (2, 0)],
            [(0, 1), (1, 1), (2, 1)],
            [(0, 2), (1, 2), (2, 2)],

            [(0, 0), (1, 1), (2, 2)],
            [(0, 2), (0, 1), (2, 0)]
        ]

        self.UTILITY = {
            "BASE": 50,
            "DRAW": 100,
            "LOSS": -1000,
            "MIDDLE": 0,
            "OPEN": 300,
            "PRE_WIN": 300,
            "PRE_LOSS": -500,
            "WIN": 1000,
            "ULTIMATE_WIN": self.infinity + 1
        }

    def get_board_state(self, board, old_move, symbol, flag):
        
        cell = (old_move[1] % 3, old_move[2] % 3)
        curr_row = cell[0] * 3
        curr_col = cell[1] * 3

        pre_win = {'x': False, 'o': False}
        state = ["", ""]
        result = ""

        for k in range(2):
            state[k] = board.small_boards_status[k][cell[0]][cell[1]]
            if state[k] != '-':
                if state[k] == 'd':
                    state[k] = "DRAW"
                elif state[k] == symbol:
                    state[k] = "WIN"
                else:
                    state[k] = "LOSS"
                continue

            cnt = {'x' : 0, 'o' : 0, '-' : 0}
            
            for pos in self.WIN_COMBINATIONS:
                a = board.big_boards_status[k][curr_row + pos[0][0]][curr_col + pos[0][1]]
                b = board.big_boards_status[k][curr_row + pos[1][0]][curr_col + pos[1][1]]
                c = board.big_boards_status[k][curr_row + pos[2][0]][curr_col + pos[2][1]]

                cnt[a] += 1
                cnt[b] += 1
                cnt[c] += 1
                if cnt['x'] == 2:
                    pre_win['x'] = True
                elif cnt['o'] == 2:
                    pre_win['o'] = True
                
                if pre_win['x'] and pre_win['o']:
                    state[k] = "MIDDLE"
                elif not pre_win['x'] and not pre_win['o']:
                    state[k] = "BASE"
                elif pre_win[symbol]:
                    state[k] = "PRE_WIN"
                else:
                    state[k] = "PRE_LOSS"

            
        if self.get_state_utility(state[0]) > self.get_state_utility(state[1]):
            result = state[0]
        else:
            result = state[1]

        if state[0] in self.block_states and state[1] in self.block_states:
            result = 'OPEN'
        elif state[0] in self.block_states:
            result = state[1]
        elif state[1] in self.block_states:
            result = state[0]

        # to return state of fixed board
        if flag:
            result = state[old_move[0]]

        return result
    
    def get_state_utility(self, state):
        value = self.UTILITY[state]
        return value

    def heuristic(self, board, old_move, current_move):

        old_cell = (old_move[1] % 3, old_move[2] % 3)
        current_cell = (current_move[1] % 3, old_move[2] % 3)

        value = 0
        state = ""
        # CURRENT BOARD UTILITY
        state = self.get_board_state(board, old_move, self.symbol, True)
        value += self.get_state_utility(state)
        if state == self.symbol:
            state = self.get_board_state(board, current_move, self.symbol, False)
            value += self.get_state_utility(state)

        # NEXT CELL UTILITY
        state = self.get_board_state(board, current_move, self.symbol, False)
        value += self.get_state_utility(state)
        return value

    def move(self, board, old_move, symbol):
        self.timer=time.time()
        self.symbol = symbol
        # self.available_cells = board.find_valid_move_cells(old_move)
        value = self.minimax(board, (-1, -1, -1), old_move, 0, self.ninfinity, self.infinity, True, symbol)
        return self.next_move

    
    def minimax(self, board, older_move, old_move, depth, alpha, beta, max_player, symbol):
        status = board.find_terminal_state()
        # if time.time() - self.timer>=23:
        #     return self.heuristic(board,old_move)
        if depth == 3 or status[0] != 'CONTINUE' or time.time()-self.timer>=23:
            if self.symbol == 'x':
                return self.heuristic(board, older_move, old_move)
            else:
                return (-1 * self.heuristic(board, older_move, old_move))
        if max_player:
            value = self.ninfinity
            self.available_cells = board.find_valid_move_cells(old_move)
            random.shuffle(self.available_cells)
            for move_cell in self.available_cells:
                board.update(old_move, move_cell, symbol)
                if symbol == 'o':
                    next_flag = 'x'
                else:
                    next_flag = 'o'
                child_value = self.minimax(board, old_move, move_cell, depth + 1, alpha, beta, False, next_flag)
                board.big_boards_status[move_cell[0]][move_cell[1]][move_cell[2]] = '-'
                board.small_boards_status[move_cell[0]][move_cell[1] / 3][move_cell[2] / 3] = '-'
                if child_value > value:
                    value = child_value
                    if depth == 0:
                        self.next_move = copy.deepcopy(move_cell)
                alpha = max(alpha, value)				
                if alpha >= beta:
                    break
            return value

        else:
            value = self.infinity
            self.available_cells = board.find_valid_move_cells(old_move)
            random.shuffle(self.available_cells)
            for move_cell in self.available_cells:
                board.update(old_move, move_cell, symbol)
                if symbol == 'o':
                    next_flag = 'x'
                else:
                    next_flag = 'o'
                child_value = self.minimax(board, old_move, move_cell, depth + 1, alpha, beta, True, next_flag)
                board.big_boards_status[move_cell[0]][move_cell[1]][move_cell[2]] = '-'
                board.small_boards_status[move_cell[0]][move_cell[1] / 3][move_cell[2] / 3] = '-'
                if child_value < value:
                    value = child_value
                    if depth == 0:
                        self.next_move = copy.deepcopy(move_cell)
                beta = min(beta, value)				
                if alpha >= beta:
                    break
            return value

