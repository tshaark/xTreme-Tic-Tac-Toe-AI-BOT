import random
import sys
import copy
from time import time
import signal
import datetime

class Team28:

    def __init__(self):
        self.available_cells = []
        self.INFINITY = 99999999
        self.symbol = 'x'
        self.begin = 0
        self.max_player_count = 0
        self.win_flag = False
        self.time_limit = 23
        self.next_move = (0 , 0, 0)
        self.small_board_value = ([['-' for i in range(3)] for j in range(3)], [['-' for i in range(3)] for j in range(3)])
        self.block_states = ['DRAW', 'WIN']

        self.WEIGHTS = ((8, 4, 8), (4, 10, 4), (8, 4, 8))

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
            "BASE": 100,
            "BIG_SETUP": 500,
            "DRAW": 100,
            "DEFENCE": 700,
            "DEFENCE_SMALL": 1000,
            "LOSS": -2200,
            "MIDDLE": 0,
            "POST_MIDDLE_WIN": 1300,
            "POST_MIDDLE_LOSS": -3300,
            "OPEN_WIN": 2000,
            "OPEN_LOSS": -4000,
            "PROFIT": 800,
            "POST_LOSS": -3200,
            "POST_WIN": 1200,
            "PRE_LOSS": -1000,
            "PRE_WIN": 800,
            "WIN": 1400,
            "PRE_ULTIMATE_WIN": 1200,
            "ULTIMATE_LOSS": -1000000,
            "ULTIMATE_WIN": 1000000
        }

    def get_base_value(self, r, c):
        return 50 * self.WEIGHTS[r][c]

    def get_current_board_state(self, board, old_move, current_move, symbol):
        opp_symbol = 'x'
        if symbol == 'x':
            opp_symbol = 'o'
 
        cell = (old_move[1] % 3, old_move[2] % 3)
        curr_row = cell[0] * 3
        curr_col = cell[1] * 3
        k = old_move[0]
        state = board.small_boards_status[k][cell[0]][cell[1]]
        pre_win = {'x': False, 'o': False, 'd': False}

        result = "BASE"
        if state != "-":
            if state == "d":
                result = "DRAW"
            elif state == symbol:
                result = "WIN"
            if result != "BASE":
                return result

        for pos in self.WIN_COMBINATIONS:
            cnt = {'x' : 0, 'o' : 0, '-' : 0}
            a = board.big_boards_status[k][curr_row + pos[0][0]][curr_col + pos[0][1]]
            b = board.big_boards_status[k][curr_row + pos[1][0]][curr_col + pos[1][1]]
            c = board.big_boards_status[k][curr_row + pos[2][0]][curr_col + pos[2][1]]

            cnt[a] += 1
            cnt[b] += 1
            cnt[c] += 1
            mov = (current_move[1] % 3, current_move[2] % 3)
            if mov in pos:
                if cnt[symbol] == 2 and cnt['-'] == 1:
                    pre_win[symbol] = True
                elif cnt[opp_symbol] == 2 and cnt[symbol] == 1:
                    pre_win['d'] = True
        
        if pre_win[symbol] == True:
            result = "PRE_WIN"
        elif pre_win['d'] == True:
            result = "DEFENCE_SMALL"
        else:
            result = "BASE"

        return result


    def get_next_board_state(self, board, old_move, symbol, player):
        opp_symbol = 'x'
        if symbol == 'x':
            opp_symbol = 'o'
    
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
                    state[k] = "DRAW"
                continue
            cnt2 = {'x': 0, 'o': 0, '-': 0}
            for i in range(3):
                for j in range(3):
                    x = board.big_boards_status[k][curr_row + i][curr_col + j]
                    cnt2[x] += 1
            if ((cnt2['-'] == 8 or (cnt2['-'] == 7 and cnt2[symbol] == 1)) and (cnt2[opp_symbol] == 1)):
                if player:
                    state[k] = "BASE"
                else:
                    state[k] = "PRE_LOSS"
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
                    state[k] = "LOSS"
            else:
                if player:
                    state[k] = "PROFIT" # defence_small
                else:
                    state[k] = "POST_LOSS"
        
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

    def pre_ultimate_win_state(self, board, move, symbol, player):
        
        state = ""
        pre_win = {'x' : False, 'o': False, 'X' : False, 'O': False}
        opp_symbol = 'x'
        if symbol == 'x':
            opp_symbol = 'o'
 
        for k in range(2):
            for i in range(3):
                for j in range(3):
                    self.small_board_value[k][i][j] = board.small_boards_status[k][i][j]

        k = move[0]
        if self.small_board_value[k][move[1] % 3][move[2] % 3] == '-':
            if player:
                self.small_board_value[k][move[1] %3][move[2] % 3] = symbol
            else:
                self.small_board_value[k][move[1] %3][move[2] % 3] = opp_symbol
        for pos in self.WIN_COMBINATIONS:
            cnt = {'x' : 0, 'o' : 0, '-' : 0, 'd' : 0}
            a = self.small_board_value[k][pos[0][0]][pos[0][1]]
            b = self.small_board_value[k][pos[1][0]][pos[1][1]]
            c = self.small_board_value[k][pos[2][0]][pos[2][1]]

            cnt[a] += 1
            cnt[b] += 1
            cnt[c] += 1

            mov = (move[1] % 3, move[2] % 3)
            if mov in pos:
                if cnt[symbol] == 3:
                    pre_win['X'] = True
                elif cnt[opp_symbol] == 3:
                    pre_win['O'] = True
                elif cnt[symbol] == 2 and cnt['-'] == 1:
                    pre_win[symbol] = True
                elif pre_win[opp_symbol] == 2 and cnt[symbol] == 1:
                    pre_win[opp_symbol] = True

        if pre_win['X']:
            state = "PRE_ULTIMATE_WIN"
        elif pre_win['O']:
            state = "ULTIMATE_LOSS"
        elif pre_win[symbol]:
            state = "BIG_SETUP"
        elif pre_win[opp_symbol]:
            state = "DEFENCE"
        else:
            state = "BASE"
        if not player and state != "ULTIMATE_LOSS":
            state = "BASE"
        return state


    def heuristic(self, board, old_move, current_move, symbol):

        # old_cell = (old_move[1] % 3, old_move[2] % 3)
        current_cell = (current_move[1] % 3, current_move[2] % 3)
        
        opp_symbol = 'x'
        if symbol == 'x':
            opp_symbol = 'o'

        value = 0
        # state = ""

        # CURRENT BOARD UTILITY
        current_state = self.get_current_board_state(board, old_move, current_move, symbol) # win/base/def-small/pre_win/draw/defence-small
        big_state = self.pre_ultimate_win_state(board, old_move, symbol, True)
        if current_state == "BASE":
            value += self.get_base_value(current_cell[0], current_cell[1])
        else:
            if current_state == "PRE_WIN" or current_state == "DEFENCE_SMALL":
                value += self.get_base_value(current_cell[0], current_cell[1])
            value += self.UTILITY[current_state] # (pre)win/loss / base / draw / middle
        if current_state == "WIN":
            self.max_player_count += 1
            if self.max_player_count == 1:
                self.win_flag = True
            if big_state == "PRE_ULTIMATE_WIN":
                value += self.UTILITY["ULTIMATE_WIN"]
            value += self.UTILITY[big_state]

            next_state = self.get_next_board_state(board, current_move, symbol, True)
            value += self.UTILITY[next_state] # post/open-win profit

        else:
            self.max_player_count = 0
            ultimate_loss_state = self.pre_ultimate_win_state(board, current_move, symbol, False)
            if ultimate_loss_state == "BASE":
                value -= self.get_base_value(current_cell[0], current_cell[1])
            else:
                value += self.UTILITY[ultimate_loss_state]
            next_state = self.get_next_board_state(board, current_move, symbol, False)
            value += self.UTILITY[next_state] # post/open-loss pre-loss loss

        return value

    def move(self, board, old_move, symbol):
        self.begin = time()
        self.symbol = symbol
        best_move = old_move
        maxDepth = 1
        val = 0
        self.stop_time = False
        while time() - self.begin < self.time_limit:
            val, move = self.move_ok(board, old_move, symbol, maxDepth)
            best_move = move
            if not self.stop_time:
                # if not maxDepth == 6:
                maxDepth += 1
        self.stop_time = False
        print "value", val, "move", best_move
        return best_move

    def move_ok(self, board, old_move, symbol, depth):
        moves = board.find_valid_move_cells(old_move)
        maxval = -self.INFINITY
        maxi = []
        i = 0
        for move in moves:
            v = self.minimax(board, old_move, move, depth, -self.INFINITY, self.INFINITY, False, symbol)
            # print v
            if v > maxval:
                maxval = v
                maxi = [i]
            elif v == maxval:
                maxi.append(i)
            i += 1
        return maxval, moves[maxi[0]]

    def minimax(self, board, older_move, old_move, depth, alpha, beta, max_player, symbol):
        status = board.find_terminal_state()
            
        if depth == 0 or status[0] != 'CONTINUE' or (time() - self.begin > self.time_limit or self.stop_time):
            self.stop_time = True
            if self.symbol == symbol:
                return self.heuristic(board, older_move, old_move, symbol)
            else:
                return -1 * self.heuristic(board, older_move, old_move, symbol)
        else:
            available_cells = board.find_valid_move_cells(old_move)
            random.shuffle(available_cells)
            score = 0
            for move_cell in available_cells:
                if max_player:
                    score = -self.INFINITY
                    board.update(old_move, move_cell, symbol)
                    if symbol == 'o':
                        next_flag = 'x'
                    else:
                        next_flag = 'o'
                    if self.win_flag:
                        score = max(score, self.minimax(board, old_move, move_cell, depth - 1, alpha, beta, True, next_flag))
                        self.win_flag = False
                    else:
                        score = max(score, self.minimax(board, old_move, move_cell, depth - 1, alpha, beta, False, next_flag))
                        
                    board.big_boards_status[move_cell[0]][move_cell[1]][move_cell[2]] = '-'
                    board.small_boards_status[move_cell[0]][move_cell[1] / 3][move_cell[2] / 3] = '-'
                    alpha = max(alpha, score)
                    if self.stop_time:
                        return score
                else:
                    score = self.INFINITY
                    board.update(old_move, move_cell, symbol)
                    if symbol == 'o':
                        next_flag = 'x'
                    else:
                        next_flag = 'o'
                    if self.win_flag:
                        self.win_flag = False
                        score = min(score, self.minimax(board, old_move, move_cell, depth - 1, alpha, beta, False, next_flag))
                    else:
                        score = min(score, self.minimax(board, old_move, move_cell, depth - 1, alpha, beta, True, next_flag))

                    board.big_boards_status[move_cell[0]][move_cell[1]][move_cell[2]] = '-'
                    board.small_boards_status[move_cell[0]][move_cell[1] / 3][move_cell[2] / 3] = '-'
                    beta = min(beta, score)
                    if self.stop_time:
                        return score
                if alpha >= beta:
                    break

            return score

