import sys
import random
import signal
import time
import copy
import traceback


class Random_Player_Old():
	def __init__(self):
		self.max_time = 5
		self.move_start_time = time.time()
		pass


	def small_board_change(self,board1,board2):
		for t in range(2):
			a = board1.small_boards_status[t]
			b = board1.small_boards_status[t]
			for i in range(3):
				for j in range(3):
					if a[i][j] != b[i][j]:
						return 1

		return 0


	# returns score in board for player 'flag'
	def current_score(self,board,flag):
		current_score = 0
		scheme = [[4,6,4],[6,3,6],[4,6,4]]
		for i in range(2):
			for j in range(3):
				for k in range(3):
					if board.small_boards_status[i][j][k] == flag:
						current_score += scheme[j][k]
		return current_score


	# returns number of 2-in-a-row flag for 3x3 board, assuming the board hasnt't been one
	def almost_row(self,board,flag):
		count = 0
		for i in range(3):
			row = board[i]
			if row[0] == flag and row[1] == flag and row[2] == '-':
				count+=1
			if row[0] == flag and row[2] == flag and row[1] == '-':
				count+=1
			if row[2] == flag and row[1] == flag and row[0] == '-':
				count+=1
		return count
						

	def almost_column(self,board,flag):
		b = []
		# transposing
		for i in range(3):
			cur_row = []
			for j in range(3):
				cur_row.append(board[j][i])
			b.append(cur_row)
		return self.almost_row(b,flag)

	def almost_diagonal(self,board,flag):
		count = 0
		if board[0][0] == flag and board[1][1] == flag and board[2][2] == '-':
			count+=1
		elif board[1][1] == flag and board[2][2] == flag and board[0][0] == '-':
			count+=1
		elif board[2][2] == flag and board[0][0] == flag and board[1][1] == '-':
			count+=1
		elif board[0][2] == flag and board[1][1] == flag and board[2][0] == '-':
			count+=1
		elif board[2][0] == flag and board[1][1] == flag and board[0][2] == '-':
			count+=1
		elif board[0][2] == flag and board[2][0] == flag and board[1][1] == '-':
			count+=1
		return count


	# finds number of 2-in-a-line in board for flag for small boards that haven't won yet
	def almost_line_small_boards(self,board,flag):
		counter = 0
		for t in range(2):
			bbs = copy.deepcopy(board.big_boards_status[t])
			sbs = copy.deepcopy(board.small_boards_status[t])
			for i in range(0,9,3):
				for j in range(0,9,3):
				# considering each small board
					# consider only small boards which aren't won
					if sbs[i/3][j/3] != '-':
						continue
					cur_board = []
					for p in range(3):
						cur_row = []
						for q in range(3):
							cur_row.append(bbs[i+p][j+q])
						cur_board.append(cur_row)
					counter += self.almost_row(cur_board,flag)
					counter += self.almost_column(cur_board,flag)
					counter += self.almost_diagonal(cur_board,flag)
		return counter

	# returns number of 2-in-a-line and 3rd empty for small boards as cells
	def almost_line_big_board(self,board,flag):
		counter = 0
		for t in range(2):
			cur_board = board.small_boards_status[t]
			counter += self.almost_row(cur_board,flag)
			counter += self.almost_column(cur_board,flag)
			counter += self.almost_diagonal(cur_board,flag)
		return counter


	# returns weight of a 3x3 board for flag ARBITRARILY DECIDED
	def weighted_cells(self,board,flag):
		total = 0
		#corner weight
		cor = 4
		# center weight
		cen = 6
		# other weight
		oth = 3
		w = [[cor,oth,cor],[oth,cen,oth],[cor,oth,cor]]
		for i in range(3):
			for j in range(3):
				if board[i][j] == flag:
					total += w[i][j]
		return total


	def cells_small_boards(self,board,flag):
		counter = 0
		for t in range(2):
			bbs = copy.deepcopy(board.big_boards_status[t])
			sbs = copy.deepcopy(board.small_boards_status[t])
			for i in range(0,9,3):
				for j in range(0,9,3):
				# considering each small board
					# consider only small boards which aren't won
					if sbs[i/3][j/3] != '-':
						continue
					cur_board = []
					for p in range(3):
						cur_row = []
						for q in range(3):
							cur_row.append(bbs[i+p][j+q])
						cur_board.append(cur_row)
					counter += self.weighted_cells(cur_board,flag)
		return counter

	def cells_big_board(self,board,flag):
		counter = 0
		for t in range(2):
			cur_board = copy.deepcopy(board.small_boards_status[t])
			counter += self.weighted_cells(cur_board,flag)
		return counter


	# returns heuristic for board if flag is the symbol of the player
	def heuristic(self,board,flag):
		other_flag = 'x' if flag=='o' else 'o'
		final = 0
		
		score_heuristic = self.current_score(board,flag) - self.current_score(board,other_flag)
		
		almost_line_score_small = self.almost_line_small_boards(board,flag) - 0.9*self.almost_line_small_boards(board,other_flag)
		
		almost_line_score_big = self.almost_line_big_board(board,flag) - self.almost_line_big_board(board,other_flag)
		
		small_boards_weight = self.cells_small_boards(board,flag) - self.cells_small_boards(board,other_flag)
		
		big_board_weight = self.cells_big_board(board,flag) - self.cells_big_board(board,other_flag)
		
		final += 0.5 * score_heuristic
		final += 10 * almost_line_score_small 
		final += 300 * almost_line_score_big
		final += 2 * small_boards_weight
		final += 15 * big_board_weight


		return final

	def minimax(self, board, old_move, player, flag, depth, alpha, beta, bonus):
		
		cells = board.find_valid_move_cells(old_move)
		random.shuffle(cells)
		
		result = board.find_terminal_state()
		if result[1]=='WON' and player == "max":
			return [100000000000 if (result[0]==flag) else -100000000000, None]
		if result[1]=='WON' and player == "min":
			return [-100000000000 if (result[0]==flag) else 100000000000, None]

		elif result[1]=='DRAW':
			return [2, None]

		if depth==0 or time.time() - self.move_start_time > self.max_time:
			heuristic_score = self.heuristic(board,flag)
			return [heuristic_score, None] #[Score, Move]
		
		#if time.time()-self.move_start_time >= self.max_time:
		#	return ["stop",(-1,-1,-1)]

		# Check for further error handling - what to return if lost
		best_move = (-1, -1, -1) if len(cells)==0 else cells[0]

		next_bonus = 0
		for move in cells:
			next_player = "min" if player == "max" else "max"
			next_bonus = 0
			next_flag =  'o' if (flag=='x') else 'x'
			save_board = copy.deepcopy(board)	
			board.update(old_move, move, flag)
			if bonus == 0:
				player_change = self.small_board_change(save_board,board)
				if player_change == 1:
					next_bonus = 1
					next_player = player
					next_flag = flag
			[score, _] = self.minimax(board, move, next_player,next_flag, depth-1, alpha, beta, next_bonus)
			#if score == "stop":
			#	return ["stop",(-1,-1,-1)]
			if player=="max":
				if score > alpha:
					alpha, best_move = score, move
			else:
				if score < beta:
					beta, best_move = score, move
			board.big_boards_status[move[0]][move[1]][move[2]] = '-'
			board.small_boards_status[move[0]][move[1]/3][move[2]/3] = '-'
			if alpha >= beta or time.time() - self.move_start_time > self.max_time:
				break
		return [alpha if (player=="max") else beta, best_move]

	def move(self, board, old_move, flag):
		# TAKE CARE OF CASE WHEN EVERYTHING IS ALLOWED IN THE BEGINNING
		board_copy = copy.deepcopy(board)
		self.move_start_time = time.time()

		depth = 1
		best_move = (-1, -1, -1)
		move = (-1, -1, -1)
		'''
		while time.time() - self.move_start_time < self.max_time:
			[score, move] = self.minimax(board_copy, old_move, "max", flag, depth, float("-inf"), float("inf"),0)
			depth += 1
			if score != "stop":
				best_move = move
			print depth
		'''
		while time.time() - self.move_start_time < self.max_time:
			best_move = move
			[score, move] = self.minimax(board_copy, old_move, "max", flag, depth, float("-inf"), float("inf"),0)
			depth += 1
			
		return best_move
