import random
import time
from extension.board_utils import list_legal_moves_for, take_notes, copy_piece_move
from extension.board_rules import get_result
from chessmaker.chess.base import Player
from chessmaker.chess.results import no_kings, checkmate

class SearchTimeout(Exception):
    pass


#In Pawns not centipawns
PIECE_VALUES = {
    "Pawn": 1,
    "Knight": 3,
    "Bishop": 3,
    "Right": 6,
    "Queen": 9,
    "King": 100
}


def agent(board, player, var):
    start_time = time.perf_counter()
    thinking_time = var[1]

    deadline = start_time + (thinking_time * 0.85)
    piece, move_opt = None, None
    print(f"Ply: {var[0]}")
    
    piece, move_opt = general_stratergy(board, player, var, deadline)
    return piece, move_opt


def general_stratergy(board, player, var, deadline):
    legal_moves = sort_legal(board, player, list_legal_moves_for(board, player))
    opponent = get_opponent(board, player)

    best_move = None
    best_score = float("-inf")
    depth = 1 

    while True:
        try:
            iterative_best_move = None
            iterative_best_score = float("-inf")
            alpha = float("-inf")
            beta = float("inf")

            for piece, move_opt in legal_moves:
                if time.perf_counter() >= deadline:
                    raise SearchTimeout
                
                temp_board = apply_move_to_copy(board, piece, move_opt) 

                if temp_board is None:
                    continue

                current_score = minimax(
                temp_board,
                opponent,
                player,
                depth - 1,
                alpha,
                beta,
                deadline
                )
                print(piece.name, move_opt, current_score)
                
                if current_score > iterative_best_score:
                    iterative_best_move = (piece, move_opt)
                    iterative_best_score = current_score
                alpha = max(alpha, iterative_best_score)
    
            depth += 1
            
            if iterative_best_move is not None:
                best_move = iterative_best_move
                best_score = iterative_best_score
        
        except SearchTimeout:
            print("Search Timeout at depth: " + str(depth))
            print(f"Search Timeout at time: {time.perf_counter():.3f} / {deadline:.3f}")
            break

    if best_move:
        piece, move_opt = best_move
        '''take_notes(piece)
        take_notes(move_opt)
        take_notes(best_score)
        take_notes("Turn " + str(var[0]))'''

        print("SELECTED PIECE:", piece)
        print("SELECTED MOVE:", move_opt)
        print("SELECTED DESTINATION:", move_opt.position)
        print("SELECTED SCORE:", best_score)

        return piece, move_opt
    return None, None


def minimax(board, current_player, maximising_player, depth, alpha, beta, deadline) -> int:
    if time.perf_counter() >= deadline:
        raise SearchTimeout

    result = check_if_board_has_won(board)

    #This is to unwind the recursion quicker if an endstate has been found. 
    if result:
        return evaluate_board(board, maximising_player)

    if depth == 0:
        return evaluate_board(board, maximising_player)

    legal_moves = list_legal_moves_for(board, current_player)
    
    if not legal_moves:
        return evaluate_board(board, maximising_player)

    opponent = get_opponent(board, current_player)

    if current_player == maximising_player:
        maximum = float("-inf")
        
        for piece, move_opt in legal_moves:
            temp_board = apply_move_to_copy(board, piece, move_opt)
            score = minimax(temp_board, opponent, maximising_player, depth - 1, alpha, beta, deadline)
            maximum = max(maximum, score)
            alpha = max(alpha, maximum)

            if alpha >= beta:
                break

        return maximum
    
    else:
        minimum = float("inf")
        
        for piece, move_opt in legal_moves:
            temp_board = apply_move_to_copy(board, piece, move_opt)
            score = minimax(temp_board, opponent, maximising_player, depth - 1, alpha, beta, deadline)
            minimum = min(minimum, score)
            beta = min(beta, minimum)

            if alpha >= beta:
                break

        return minimum


def get_piece_value(piece):
    return PIECE_VALUES.get(piece.name, 0)


def check_if_board_has_won(board):
    for rf in [no_kings, checkmate]:
        res = rf(board)
        if res:
            return res
    return None


def evaluate_board(board, player):
    '''Evaluates the board from the perspective of the passed
    in player. Making note not to get confused. 
    We always pass in MAX player in Minimax for consistency'''
    
    score = 0
    MATESCORE = 10000
    
    #Checkmate eval
    result = check_if_board_has_won(board)

    if result:
        result = result.lower()

        if "white loses" in result:
            winner = Player("black")
        elif "black loses" in result:
            winner = Player("white")
        else:
            return 0
    
        if winner.name == player.name:
            return MATESCORE
        return -MATESCORE

    #General Board Eval
    for piece in board.get_pieces():
        value = PIECE_VALUES.get(piece.name)
        if piece.player == player:
            score += value
        else:
            score -= value

    return score


def sort_legal(board, player, legal):
    #Has time O(mp + m log m)
    scored_moves = []

    for piece, move_opt in legal:
        score = evaluate_move(board, player, piece, move_opt)
        scored_moves.append((score, piece, move_opt))
    
    scored_moves.sort(key=lambda x: x[0], reverse=True)
    return [(piece, move_opt) for score, piece, move_opt in scored_moves]


def evaluate_move(board, player, piece, move_opt) -> int:
    previous_score = evaluate_board(board, player)

    temp_board = apply_move_to_copy(board, piece, move_opt)

    if temp_board is None:
        return float("-inf")

    new_score = evaluate_board(temp_board, player)

    return new_score - previous_score


def apply_move_to_copy(board, piece, move_opt):
    new_board = board.clone()

    new_board, new_piece, new_move = copy_piece_move(
        new_board, piece, move_opt
    )

    if new_piece is None or new_move is None:
        return None

    new_piece.move(new_move)

    return new_board


def get_opponent(board, player):
    for p in board.players:
        if p != player:
            return p