# -*- coding: utf-8 -*-

import numpy as np
import os
import signal
import sys

def signal_handler(signal, frame):
        print('\nSee you soon!')
        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

EMPTY = "[ ]"
PLAYER1 = "[O]"
PLAYER2 = "[X]"

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
	print s
	i=0;
	for row in state:
		string = ""
		for column in row:
			string += column + " "
		print str(i).zfill(2) + " " + string
		i+=1
		# print string

# returns empty positions
def get_available_positions(state):
	available_positions = []
	for pos_x, row in enumerate(state):
		for pos_y, pos in enumerate(row):
			if pos == EMPTY:
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

#returns all diagonals in state
def get_all_diagonals(state):
	x,y = 15,15
	a = np.array(state)
	diags = [a[::-1,:].diagonal(i) for i in range(-a.shape[0]+1,a.shape[1])]
	diags.extend(a.diagonal(i) for i in range(a.shape[1]-1,-a.shape[0],-1))
	diagonals = [n.tolist() for n in diags]
	return diagonals

# returns an array of sequences
def get_diagonal_sequences(state):
	sequences = []
	diagonals = get_all_diagonals(state)
	for diagonal in diagonals:
		sequences += get_sequences_in_array(diagonal)
	return sequences

"""
TO-DO: TEM QUE RETORNAR A QUANTIDADE DE ABERTURAS DE CADA DUPLA, TRIPLA, QUÁDRUPLA PRA USAR NO CALCULO DA HEURISTICA

==== Heuristica ====
	Dupla 		= +1
	Tripla 		= +812
	Quadrupla 	= +591136
	Quintupla 	= +383056128
"""

# TO-DO
# returns the score for the current state (using heuristics)
def get_score(state):
	pass


def start_game_pvp():
	print "Start game"
	state = get_initial_state()
	turn = PLAYER1

	all_sequences = []
	win = False
	winner = None

	while win == False:
		os.system('tput reset')
		print " === === === === === ===  === === === === === === === === ==="
		print " === === === === === ===  PYMOKU  === === === === === === ==="
		print " === === === === === ===  === === === === === === === === ==="
		if len(get_available_positions(state)) == 0:
			print "Nao ha mais posicoes disponiveis, empate."
			break

		all_sequences = []
		for sequence in get_horizontal_sequences(state):
			all_sequences.append(sequence)
		for sequence in get_vertical_sequences(state):
			all_sequences.append(sequence)
		for sequence in get_diagonal_sequences(state):
			all_sequences.append(sequence)


		print_state(state)
		for sequence in all_sequences:
			# print "seq" + str(sequence)
			if len(sequence) > 0:
				if sequence[2] == 2:
					print "Dupla de " + str(sequence[0]) + " com " + str(sequence[1]) + " abertura(s)"
				elif sequence[2] == 3:
					print "Tripla de " + str(sequence[0]) + " com " + str(sequence[1]) + " abertura(s)"
				elif sequence[2] == 4:
					print "Quadrupla de " + str(sequence[0]) + " com " + str(sequence[1]) + " abertura(s)"
				elif sequence[2] == 5:
					print "Quintupla de " + str(sequence[0]) + " com " + str(sequence[1]) + " abertura(s)"
					win = True
					winner = sequence[0]
					break

		if win == True:
			print "Game ended"
			break

		move = False
		while move == False:
			print "Jogador " + turn + ", e a sua vez: "
			error = False
			try:
				row = int(raw_input("linha: "))
				col = int(raw_input("coluna: "))
				move = make_move(state, [row,col], turn)
			except IndexError:
				print "Por favor, insira valores entre 0 e 14"
				error = True
			except ValueError:
				print "Por favor, insira valores entre 0 e 14"
				error = True
			if error == False and move == False:
				print "Posicao atualmente ocupada, escolha outra"


		if turn == PLAYER1:
			turn = PLAYER2
		elif turn == PLAYER2:
			turn = PLAYER1

	if win == True:
		print "\nThe Winner is player"+ str(winner)
		print_menu()


def print_menu():
	print "=== === === === === === === === ==="
	print "=== === === GOMOKU GAME === === ==="
	print "=== === === === === === === === ==="
	print "===		MENU		==="
	print "=== === === === === === === === ==="
	#print "=== MENU:	       		==="
	print "=== 1. Player vs Player 	==="
	print "=== 2. Player vs Computer 	==="
	print "=== 3. Exit Game		==="
	print "=== === === === === === === === ==="


if __name__ == "__main__" :
	os.system('tput reset')
	print_menu()
	exit = False
	while exit == False:
		user_input = raw_input("=== Insira: ")
		if user_input == "1":
			start_game_pvp()
		elif user_input == "2":
			"Em breve este recurso estara disponivel"
		elif user_input == "3":
			exit = True
			print "Ate mais!"
		else:
			print "Opcao invalida!"
