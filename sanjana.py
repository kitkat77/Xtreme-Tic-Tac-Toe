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
        self.move_count = 0
        self.is_bonus_move = False
        self.MAX_TIME = 22
        self.WIN_SCORE = 100000000000
    

    # Returns the best move
    def move(self, board, old_move, flag):

        self.move_start_time = time.time()

        self.move_count += 1
        board_copy = copy.deepcopy(board)

        if not self.player and not self.other_player:
            self.player = flag
            self.other_player = 'x' if flag=='o' else 'o'

        depth = 1
        best_move = (-1, -1, -1)
        move = (-1, -1, -1)

        while time.time() - self.move_start_time < self.MAX_TIME:
            best_move = move
            [_, move, _] = self.minimax(board_copy, old_move, flag, depth, float("-inf"), float("inf"), self.is_bonus_move)
            depth += 1
        

        new_board = copy.deepcopy(board)
        new_board.update(old_move, best_move, flag)

        if self.small_board_change(new_board, board) and not self.is_bonus_move:
            self.is_bonus_move = True
        else:
            self.is_bonus_move = False

        return best_move


    # Minimax
    def minimax(self, board, old_move, flag, depth, alpha, beta, bonus_move):

        # Check terminal state
        end_result = board.find_terminal_state()
        if end_result[1] == 'WON':
            return [self.WIN_SCORE if (end_result[0]==self.player and flag==self.player) else -self.WIN_SCORE, None, depth]
        elif end_result[1] == 'DRAW':
            return [self.draw_score(board), None, depth]
    
        # Return if max depth or time out 
        if depth == 0 or time.time() - self.move_start_time > self.MAX_TIME:
            return [self.heuristic(board), None, depth]


        cells = board.find_valid_move_cells(old_move)
        # if self.get_other_player_major_board(board) == 1:
        #     sorted(cells, key=lambda x: x[0], reverse=True)
        # else:
        #     sorted(cells, key=lambda x: x[0])
        sorted(cells, key=lambda x: x[0], reverse=True)

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
                elif score == beta and move_depth > best_depth:
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


    # Draw
    def draw_score(self, board):

        score = 0

        center = corner = other = 0 
        if self.winning(board):
            center, corner, other = 3, 4, 3
        else:
            center, corner, other = 100, 100, 100
        
        scheme = [[corner,other,corner],[other,center,other],[corner,other,corner]]

        for i in range(2):
            for j in range(3):
                for k in range(3):
                    if board.small_boards_status[i][j][k] == self.player:
                        score += scheme[j][k]
                    elif board.small_boards_status[i][j][k] == self.other_player:
                        score -= scheme[j][k]
        
        return score
    

    # Checks is player is winning or not
    def winning(self, board):

        player_win_count = 0
        other_player_win_count = 0

        for i in range(2):
            for j in range(3):
                for k in range(3):
                    if board.small_boards_status[i][j][k] == self.player:
                        player_win_count += 1
                    elif board.small_boards_status[i][j][k] == self.other_player:
                        other_player_win_count += 1
        
        if player_win_count > other_player_win_count:
            return True
        else:
            return False


    # Check other player's major board
    def get_other_player_major_board(self, board):

        board1_count = 0
        board2_count = 0

        for i in range(2):
            for j in range(9):
                for k in range(9):
                    if board.big_boards_status[i][j][k] == self.other_player:
                        if i == 0:
                            board1_count += 1
                        else:
                            board2_count += 1
        
        if board1_count >= board2_count:
            return 1
        else:
            return 2

    # Heuristic
    def heuristic(self, board):
        
        heuristic_score = 0

        small_almost_line_scale = 80
        big_almost_line_scale = 50
        small_weight_scale = 20
        big_weight_scale = 100

        if self.winning(board) or self.move_count > 10:
            small_almost_line_scale = 10
            big_almost_line_scale = 300
            small_weight_scale = 2
            big_weight_scale = 15
    

        small_almost_line = self.small_boards_almost_line(board, self.player) - self.small_boards_almost_line(board, self.other_player)
        big_almost_line = self.big_board_almost_line(board, self.player) - self.big_board_almost_line(board, self.other_player)
        small_weight = self.small_boards_cells_weight(board, self.player) - self.small_boards_cells_weight(board, self.other_player)
        big_weight = self.big_board_cells_weight(board, self.player) - self.big_board_cells_weight(board, self.other_player)

        heuristic_score += small_almost_line * small_almost_line_scale
        heuristic_score += big_almost_line * big_almost_line_scale
        heuristic_score += small_weight * small_weight_scale
        heuristic_score += big_weight * big_weight_scale

        return heuristic_score


    # Give weights to cells
    def weighted_cells(self, board, flag, board_type):

        total_weight = 0

        center = corner = other = 0 
        if board_type == "big":
            center, corner, other = 6, 6, 6
        else:
            center, corner, other = 3, 4, 6
        weights = [[corner,other,corner],[other,center,other],[corner,other,corner]]

        for i in range(3):
            for j in range(3):
                if board[i][j] == flag:
                    total_weight += weights[i][j]
        
        return total_weight
    

    # Returns weights for each big board cell
    def big_board_cells_weight(self, board, flag):

        bb_weight = 0
        for i in range(2):
            bb_weight += self.weighted_cells(board.small_boards_status[i], flag, "big")
        
        return bb_weight
    

    # Returns weight for each cell in all small boards
    def small_boards_cells_weight(self, board, flag):

        sb_weight = 0

        for i in range(2):

            bb = copy.deepcopy(board.big_boards_status[i])
            sb = copy.deepcopy(board.small_boards_status[i])

            for j in range(0, 9, 3):
                for k in range(0, 9, 3):

                    if sb[j/3][k/3] != '-':
                        continue

                    cur_small_board = []

                    for p in range(3):
                        cur_row = []
                        for q in range(3):
                            cur_row.append(bb[j+p][k+q])
                        cur_small_board.append(cur_row)
                    
                    sb_weight += self.weighted_cells(cur_small_board, flag, "small")
        
        return sb_weight


    # Checks if there are 2 in a row
    def almost_row(self, board, flag):
            
        count = 0
        for i in range(3):
            row = board[i]
            if row[0] == flag and row[1] == flag and row[2] == '-':
                count += 1
            if row[0] == flag and row[2] == flag and row[1] == '-':
                count += 1
            if row[2] == flag and row[1] == flag and row[0] == '-':
                count += 1
        
        return count

    
    # Checks if there are two in a column
    def almost_column(self, board, flag):
        
        transpose_board = []
        for i in range(3):
            cur_row = []
            for j in range(3):
                cur_row.append(board[j][i])
            transpose_board.append(cur_row)
        
        return self.almost_row(transpose_board, flag)
    

    # Checks if there are two in a diagonal
    def almost_diagonal(self, board, flag):

        count = 0
        if board[0][0] == flag and board[1][1] == flag and board[2][2] == '-':
            count += 1
        if board[1][1] == flag and board[2][2] == flag and board[0][0] == '-':
            count += 1
        if board[2][2] == flag and board[0][0] == flag and board[1][1] == '-':
            count += 1
        if board[0][2] == flag and board[1][1] == flag and board[2][0] == '-':
            count += 1
        if board[2][0] == flag and board[1][1] == flag and board[0][2] == '-':
            count += 1
        if board[0][2] == flag and board[2][0] == flag and board[1][1] == '-':
            count += 1
        
        return count

    
    # Checks for two in a line in big board
    def big_board_almost_line(self, board, flag):

        count = 0
        for i in range(2):
            count += self.almost_row(board.big_boards_status[i], flag)
            count += self.almost_column(board.big_boards_status[i], flag)
            count += self.almost_diagonal(board.big_boards_status[i], flag)
        
        return count
    

    # Checks for two in a line in small boards
    def small_boards_almost_line(self, board, flag):

        count = 0

        for i in range(2):

            bb = copy.deepcopy(board.big_boards_status[i])
            sb = copy.deepcopy(board.small_boards_status[i])

            for j in range(0, 9, 3):
                for k in range(0, 9, 3):

                    if sb[j/3][k/3] != '-':
                        continue

                    cur_small_board = []

                    for p in range(3):
                        cur_row = []
                        for q in range(3):
                            cur_row.append(bb[j+p][k+q])
                        cur_small_board.append(cur_row)
                    
                    count += self.almost_row(cur_small_board, flag)
                    count += self.almost_column(cur_small_board, flag)
                    count += self.almost_diagonal(cur_small_board, flag)
        
        return count