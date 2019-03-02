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
            "BIG_SETUP",
            "DRAW",
            "LOSS",
            "MIDDLE",
            "OPEN",
            "POST_MIDDLE",
            "POST_LOSS",
            "POST_WIN",
            "PRE_LOSS",
            "PRE_WIN",
            "WIN",
            "PRE_ULTIMATE_WIN",
            "ULTIMATE_LOSS",
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
            "BASE": 0,
            "BIG_SETUP": 0,
            "DRAW": 0,
            "LOSS": 0,
            "MIDDLE": 0,
            "POST_MIDDLE": 0, # +ve
            "OPEN": 0, # +ves
            "POST_LOSS": 0,
            "POST_WIN": 0,
            "PRE_LOSS": 0,
            "PRE_WIN": 0,
            "WIN": 0,
            "PRE_ULTIMATE_WIN": 0, # rand
            "ULTIMATE_LOSS": self.ninfinity - 1,
            "ULTIMATE_WIN": self.infinity + 1
        }

    # def get_board_state(self, board, old_move, symbol, flag, player):
    def get_board_state(self, board, old_move, symbol, flag):
        
        cell = (old_move[1] % 3, old_move[2] % 3)
        curr_row = cell[0] * 3
        curr_col = cell[1] * 3

        pre_win = {'x': False, 'o': False}
        state = ["", ""]
        result = ""

        # for k in range(2):
        #     for i in range(3):
        #         for j in range(3):
        #             self.small_board_value[k][i][j] = board.small_boards_status[k][i][j]

        for k in range(2):

            # check if board state for win/loss/draw
            temp_state = board.small_boards_status[k][cell[0]][cell[1]]
            if temp_state != '-':
                if state[k] == 'd':
                    state[k] = "DRAW"
                elif state[k] == symbol:
                    state[k] = "WIN"
                else:
                    state[k] = "LOSS"

            for pos in self.WIN_COMBINATIONS:
                cnt = {'x' : 0, 'o' : 0, '-' : 0}
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
            
            if not pre_win['x'] and not pre_win['o']:
                state[k] = "BASE"
            elif pre_win['x'] and pre_win['o']:
                if flag:
                    state[k] = "MIDDLE"
                else:
                    state[k] = "POST_MIDDLE"

            elif pre_win[symbol]:
                if flag:
                    state[k] = "PRE_WIN"
                else:
                    state[k] = "POST_WIN"
            else:
                if flag:
                    state[k] = "PRE_LOSS"
                else:
                    state[k] = "POST_LOSS"

            
        if self.get_state_utility(state[0]) > self.get_state_utility(state[1]):
            result = state[0]
        else:
            result = state[1]

        # getting state considering both big boards
        if state[0] in self.block_states and state[1] in self.block_states:
            result = "OPEN"
        elif state[0] in self.block_states:
            result = state[1]
        elif state[1] in self.block_states:
            result = state[0]

        # to return state of fixed board
        if flag:
            result = state[old_move[0]]

        return result

    def pre_ultimate_win_state(self, board, move, symbol):
        
        result = ""
        state = ["", ""]
        pre_win = {'x' : False, 'o': False, 'X' : False}
        opp_symbol = 'x'
        if self.symbol == 'x':
            opp_symbol = 'o'
 
        for k in range(2):
            for i in range(3):
                for j in range(3):
                    self.small_board_value[k][i][j] = board.small_boards_status[k][i][j]

        for k in range(2):

            self.small_board_value[k][move[1] % 3][move[2] % 3] = symbol

            for pos in self.WIN_COMBINATIONS:
                cnt = {'x' : 0, 'o' : 0, '-' : 0, 'd' : 0}
                a = self.small_board_value[k][pos[0][0]][pos[0][1]]
                b = self.small_board_value[k][pos[1][0]][pos[1][1]]
                c = self.small_board_value[k][pos[2][0]][pos[2][1]]

                cnt[a] += 1
                cnt[b] += 1
                cnt[c] += 1
                if cnt[symbol] == 3:
                    pre_win['X'] = True
                elif cnt[symbol] == 2 and cnt['-'] == 1:
                    pre_win[symbol] = True
                elif pre_win[opp_symbol] == 2 and cnt['-'] == 1:
                    pre_win[opp_symbol] = True

            if pre_win['X']:
                state[k] = "PRE_ULTIMATE_WIN"
            elif pre_win[symbol]:
                state[k] = "BIG_SETUP"
        
        if self.UTILITY[state[0]] > self.UTILITY[state[1]]:
            result = state[0]
        else:
            result = state[1]
        return result


    def get_state_utility(self, state):
        # possible additions ?? >>>> FOUND IT!!!
        if state == "BASE":
            pass
        return self.UTILITY[state]

    def heuristic(self, board, old_move, current_move):

        # old_cell = (old_move[1] % 3, old_move[2] % 3)
        # current_cell = (current_move[1] % 3, old_move[2] % 3)

        opp_symbol = 'x'
        if self.symbol == 'x':
            opp_symbol = 'o'
        value = 0
        state = ""

        # CURRENT BOARD UTILITY
        state = self.get_board_state(board, old_move, self.symbol, True)
        value += self.get_state_utility(state)

        if state == "WIN":
            state = self.pre_ultimate_win_state(board, old_move, self.symbol)
            if state == "PRE_ULTIMATE_WIN":
                state = "ULTIMATE_WIN"
                return self.UTILITY[state]
            value += self.UTILITY[state]

            state = self.pre_ultimate_win_state(board, current_move, self.symbol)
            value += self.UTILITY[state]

            state = self.get_board_state(board, current_move, self.symbol, False)
            value += self.get_state_utility(state)

        # NEXT CELL UTILITY
        else:

            state = self.pre_ultimate_win_state(board, current_move, opp_symbol)
            value -= self.UTILITY[state]

            # state = self.get_board_state(board, current_move, self.symbol, False)
            state = self.get_board_state(board, current_move, opp_symbol, False)
            value -= self.get_state_utility(state)
        

        
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
        if depth == 4 or status[0] != 'CONTINUE' or time.time() - self.timer >= 23:
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

