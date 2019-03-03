import sys
import random
import signal
import time
import copy
import traceback

class Random_Player_Old():


    def __init__(self):
        self.player = None
        self.other_player = None
        self.move_start_time = time.time()
        self.MAX_TIME = 15
        self.WIN_SCORE = 100000000000
    

    # Returns the best move
    def move(self, board, old_move, flag):

        self.move_start_time = time.time()
        board_copy = copy.deepcopy(board)

        if not self.player and not self.other_player:
            self.player = flag
            self.other_player = 'x' if flag=='o' else 'o'

        depth = 1
        best_move = (-1, -1, -1)
        move = (-1, -1, -1)

        while time.time() - self.move_start_time < self.MAX_TIME:
            best_move = move
            [_, move, _] = self.minimax(board_copy, old_move, flag, depth, float("-inf"), float("inf"), False)
            depth += 1
        
        return best_move


    # Minimax
    def minimax(self, board, old_move, flag, depth, alpha, beta, bonus_move):

        # Check terminal state
        end_result = board.find_terminal_state()
        if end_result[1] == 'WON':
            return [self.WIN_SCORE if end_result[0]==self.player else -self.WIN_SCORE, None, depth]
        elif end_result[1] == 'DRAW':
            return [2, None, depth] #CHANGE
    

        # Return if max depth or time out 
        if depth == 0 or time.time() - self.move_start_time > self.MAX_TIME:
            return [0, None, depth] #CHANGE


        cells = board.find_valid_move_cells(old_move)
        original_board = copy.deepcopy(board)
        best_move = (-1, -1, -1) if len(cells)==0 else cells[0]
        best_depth = -1 if (flag==self.player) else 100000000000

        for move in cells:

            next_bonus_move = False
            next_flag = 'o' if (flag=='x') else 'x'
            board.update(old_move, move, flag)

            if (not bonus_move) and self.small_board_change(board, original_board):
                next_bonus_move = True
                next_flag = flag
            
            [score, _, move_depth] = self.minimax(board, move, next_flag, depth-1, alpha, beta, next_bonus_move)

            if self.player == flag:
                if score > alpha:
                    alpha, best_move, best_depth = score, move, move_depth
                elif score == alpha and move_depth > best_depth:
                    best_move, best_depth = move, move_depth
            else:
                if score < beta:
                    beta, best_move, best_depth = score, move, move_depth
                elif score == beta and move_depth < best_depth:
                    best_move, best_depth = move, move_depth
            
            board.big_boards_status[move[0]][move[1]][move[2]] = '-'
            board.small_boards_status[move[0]][move[1]/3][move[2]/3] = '-'

            if alpha >= beta or time.time() - self.move_start_time > self.MAX_TIME:
                break
            
        return [alpha if self.player==flag else beta, best_move, best_depth]
                    

    # Compare two small boards
    def small_board_change(self, board1, board2):

        for board_no in range(2):
            small_board1 = board1.small_boards_status[board_no]
            small_board2 = board2.small_boards_status[board_no]
            for i in range(3):
                for j in range(3):
                    if small_board1[i][j] != small_board2[i][j]:
                        return True
        
        return False
