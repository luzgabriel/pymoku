# -*- coding: utf-8 -*-

import numpy as np
import os
import signal
import sys
import copy

EMPTY = "[ ]"
PLAYER1 = "[O]"
PLAYER2 = "[X]"
debug = False
MAX_ROUNDS = 2


#^C handler
def signal_handler(signal, frame):
	print('\nSee you soon!')
	sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

# returns the inicial state of the game, with all the board empty
def get_initial_state():
	state = []
	for i in range(15):
		state.append([EMPTY for j in range(15)])
	return state

# prints a state of the board
def print_state(state):
	s = " "
	for j in range(15):
		s += "  " + str(j).zfill(2)
	print(s)
	i=0;
	for row in state:
		string = ""
		for column in row:
			string += column + " "
		print(str(i).zfill(2) + " " + string)
		i+=1

# returns empty positions
def get_available_positions(state):
	available_positions = []
	for pos_x, row in enumerate(state):
		for pos_y, pos in enumerate(row):
			if pos == EMPTY:
				available_positions.append([pos_x,pos_y])
	return available_positions

# returns empty positions in the bounds established
def get_available_positions_with_bounds(state, bounds):
	available_positions = []
	if len(bounds) == 4:
		bound_x_min = bounds[0]
		bound_x_max = bounds[1]
		bound_y_min = bounds[2]
		bound_y_max = bounds[3]
	else:
		bound_x_min = bounds[0]
		bound_x_max = bounds[0]
		bound_y_min = bounds[0]
		bound_y_max = bounds[0]

	for pos_x, row in enumerate(state):
		for pos_y, pos in enumerate(row):
			if (pos == EMPTY) and (pos_x >= bound_x_min) and (pos_x <= bound_x_max) and (pos_y >= bound_y_min) and (pos_y <= bound_y_max):
				available_positions.append([pos_x,pos_y])
	return available_positions

# given a position (pos) [x,y] of the board, returns if its empty
def is_position_available(state, pos):
	pos_x = pos[0]
	pos_y = pos[1]
	return state[pos_x][pos_y] == EMPTY

# user = PLAYER1 or PLAYER2
def make_move(state, pos, user):
	pos_x = pos[0]
	pos_y = pos[1]
	if is_position_available(state, pos):
		state[pos_x][pos_y] = user
		return True
	return False

def get_bounds(moves):
	if len(moves) == 0:
		return [5,9,5,9] # bounds on center
	min_x = 15
	min_y = 15
	max_x = 0
	max_y = 0
	for move in moves:
		if move[0] < min_x:
			min_x = move[0]
		if move[0] >  max_x:
			max_x = move[0]
		if move[1] < min_y:
			min_y = move[1]
		if move[1] > max_y:
			max_y = move[1]

	if min_x < 2:
		min_x = 2
	if max_x > 12:
		max_x = 12 
	if min_y < 2:
		min_y = 2
	if max_y > 12:
		max_y = 12 
	return [min_x - 2, max_x + 2, min_y - 2, max_y + 2]


#returns sequences in an array
def get_sequences_in_array(array):
	sequences = []
	tmp_seq = []
	tmp_opening = 0
	for i, item in enumerate(array):
		if i > 0:
			last_item = array[i-1]
			if item != EMPTY:
				if last_item != item:
					if last_item == EMPTY:
						tmp_opening = 1
						tmp_seq.append(item)
					else:
						if(len(tmp_seq) > 1):
							sequences.append([tmp_seq[0], tmp_opening, len(tmp_seq)])
						tmp_seq = []
						tmp_opening = 0
				else:
					if(len(tmp_seq) < 1):
						tmp_seq.append(last_item)
					tmp_seq.append(item)
			elif last_item != item:
				if len(tmp_seq) > 1:
					sequences.append([tmp_seq[0], tmp_opening+1, len(tmp_seq)])
				tmp_seq = []
				tmp_opening = 0
	if len(tmp_seq) > 1:
		sequences.append([tmp_seq[0], tmp_opening, len(tmp_seq)])
	return sequences

