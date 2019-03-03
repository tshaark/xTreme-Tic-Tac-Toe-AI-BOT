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
        self.depthSoFar = 3
        self.next_move = (0 , 0, 0)
        self.small_board_value = ([['-' for i in range(3)] for j in range(3)], [['-' for i in range(3)] for j in range(3)])
        
        self.STATES = [
            "BASE",
            "BIG_SETUP",
            "DRAW",
            "LOSS",
            "MIDDLE",
            "OPEN_WIN",
            "OPEN_LOSS",
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

        self.WEIGHTS = ((6, 4, 6), (4, 10, 4), (6, 4, 6))

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

        # 2700 b + win + open
        # 2700 b + win + post_middle
        # 2700 b + win + post_win
        # 2700 b + win + post_lost
        # 2000 p + mid +
        # 1800 p + pre_win
        # 1700 b + mid
        # 1500 b + pre_win
        # 1400 p + draw
        # 1100 b + draw
        # 1050 p + base
        # 750 b + base
        # 0 p + pre_loss
        # -300 b + pre_loss

        self.UTILITY = {
            "BASE": 500,
            "BIG_SETUP": 8000,
            "DRAW": 1000,
            "LOSS": -1000,
            "MIDDLE": 1500,
            "POST_MIDDLE_WIN": 3000,
            "POST_MIDDLE_LOSS": -9000,
            "OPEN_WIN": 6000,
            "OPEN_LOSS": -600,
            "POST_LOSS": -8000,
            "POST_WIN": 2500,
            "PRE_LOSS": -1500,
            "PRE_WIN": 2000,
            "WIN": 5000,
            "PRE_ULTIMATE_WIN": 10000, # rand
            "ULTIMATE_LOSS": self.ninfinity,
            "ULTIMATE_WIN": self.infinity
        }

    def get_base_value(self, state, r, c):
        return 20 * self.UTILITY["BASE"] * self.WEIGHTS[r][c]

    def get_current_board_state(self, board, old_move, symbol):
        
        cell = (old_move[1] % 3, old_move[2] % 3)
        curr_row = cell[0] * 3
        curr_col = cell[1] * 3
        k = old_move[0]
        state = board.small_boards_status[k][cell[0]][cell[1]]
        pre_win = {'x': False, 'o': False}

        result = ""
        if state != "-":
            if state == "d":
                result = "DRAW"
            elif state == symbol:
                result = "WIN"
            else:
                result = "LOSS"

        for pos in self.WIN_COMBINATIONS:
            cnt = {'x' : 0, 'o' : 0, '-' : 0}
            a = board.big_boards_status[k][curr_row + pos[0][0]][curr_col + pos[0][1]]
            b = board.big_boards_status[k][curr_row + pos[1][0]][curr_col + pos[1][1]]
            c = board.big_boards_status[k][curr_row + pos[2][0]][curr_col + pos[2][1]]

            cnt[a] += 1
            cnt[b] += 1
            cnt[c] += 1
            if cnt['x'] == 2 and cnt['-'] == 1:
                pre_win['x'] = True
            elif cnt['o'] == 2 and cnt['-'] == 1:
                pre_win['o'] = True
            # elif cnt[symbol] == '1' and cnt['-'] == 2:

        if not pre_win['x'] and not pre_win['o']:
            result = "BASE"
        elif pre_win['x'] and pre_win['o']:
            result = "MIDDLE"
        elif pre_win[symbol]:
            result = "PRE_WIN"
        else:
            result = "PRE_LOSS"

        return result


    def get_next_board_state(self, board, old_move, symbol, player):
        
        cell = (old_move[1] % 3, old_move[2] % 3)
        curr_row = cell[0] * 3
        curr_col = cell[1] * 3

        pre_win = {'x': False, 'o': False}
        state = ["", ""]
        result = ""

        for k in range(2):

            # check if board state for win/loss/draw
            temp_state = board.small_boards_status[k][cell[0]][cell[1]]
            if temp_state != '-':
                if temp_state == 'd':
                    state[k] = "DRAW"
                elif temp_state == symbol:
                    state[k] = "WIN"
                else:
                    state[k] = "LOSS"
                continue
                
            for pos in self.WIN_COMBINATIONS:
                cnt = {'x' : 0, 'o' : 0, '-' : 0}
                a = board.big_boards_status[k][curr_row + pos[0][0]][curr_col + pos[0][1]]
                b = board.big_boards_status[k][curr_row + pos[1][0]][curr_col + pos[1][1]]
                c = board.big_boards_status[k][curr_row + pos[2][0]][curr_col + pos[2][1]]

                cnt[a] += 1
                cnt[b] += 1
                cnt[c] += 1
                if cnt['x'] == 2 and cnt['-'] == 1:
                    pre_win['x'] = True
                elif cnt['o'] == 2 and cnt['-'] == 1:
                    pre_win['o'] = True
            
            if not pre_win['x'] and not pre_win['o']:
                state[k] = "BASE"
            elif pre_win['x'] and pre_win['o']:
                if player:
                    state[k] = "POST_MIDDLE_WIN"
                else:
                    state[k] = "POST_MIDDLE_LOSS"
            elif pre_win[symbol]:
                if player:
                    state[k] = "POST_WIN"
                else:
                    state[k] = "POST_LOSS"
            else:
                if player:
                    state[k] = "POST_LOSS"
                else:
                    state[k] = "POST_WIN"
        
        if player:
            if (self.UTILITY[state[0]] > self.UTILITY[state[1]]):
                result = state[0]
            else:
                result = state[1]
        else:
            if (self.UTILITY[state[0]] > self.UTILITY[state[1]]):
                result = state[1]
            else:
                result = state[0]

        # getting state considering both big boards
        if state[0] in self.block_states and state[1] in self.block_states:
            if player:
                result = "OPEN_WIN"
            else:
                result = "OPEN_LOSS"
        elif state[0] in self.block_states:
            result = state[1]
        elif state[1] in self.block_states:
            result = state[0]

        # print result
        return result

    def pre_ultimate_win_state(self, board, move, symbol):
        
        state = ""
        pre_win = {'x' : False, 'o': False, 'X' : False}
        opp_symbol = 'x'
        if self.symbol == 'x':
            opp_symbol = 'o'
 
        for k in range(2):
            for i in range(3):
                for j in range(3):
                    self.small_board_value[k][i][j] = board.small_boards_status[k][i][j]

        k = move[0]
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
            state = "PRE_ULTIMATE_WIN"
        elif pre_win[symbol]:
            state = "BIG_SETUP"
        else:
            state = "BASE"
        
        return state


    def get_state_utility(self, state):
        # possible additions ?? >>>> FOUND IT!!!
        # if state == "BASE":
        #     pass
        return self.UTILITY[state]

    def heuristic(self, board, old_move, current_move, symbol):

        old_cell = (old_move[1] % 3, old_move[2] % 3)
        # current_cell = (current_move[1] % 3, old_move[2] % 3)

        opp_symbol = 'x'
        if symbol == 'x':
            opp_symbol = 'o'
        value = 0
        state = ""

        # CURRENT BOARD UTILITY
        state = self.get_current_board_state(board, old_move, symbol)
        if state == "BASE":
            value += self.get_base_value(state, old_cell[0], old_cell[1])
        else:
            value += self.UTILITY[state] # (pre)win/loss / base / draw / middle

        big_state = self.pre_ultimate_win_state(board, old_move, symbol)
        if state == "WIN":
            if big_state == "PRE_ULTIMATE_WIN":
                return self.UTILITY["ULTIMATE_WIN"]

            state = self.get_next_board_state(board, current_move, symbol, True)
            value += self.get_state_utility(state) # post-middle/win/loss / open
        # NEXT CELL UTILITY
        else:
            state = self.get_next_board_state(board, current_move, symbol, False)
            value += self.UTILITY[state] # post-middle/win/loss / open

        value += self.UTILITY[big_state] # BIG_SETUP, PRE_U_W

        # print value
        return value

    def move(self, board, old_move, symbol):
        self.timer=time.time()
        self.symbol = symbol
        self.depthSoFar = 4
        while(time.time() - self.timer < 10):
            value = self.minimax(board, (-1, -1, -1), old_move, 0, self.ninfinity, self.infinity, True, symbol)
        return self.next_move

    
    def minimax(self, board, older_move, old_move, depth, alpha, beta, max_player, symbol):
        status = board.find_terminal_state()
        if depth == self.depthSoFar or status[0] != 'CONTINUE' or time.time() - self.timer >= 22:
            self.depthSoFar += 1
            if self.symbol == symbol:
                return self.heuristic(board, older_move, old_move, symbol)
            else:
                return (-1 * self.heuristic(board, older_move, old_move, symbol))
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

