# Python 3.11+
import sys, time
from itertools import cycle
from chessmaker.chess.base import Board
from extension.board_utils import list_legal_moves_for, take_notes, copy_piece_move
from extension.board_rules import get_result, thinking_with_timeout, THINKING_TIME_BUDGET, GAME_TIME_BUDGET
from samples import white, black, sample0, sample1, sample2
from agent_main import agent, evaluate_board, apply_move_to_copy
from agent_main175 import opponent
from test_fullgame import make_custom_board

board, players = make_custom_board(sample0)

print("Before:", board.current_player.name)

piece, move = list_legal_moves_for(board, board.current_player)[0]

new_board = apply_move_to_copy(board, piece, move)

print("Original:", board.current_player.name)
print("New:", new_board.current_player.name)