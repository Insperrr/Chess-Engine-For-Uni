import time, random
from extension.board_utils import list_legal_moves_for, take_notes, copy_piece_move
from extension.board_rules import get_result


def opponent(board, player, var):

    # Constants

    # Hardcoded opening moves for best starts (for sample0, sample1 setups)
    OPENING_MOVES_1 = [ # Opening moves when agent plays as white 
        {"key": "nqkbrppppp     PPPPPRBKQN", "piece": "Pawn", "pos": (3, 3), "to": (3, 2)},
        {"key": "rqknbppppp     PPPPPBNKQR", "piece": "Pawn", "pos": (0, 3), "to": (0, 2)}
    ]
    OPENING_MOVES_2 = [  # Opening move when agent plays as black 
        {"key": " qkbrppppp n   PPPPPRBKQN", "piece": "Pawn", "pos": (0, 3), "to": (1, 2)},
        {"key": "nqkb ppppp   r PPPPPRBKQN", "piece": "Pawn", "pos": (4, 3), "to": (3, 2)},
        {"key": "nqkbr ppppp    PPPPPRBKQN", "piece": "Pawn", "pos": (3, 3), "to": (3, 2)},
        {"key": "nqkbrp ppp p   PPPPPRBKQN", "piece": "Pawn", "pos": (0, 3), "to": (1, 2)},
        {"key": "nqkbrpp pp  p  PPPPPRBKQN", "piece": "Pawn", "pos": (1, 3), "to": (2, 2)},
        {"key": "nqkbrppp p   p PPPPPRBKQN", "piece": "Pawn", "pos": (4, 3), "to": (3, 2)},
        {"key": "nqkbrpppp     pPPPPPRBKQN", "piece": "Pawn", "pos": (3, 3), "to": (4, 2)},

        {"key": " qknbppppp r   PPPPPBNKQR", "piece": "Pawn", "pos": (0, 3), "to": (1, 2)},
        {"key": "rqk bppppp  n  PPPPPBNKQR", "piece": "Pawn", "pos": (3, 3), "to": (2, 2)},
        {"key": "rqk bppppp    nPPPPPBNKQR", "piece": "Pawn", "pos": (3, 3), "to": (4, 2)},
        {"key": "rqknb ppppp    PPPPPBNKQR", "piece": "Pawn", "pos": (1, 3), "to": (0, 2)},
        {"key": "rqknbp ppp p   PPPPPBNKQR", "piece": "Pawn", "pos": (0, 3), "to": (1, 2)},
        {"key": "rqknbpp pp  p  PPPPPBNKQR", "piece": "Pawn", "pos": (1, 3), "to": (2, 2)},
        {"key": "rqknbppp p   p PPPPPBNKQR", "piece": "Pawn", "pos": (4, 3), "to": (3, 2)},
        {"key": "rqknbpppp     pPPPPPBNKQR", "piece": "Pawn", "pos": (3, 3), "to": (4, 2)}
    ]

    # Piece values
    PIECE_VALUES = {
        'Pawn': 325,    # Pawn
        'Right': 650,   # Right
        'Knight': 350,  # Knight
        'Bishop': 300,  # Bishop
        'Queen': 650,   # Queen
        'King': 0       # King (has no value, will never be taken)
    }

    # Piece-square tables
    PIECE_SQUARE_TABLES = {
        "Pawn": [
            [  0,   0,   0,   0,   0],
            [ 20,  15,  10,  15,  25],
            [ 30,  25,  20,  25,  30],
            [  5,  10,  15,  10,   5],
            [  0,   0,   0,   0,   0]
        ],

        "Knight": [
            [ -20,  10,  20,  10, -20],
            [  10,  25,  35,  25,  10],
            [  20,  35,  50,  35,  20],
            [  10,  25,  35,  25,  10],
            [ -20,  10,  20,  10, -20]
        ],

        "Bishop": [
            [ -10,   0,  10,   0, -10],
            [   0,  20,  25,  20,   0],
            [  10,  30,  40,  30,  10],
            [   0,  20,  25,  20,   0],
            [ -10,   0,  10,   0, -10]
        ],

        "Rook": [
            [ 20,  25,  25,  25,  20],
            [ 25,  30,  35,  30,  25],
            [ 35,  40,  25,  40,  35],
            [ 25,  30,  35,  30,  25],
            [ 20,  25,  25,  25,  20]
        ],

        "Right": [
            [  0,  20,  30,  20,   0],
            [ 20,  35,  35,  35,  20],
            [ 40,  50,  40,  50,  40],
            [ 20,  35,  35,  35,  20],
            [  0,  20,  30,  20,   0]
        ],

        "Queen": [
            [ 30,  20,  30,  20,  30],
            [ 20,  30,  40,  30,  20],
            [ 30,  40,  50,  40,  30],
            [ 20,  30,  40,  30,  20],
            [ 30,  20,  30,  20,  30]
        ],

        "King": [
            [ -50, -25, -10, -25, -50],
            [ -25,   0,  10,   0, -25],
            [ -10,  10,  20,  10, -10],
            [ -25,   0,  10,   0, -25],
            [ -50, -25, -10, -25, -50]
        ]
    }

    # Global variables
    t_table = {} # Transposition table
    r_table = {} # Results table (caches previous calculated results)
    think_start = 9e20 # Global variable to calculate total elapsed thinking time


    # Gets all legal moves for a specific player
    def get_legal_moves(_board, mine): # mine: True = agent's moves, False = opponent's moves
        if mine:
            return list_legal_moves_for(_board, board.players[0] if player == board.players[0] else board.players[1])
        return list_legal_moves_for(_board, board.players[1] if player == board.players[0] else board.players[0])


    # Generates a key to identify each board state for t_table and r_table
    def gen_key(_board):
        key_table = [' ' for i in range(25)]
        for piece in _board.get_pieces():
            name = "N" if piece.name == "Knight" else piece.name[0]
            key_table[piece.position.y * 5 + piece.position.x] = name if piece.player == board.players[0] else name.lower()
        key = ''.join(key_table)
        return key


    # Gets result of a board state either from a r_table or get_result() (then stores to r_table)
    def get_result_with_r_table(board):
        nonlocal r_table
        key = gen_key(board)
        if not key in r_table:
            result = get_result(board)
            if result:
                if "Checkmate - " in result or "Stalemate - " in result:
                    r_table[key] = (1, player.name in result)
                elif "Draw - " in result:
                    r_table[key] = (2, player.name in result)
                else:
                    r_table[key] = (0, False)
            else:
                r_table[key] = (0, False)
        return r_table[key]


    # Evaluates any given chessboard state
    def evaluate_board(board, player, depth):
        nonlocal PIECE_VALUES, PIECE_SQUARE_TABLES

        key = gen_key(board)
        if key in t_table:
            return (1 if player.name == "white" else -1) * t_table[key]

        total_score = 0
        for piece in board.get_pieces():
            if piece:
                piece_player = piece.player.name  # 'white' for white, 'black' for black
                piece_type = piece.name    # 'Knight', 'Pawn', 'King', 'Queen', etc.
                piece_value = PIECE_VALUES.get(piece_type, 0)  # Get the piece value

                # Get the piece-square table value (positioning value)
                if piece_type in PIECE_SQUARE_TABLES:
                    piece_square_value = PIECE_SQUARE_TABLES[piece_type][piece.position.y][piece.position.x]

                    # Adjust score based on color
                    if player.name == piece_player:
                        total_score += piece_value + piece_square_value  # Add score for the players's pieces
                    else:
                        total_score -= piece_value + piece_square_value  # Subtract score for the opponent's pieces
    
        t_table[key] = total_score
        return total_score


    # Negative min-max algorithm
    def negamax(board_current, depth, alpha, beta, color):
        key = gen_key(board_current)
        result = get_result_with_r_table(board_current)
        if depth == 0 or result[0] != 0:  # Base case indicating either a terminal node or maximum depth reached
            if result[0] == 1: # Checkmate or Stalemate
                return -100000000 * (999 if result[1] else (depth + 1))
            elif result == 2: # Draw
                return 1000000 * (1 if result[1] else (depth + 1))
            return color * (evaluate_board(board_current, player, depth + 1)) # Evaluate the position and multiply by color (1 for maximizing player, -1 for minimizing player)
        
        # If less than 1 second of thinking time left, consider node as terminal (negative score) and exit algorithm
        if (var[1] - (time.perf_counter() - think_start)) < 1:
            return color * -1000000

        best_value = -9e20 # Start with the worst possible value
        for (p_piece, p_move_opt) in get_legal_moves(board_current, True if color == 1 else False):
            board_tmp = board_current.clone() # Clone board to make a full copy rather than a shallow copy
            board_tmp, piece, move_opt = copy_piece_move(board_tmp, p_piece, p_move_opt)
            piece.move(move_opt)

            value = -negamax(board_tmp, depth - 1, -beta, -alpha, -color) # Recursion with a negated value

            if value > best_value:
                best_value = value
                if best_value >= 100000000:
                    return best_value
            
            # Alpha-beta pruning
            alpha = max(alpha, best_value)
            if alpha >= beta:
                break

        return best_value


    # Calculates the best move with a variable depth using IDS (iterative deepening search)
    def best_move():
        best_value = -9e20
        best_move = (None, None, None)
        depth = 2 # Starts with depth 2 as a general minimum for all board states

        while True:
            legal_moves = list_legal_moves_for(board, player)
            if len(legal_moves) == 0:
                take_notes(f"No moves left to discover, finishing move at depth {depth} with value {best_value}.")
                return best_moves

            for (p_piece, p_move_opt) in list_legal_moves_for(board, player):
                board_tmp = board.clone()
                board_tmp, piece, move_opt = copy_piece_move(board_tmp, p_piece, p_move_opt)
                piece.move(move_opt)
                
                value = -negamax(board_tmp, depth - 1, -9e20, 9e20, -1)
                if value > best_value:
                    best_value = value
                    best_move = (best_value, p_piece, p_move_opt)
                
                # If less than 1 second of thinking time left, return current best move
                if (var[1] - (time.perf_counter() - think_start)) < 1:
                    take_notes(f"Close to thinking time out, finishing move at depth {depth} with value {best_value}.")
                    return best_move
            
            depth += 1 # IDS

        return best_move
    

    """"
    This is an example of your designed Agent

    Parameters
    ----------
    board: the current chess board
    player: your assigned player role (white or black)
    var:  [ply, THINKING_TIME_BUDGET] a list cotaining the ply ID and the thinking_time_budget (secs)

    Returns
    -------
    piece: your selected chess piece
    move_opt: your selected move of your selected chess piece
    
    Hints:
    -----
    - List of players on the current board game: list(board.players) - default list: [Player (white), Player (black)]
    - board.players[0].name = "white" and board.players[1].name = "black"
    - Name of the player assigned to the Agent (either "white" or "black"): player.name
    - list of pieces of the current player: list(board.get_player_pieces(player))
    - List of pieces and corresponding moves for each pieces of the player: piece, move_opt = list_legal_moves_for(board, player)
    - From var: ply ID = var[0], timeout = var[1]
    - Use the timeout variable together with time.perf_counter()
    to ensure the agent returns its best move before the time limit expires.
    """

    think_start = time.perf_counter()
    piece, move_opt = None, None

    key = gen_key(board)
    for opening_move in OPENING_MOVES_1:
        # If matching one of the opening moves in OPENING_MOVES_1
        if key == opening_move["key"] or key.swapcase() == opening_move["key"]:
            if player.name == "white":
                pos = opening_move["pos"]
                to  = opening_move["to"]
            else:
                pos = (4 - opening_move["pos"][0], 4 - opening_move["pos"][1])
                to  = (4 - opening_move["to"][0], 4 - opening_move["to"][1])
            for (p_piece, p_move_opt) in list_legal_moves_for(board, player):
                if p_piece.name == opening_move["piece"] and \
                    p_piece.position.x == pos[0] and p_piece.position.y == pos[1] and \
                    p_move_opt.position.x == to[0] and p_move_opt.position.y == to[1]:
                    take_notes("Executing opening move")
                    return p_piece, p_move_opt # TODO: add take_notes()
    else:
        # If matching one of the opening moves in OPENING_MOVES_2
        for opening_move in OPENING_MOVES_2:
            if (key == opening_move["key"] and player.name == "white") or \
               (key.swapcase() == opening_move["key"] and player.name == "black"):
                pos = opening_move["pos"]
                to  = opening_move["to"]
                for (p_piece, p_move_opt) in list_legal_moves_for(board, player):
                    if p_piece.name == opening_move["piece"] and \
                        p_piece.position.x == pos[0] and p_piece.position.y == pos[1] and \
                        p_move_opt.position.x == to[0] and p_move_opt.position.y == to[1]:
                        take_notes("Executing follow-up opening move")
                        return p_piece, p_move_opt # TODO: add take_notes()
            elif (key[::-1] == opening_move["key"] and player.name == "white") or \
                 (key[::-1].swapcase() == opening_move["key"] and player.name == "black"):
                pos = (4 - opening_move["pos"][0], 4 - opening_move["pos"][1])
                to  = (4 - opening_move["to"][0], 4 - opening_move["to"][1])
                for (p_piece, p_move_opt) in list_legal_moves_for(board, player):
                    if p_piece.name == opening_move["piece"] and \
                        p_piece.position.x == pos[0] and p_piece.position.y == pos[1] and \
                        p_move_opt.position.x == to[0] and p_move_opt.position.y == to[1]:
                        take_notes("Executing follow-up opening move")
                        return p_piece, p_move_opt

        # Otherwise, calculate and execute best move
        best_value, piece, move_opt = best_move()
        return piece, move_opt