# returns an array of sequences
def get_horizontal_sequences(state):
	sequences = []
	a = np.array(state)
	for row in range(15):
		sequences += get_sequences_in_array(a[row,:])
	return sequences

# returns an array of sequences
def get_vertical_sequences(state):
	a = np.array(state)
	sequences = []
	for col in range(15):
		sequences += get_sequences_in_array(a[:,col])
	return sequences

# returns an array of sequences
def get_diagonal_sequences(state):
	sequences = []
	x,y = 15,15
	a = np.array(state)
	diags = [a[::-1,:].diagonal(i) for i in range(-a.shape[0]+1,a.shape[1])]
	diags.extend(a.diagonal(i) for i in range(a.shape[1]-1,-a.shape[0],-1))
	diagonals = [n.tolist() for n in diags]
	for diagonal in diagonals:
		sequences += get_sequences_in_array(diagonal)
	return sequences


# returns score given the length of a sequence
def get_sequence_score(length):
	if length == 2:
		return 1
	elif length == 3:
		return 812
	elif length == 4:
		return 591136
	elif length == 5:
		return 38305612800000


def get_heuristic(state, player, round_number):
	all_sequences = []
	for sequence in get_horizontal_sequences(state):
		all_sequences.append(sequence)
	for sequence in get_vertical_sequences(state):
		all_sequences.append(sequence)
	for sequence in get_diagonal_sequences(state):
		all_sequences.append(sequence)

	player1_score = 0
	player2_score = 0
	for sequence in all_sequences:
		if len(sequence) > 0:
			if sequence[2] == 2:
				if sequence[0] == PLAYER1:
					player1_score += get_sequence_score(2)*sequence[1]
				else:
					player2_score += get_sequence_score(2)*sequence[1]

			elif sequence[2] == 3:
				if sequence[0] == PLAYER1:
					player1_score += get_sequence_score(3)*sequence[1]
				else:
					player2_score += get_sequence_score(3)*sequence[1]

			elif sequence[2] == 4:
				if sequence[0] == PLAYER1:
					player1_score += get_sequence_score(4)*sequence[1]
				else:
					player2_score += get_sequence_score(4)*sequence[1]

			elif sequence[2] >= 5:
				if sequence[0] == PLAYER1:
					player1_score += get_sequence_score(5)
				else:
					player2_score += get_sequence_score(5)

	if (player == PLAYER1):
		return ((player1_score - player2_score)*255)/round_number
	else:
		return ((player2_score - player1_score)*255)/round_number

def alpha_beta(player, state, alpha, beta, rounds, round_number, bounds):
	possible_moves = get_available_positions_with_bounds(state, bounds)
	bestMove = [-1,-1]
	maximum = MAX_ROUNDS
	#if round_number > 25:
		#maximum = 4
	if ((len(possible_moves) == 0) or (rounds >= maximum)):
		score = get_heuristic(state, player, round_number+rounds)
		return [score, bestMove]
	else:
		if(player == PLAYER2):
			for move in possible_moves:
				tmp_state = [copy.copy(element) for element in state]
				make_move(tmp_state, move, player)
				score = alpha_beta(PLAYER1, tmp_state, alpha, beta, rounds+1, round_number, bounds)[0]
				if score > alpha:
					alpha = score
					bestMove = move
				if alpha >= beta:
					return [alpha, bestMove]
			return [alpha, bestMove]
		else:
			for move in possible_moves:
				tmp_state = [copy.copy(element) for element in state]
				make_move(tmp_state, move, player)
				score = alpha_beta(PLAYER2, tmp_state, alpha,beta, rounds + 1, round_number, bounds)[0]
				if score < beta:
					beta = score
					bestMove = move
				if alpha >= beta:
					return [beta, bestMove]
			return [beta, bestMove]
		if rounds == 0:
			return [score, bestMove]

#returns best move using minimax algorithm
def get_pc_move(state, round_number, bounds):
	tmp = alpha_beta(PLAYER2, state,(-sys.maxsize-1), sys.maxsize, 0, round_number, bounds)
	return tmp[1]

