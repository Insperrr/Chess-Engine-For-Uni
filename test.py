# Python 3.11+
import sys, time
from itertools import cycle
from chessmaker.chess.base import Board
from extension.board_utils import print_board_ascii, copy_piece_move
from extension.board_rules import get_result, thinking_with_timeout, THINKING_TIME_BUDGET, GAME_TIME_BUDGET
from samples import white, black, sample0, sample1, sample2
from agent_main import agent, evaluate_board
from agent_main175 import opponent
from test_fullgame import make_custom_board


board1, players1 = make_custom_board(sample0)
board2, players2 = make_custom_board(sample2)

score1 = evaluate_board(board1, players1[0])  # White
score2 = evaluate_board(board2, players2[1])  # Black

print("Original position (White perspective):", score1)
print("Mirrored position (Black perspective):", score2)
print("Difference:", abs(score1 - score2))