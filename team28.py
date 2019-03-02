import random
import sys
import copy
import time
import signal

class Player28:
    def __init__(self):
        self.available_cells = []
        self.infinity=99999999
        self.ninfinity=-99999999
        self.timer=0
        self.symbol='x'
        self.next_move=(0 , 0, 0)

        self.WIN_STATES = [
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
            "PRE_WIN": 500,
            "WIN": 1000,
            "ULTIMATE_WIN": self.infinity + 1
        }

    def utility_win(self, board, old_move, current_move, symbol):
        curr_row = (old_move[1] % 3) * 3
        curr_col = (old_move[2] % 3) * 3
        flag = False

        next_cell = (current_move[1] % 3, current_move[2] % 3)

        k = old_move[0]

        next_cell = (current_move[1]%3, current_move[2]%3)

        for pos in self.WIN_STATES:
                a = board.big_boards_status[k][curr_row + pos[0][0]][curr_col + pos[0][1]]
                b = board.big_boards_status[k][curr_row + pos[1][0]][curr_col + pos[1][1]]
                c = board.big_boards_status[k][curr_row + pos[2][0]][curr_col + pos[2][1]]

                if a == symbol and b == symbol and c == symbol:
                    flag = True
                    break

        if flag:
            return self.UTILITY["WIN"]
        else:
            return self.UTILITY["BASE"]


    def heuristic(self, board, old_move, current_move):
        # curr_row = (old_move[1] % 3) * 3
        # curr_col = (old_move[2] % 3) * 3
        
        value = self.utility_win(board, old_move, current_move, self.symbol)

        return value

    def move(self,board,old_move,symbol):
        self.timer=time.time()
        self.symbol = symbol
        # self.available_cells = board.find_valid_move_cells(old_move)
        value = self.minimax(board, (-1, -1, -1), old_move, 0, self.ninfinity, self.infinity, True, symbol)
        return self.next_move

    
    def minimax(self,board, older_move, old_move, depth, alpha, beta, max_player, symbol):
        status = board.find_terminal_state()
        # if time.time() - self.timer>=23:
        #     return self.heuristic(board,old_move)
        if depth == 3 or status[0] != 'CONTINUE' or time.time()-self.timer>=23:
            if self.symbol == 'x':
                return self.heuristic(board, older_move, old_move)
            else:
                return (-1*self.heuristic(board, older_move, old_move))
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
            