#starts game agains AI
def start_game_single_player():
		round_number = 1
		moves = []
		print("Start game")
		state = get_initial_state()
		turn = PLAYER1

		all_sequences = []
		win = False
		winner = None

		while win == False:
			print_header()
			print_state(state)

			if len(get_available_positions(state)) == 0:
				print("No more available positions. It's a tie!")
				break

			all_sequences = []
			for sequence in get_horizontal_sequences(state):
				all_sequences.append(sequence)
			for sequence in get_vertical_sequences(state):
				all_sequences.append(sequence)
			for sequence in get_diagonal_sequences(state):
				all_sequences.append(sequence)

			player1_score = 0
			player2_score = 0
			for sequence in all_sequences:
				if len(sequence) > 0:
					if sequence[2] == 2:
						if sequence[0] == PLAYER1:
							player1_score += get_sequence_score(2)*sequence[1]
						else:
							player2_score += get_sequence_score(2)*sequence[1]
						if debug: print("Dupla de " + str(sequence[0]) + " com " + str(sequence[1]) + " abertura(s)")
					elif sequence[2] == 3:
						if sequence[0] == PLAYER1:
							player1_score += get_sequence_score(3)*sequence[1]
						else:
							player2_score += get_sequence_score(3)*sequence[1]
						if debug: print("Tripla de " + str(sequence[0]) + " com " + str(sequence[1]) + " abertura(s)")
					elif sequence[2] == 4:
						if sequence[0] == PLAYER1:
							player1_score += get_sequence_score(4)*sequence[1]
						else:
							player2_score += get_sequence_score(4)*sequence[1]
						if debug: print("Quadrupla de " + str(sequence[0]) + " com " + str(sequence[1]) + " abertura(s)")
					elif sequence[2] >= 5:
						if sequence[0] == PLAYER1:
							player1_score += get_sequence_score(5)*sequence[1]
						else:
							player2_score += get_sequence_score(5)*sequence[1]
						if debug: print("Quintupla de " + str(sequence[0]) + " com " + str(sequence[1]) + " abertura(s)")
						win = True
						winner = sequence[0]
			if debug:
				print("SCORE<"+str(PLAYER1)+">: "+str(player1_score)+ "    SCORE<"+str(PLAYER2)+">: "+str(player2_score))
			if win == True:
				print("Game ended")
				break

			if turn == PLAYER1:
				move = False
				while move == False:
					print("Player " + turn + "'s turn:")
					error = False
					try:
						row = int(raw_input("row: "))
						col = int(raw_input("col: "))
						move = make_move(state, [row,col], turn)
						moves.append([row,col])
						round_number += 1
					except IndexError:
						print("Please insert values between 0 and 14")
						error = True
					except ValueError:
						print("Please insert values between 0 and 14")
						error = True
					if error == False and move == False:
						print("Position is busy")

			else:
				bounds = get_bounds(moves)
				make_move(state, get_pc_move(state, round_number, bounds), turn)
				round_number += 1

			if turn == PLAYER1:
				turn = PLAYER2
			elif turn == PLAYER2:
				turn = PLAYER1

		if win:
			print("\nPLAYER "+ str(winner) + " WINS")
		print("Play again? [Y/n]")
		exit = False
		while not exit:
			user_input = raw_input("")
			if (user_input == "y"):
				start_game_single_player()
			elif (user_input == "n"):
				print_menu()
			else:
				print("Invalid option")

def print_header():

	if debug:
		print(" === === === === === ===  DEBUG === === === === === === === ===")
	else:
		os.system('tput reset')
	print(" === === === === === ===  === === === === === === === === ===")
	print(" === === === === === ===  PYMOKU		=== === === === === === ===")
	print(" === === === === === ===  === === === === === === === === ===")

