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
        self.next_move=(0,0,0)

    def heuristic(self,board,old_move):
        return random.randrange(50)

    def move(self,board,old_move,symbol):
        self.timer=time.time()
        self.symbol = symbol
        # self.available_cells = board.find_valid_move_cells(old_move)
        value = self.minimax(board,old_move,0,self.ninfinity,self.infinity,True,symbol)
        return self.next_move

    
    def minimax(self,board,old_move,depth,alpha,beta,max_player,symbol):
        status = board.find_terminal_state()
        if time.time()-self.timer>=23:
            return self.heuristic()
        if depth == 3 or status[0] != 'CONTINUE':
            if self.symbol == 'x':
                return self.heuristic(board, old_move)
            else:
                return (0 - self.heuristic(board, old_move))
        if max_player:
            value = self.ninfinity
            self.available_cells = board.find_valid_move_cells(old_move)
            random.shuffle(self.available_cells)
            for move in self.available_cells:
                board.update(old_move, move, symbol)
                if symbol == 'x':
                    next_flag = 'o'
                else:
                    next_flag = 'x'
                child_value = self.minimax(board, move, depth + 1, alpha, beta, False, next_flag)
                board.big_boards_status[move[0]][move[1]][move[2]] = '-'
                board.small_boards_status[move[0]][move[1] / 3][move[2] / 3] = '-'
                if child_value > value:
                    value = child_value
                    if depth == 0:
                        self.next_move = copy.deepcopy(move)
                alpha = max(alpha, value)				
                if beta <= alpha:
                    break
            return value

        else:
            value = self.infinity
            self.available_cells = board.find_valid_move_cells(old_move)
            random.shuffle(self.available_cells)
            for move in self.available_cells:
                board.update(old_move, move, symbol)
                if symbol == 'x':
                    next_flag = 'o'
                else:
                    next_flag = 'x'
                child_value = self.minimax(board, move, depth + 1, alpha, beta, True, next_flag)
                board.big_boards_status[move[0]][move[1]][move[2]] = '-'
                board.small_boards_status[move[0]][move[1] / 3][move[2] / 3] = '-'
                if child_value < value:
                    value = child_value
                    if depth == 0:
                        self.next_move = copy.deepcopy(move)
                beta = min(beta, value)				
                if beta <= alpha:
                    break
            return value
            



