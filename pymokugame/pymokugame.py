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


# given a position (pos) [x,y] of the board, returns if its empty
def is_position_available(state, pos):
	return state[pos[0]][pos[1]] == EMPTY


def get_positions_bounded(state, moves):
	positions = []
	for move in moves:
		move_x = move[0]
		move_y = move[1]
		for i in range(5):
			for j in range(5):
				new_bound_x = move_x + (i - 2)
				new_bound_y = move_y + (j - 2)
				if (new_bound_x >= 0) and (new_bound_y >= 0) and (new_bound_x < 15) and (new_bound_y < 15):
					if ([new_bound_x, new_bound_y] not in positions) and (state[new_bound_x][new_bound_y] == EMPTY):
						positions.append([new_bound_x,new_bound_y])
	return positions


# user = PLAYER1 or PLAYER2
def make_move(state, pos, user):
	if is_position_available(state, pos):
		state[pos[0]][pos[1]] = user
		return True
	return False


def get_vertical_from_position(state, pos):
	a = np.array(state)
	return a[:,pos[1]]


def get_horizontal_from_position(state, pos):
	a = np.array(state)
	return a[pos[0],:]


def get_sequences_from_positions(state, moves):
	sequences = []
	visited = []
	for move in moves:
		if move[1] not in visited:
			vertical = get_vertical_from_position(state,move)
			sequence = get_sequences_in_array(vertical)
			visited.append(move[1])
			if len(sequence) > 0:
				sequences.extend(sequence)

		if move[0]+15 not in visited:
			horizontal = get_horizontal_from_position(state,move)
			sequence = get_sequences_in_array(horizontal)
			visited.append(move[0]+15)
			if len(sequence) > 0:
				sequences.extend(sequence)

	return sequences


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
		return 383056128


def get_all_sequences(state, moves):
	all_sequences = (get_sequences_from_positions(state,moves))
	for sequence in get_diagonal_sequences(state):
		all_sequences.append(sequence)
	return all_sequences


def exists_winner(state, moves):
	all_sequences = get_all_sequences(state, moves)
	for sequence in all_sequences:
		if len(sequence) > 0:
			if sequence[2] == 5:
				return sequence[0]
	return EMPTY


def get_heuristic(state, player, round_number, moves):
	all_sequences = get_all_sequences(state, moves)
	score = 0
	for sequence in all_sequences:
		if len(sequence) > 0:
			for i in range(2, 5):
				if sequence[2] == i:
					score = score + get_sequence_score(i)*sequence[1] if sequence[0] == PLAYER2 else score - get_sequence_score(i)*sequence[1]
					break;
			if sequence[2] >= 5:
				score = score + get_sequence_score(5) if sequence[0] == PLAYER2 else score - get_sequence_score(5)
	return (score*225)/round_number


def unmake_move(state, move):
	state[move[0]][move[1]] = EMPTY


def alpha_beta(player, state, alpha, beta, rounds, round_number, moves):
	possible_moves = get_positions_bounded(state, moves)
	bestMove = [-1,-1]
	maximum = MAX_ROUNDS

	if ((len(possible_moves) == 0) or (rounds >= maximum)):
		score = get_heuristic(state, player, round_number+rounds,moves)
		return [score, bestMove]
	else:
		for move in possible_moves:
			make_move(state, move, player)
			moves.append(move)
			score = alpha_beta(PLAYER2 if player==PLAYER1 else PLAYER1, state, alpha,beta, rounds + 1, round_number, moves)[0]
			unmake_move(state, move)
			moves.remove(move)
			if(player == PLAYER2):
				if score > alpha:
					alpha = score
					bestMove = move
			else:
				if score < beta:
					beta = score
					bestMove = move
			if alpha >= beta:
				return [alpha if player==PLAYER2 else beta, bestMove]
		return [alpha if player==PLAYER2 else beta, bestMove]


#returns best move using minimax algorithm
def get_pc_move(state, round_number, moves):
	return alpha_beta(PLAYER2, state,(-sys.maxsize-1), sys.maxsize, 0, round_number, moves)[1]


def start_game(pvp):
	round_number = 1
	moves = []
	state = get_initial_state()
	turn = get_initial_player(pvp)
	winner = EMPTY
	print_header()
	print_state(state)
	while winner == EMPTY:
		if len(moves) == 225:
			break
		if (turn == PLAYER2) and (len(moves) == 0):
			make_move(state, [7,7], turn)
		else:
			move = input_position(turn, state) if turn==PLAYER1 or pvp else get_pc_move(state, round_number, moves)
			make_move(state, move, turn)
			moves.append(move)
		round_number += 1
		winner = exists_winner(state, moves)
		turn = PLAYER2 if turn==PLAYER1 else PLAYER1
		print_header()
		print_state(state)
	game_over(winner, pvp)


def print_header():
	if debug:
		print(" === === === === === ===  DEBUG === === === === === === === ===")
	else:
		os.system('tput reset')
	print(" === === === === === ===  === === === === === === === === ===")
	print(" === === === === === ===  PYMOKU  === === === === === === ===")
	print(" === === === === === ===  === === === === === === === === ===")


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
		user_input = input("=== Insert option: ")
		if user_input == "1":
			start_game(True)
		elif user_input == "2":
			start_game(False)
		elif user_input == "3":
			exit = True
			print("See you soon!")
			sys.exit(0)
		else:
			print("Invalid option")


def get_initial_player(pvp):
	if pvp:
		return PLAYER1
	else:
		while(True):
			user_input = input("=== Insert 1 for HUMAN first, or 2 for COMPUTER first: ")
			if user_input == "1":
				return PLAYER1
			elif user_input == "2":
				return PLAYER2
			print("Not a valid entry")


def game_over(winner, pvp):
	print("GAME OVER")
	print("\nPLAYER "+ str(winner) + " WINS" if winner != EMPTY else "No more available positions. It's a tie!")
	print("Play again? [Y/n]")
	exit = False
	while not exit:
		user_input = input("")
		if (user_input == "y"):
			start_game(pvp)
		elif (user_input == "n"):
			print_menu()
		else:
			print("Invalid option")


def input_position(turn,state):
	while True:
		try:
			print("Player " + turn + "'s turn:")
			row = int(input("row: "))
			col = int(input("col: "))
			if (row > 15 or col > 15):
				print("Please insert values between 0 and 14")
			elif not is_position_available(state, [row,col]):
				print("Position is busy")
			else:
				return [row,col]
		except IndexError:
			print("Please insert values between 0 and 14")
		except ValueError:
			print("Please insert values between 0 and 14")
	return []

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

def main():
	if len(sys.argv) > 1:
		if sys.argv[1] == 'debug':
			debug = True
	print_menu()

if __name__ == "__main__":
	main()