#Stats game person vs person
def start_game_pvp():
	print("Start game")
	state = get_initial_state()
	turn = PLAYER1

	all_sequences = []
	win = False
	winner = None

	while win == False:
		print_header()
		print_state(state)

		if len(get_available_positions(state)) == 0:
			print("No more available positions. It's a tie!")
			break

		all_sequences = []
		for sequence in get_horizontal_sequences(state):
			all_sequences.append(sequence)
		for sequence in get_vertical_sequences(state):
			all_sequences.append(sequence)
		for sequence in get_diagonal_sequences(state):
			all_sequences.append(sequence)

		player1_score = 0
		player2_score = 0
		for sequence in all_sequences:
			if len(sequence) > 0:
				if sequence[2] == 2:
					if sequence[0] == PLAYER1:
						player1_score += get_sequence_score(2)*sequence[1]
					else:
						player2_score += get_sequence_score(2)*sequence[1]
					if debug: print("Dupla de " + str(sequence[0]) + " com " + str(sequence[1]) + " abertura(s)")
				elif sequence[2] == 3:
					if sequence[0] == PLAYER1:
						player1_score += get_sequence_score(3)*sequence[1]
					else:
						player2_score += get_sequence_score(3)*sequence[1]
					if debug: print("Tripla de " + str(sequence[0]) + " com " + str(sequence[1]) + " abertura(s)")
				elif sequence[2] == 4:
					if sequence[0] == PLAYER1:
						player1_score += get_sequence_score(4)*sequence[1]
					else:
						player2_score += get_sequence_score(4)*sequence[1]
					if debug: print("Quadrupla de " + str(sequence[0]) + " com " + str(sequence[1]) + " abertura(s)")
				elif sequence[2] >= 5:
					if sequence[0] == PLAYER1:
						player1_score += get_sequence_score(5)*sequence[1]
					else:
						player2_score += get_sequence_score(5)*sequence[1]
					if debug: print("Quintupla de " + str(sequence[0]) + " com " + str(sequence[1]) + " abertura(s)")
					win = True
					winner = sequence[0]
		if debug: print("SCORE<"+str(PLAYER1)+">: "+str(player1_score)+ "    SCORE<"+str(PLAYER2)+">: "+str(player2_score))
		if win == True:
			print("Game ended")
			break

		move = False
		while move == False:
			print("Player " + turn + "'s turn:")
			error = False
			try:
				row = int(raw_input("row: "))
				col = int(raw_input("col: "))
				move = make_move(state, [row,col], turn)
			except IndexError:
				print("Please insert values between 0 and 14")
				error = True
			except ValueError:
				print("Please insert values between 0 and 14")
				error = True
			if error == False and move == False:
				print("Position is busy")

		if turn == PLAYER1:
			turn = PLAYER2
		elif turn == PLAYER2:
			turn = PLAYER1

	if win:
		print("\nPLAYER "+ str(winner) + " WINS")
	print("Play again? [Y/n]")
	exit = False
	while not exit:
		user_input = raw_input("")
		if (user_input == "y"):
			start_game_pvp()
		elif (user_input == "n"):
			print_menu()
		else:
			print("Invalid option")

def print_menu():
	if debug:
		print("=== === ===  DEBUG  === === === ===")
	else:
		os.system('tput reset')
	print("=== === === === === === === === ===")
	print("=== === ===   PYMOKU    === === ===")
	print("=== === === === === === === === ===")
	print("===		MENU		===")
	print("=== === === === === === === === ===")
	print("=== 1. Player vs Player 	===")
	print("=== 2. Player vs Computer 	===")
	print("=== 3. Exit Game		===")
	print("=== === === === === === === === ===")
	exit = False
	while not exit:
		user_input = raw_input("=== Insert option: ")
		if user_input == "1":
			start_game_pvp()
		elif user_input == "2":
			start_game_single_player()
		elif user_input == "3":
			exit = True
			print("See you soon!")
			sys.exit(0)
		else:
			print("Invalid option")

if __name__ == "__main__" :
	if len(sys.argv) > 1:
		if sys.argv[1] == 'debug':
			debug = True
	print_menu()
