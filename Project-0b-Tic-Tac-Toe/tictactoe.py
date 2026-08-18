"""
Tic Tac Toe Player
"""

import copy
import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    # Count X's and O's on the board
    x_count = 0
    o_count = 0
    
    for row in board:
        for cell in row:
            if cell == X:
                x_count += 1
            elif cell == O:
                o_count += 1
    
    # X goes first, so if counts are equal, it's X's turn
    if x_count == o_count:
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possible_actions = set()
    
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                possible_actions.add((i, j))
    
    return possible_actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    # Raise exception if action is not valid
    if action not in actions(board):
        raise Exception("Invalid action")
    
    # Deep copy the board to avoid modifying the original
    new_board = copy.deepcopy(board)
    
    # Get current player and make the move
    current_player = player(board)
    i, j = action
    new_board[i][j] = current_player
    
    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Check rows
    for row in board:
        if row[0] == row[1] == row[2] and row[0] is not None:
            return row[0]
    
    # Check columns
    for j in range(3):
        if board[0][j] == board[1][j] == board[2][j] and board[0][j] is not None:
            return board[0][j]
    
    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] is not None:
        return board[0][0]
    
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] is not None:
        return board[0][2]
    
    # No winner
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # Check if there's a winner
    if winner(board) is not None:
        return True
    
    # Check if board is full (no empty cells)
    for row in board:
        for cell in row:
            if cell is None:
                return False
    
    # Board is full and no winner - tie game
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    # If board is terminal, return None
    if terminal(board):
        return None
    
    current_player = player(board)
    best_action = None
    
    if current_player == X:
        # X wants to maximize utility
        best_value = -math.inf
        for action in actions(board):
            new_board = result(board, action)
            value = min_value(new_board)
            if value > best_value:
                best_value = value
                best_action = action
    else:
        # O wants to minimize utility
        best_value = math.inf
        for action in actions(board):
            new_board = result(board, action)
            value = max_value(new_board)
            if value < best_value:
                best_value = value
                best_action = action
    
    return best_action


def max_value(board):
    """
    Helper function for Minimax: returns maximum utility.
    """
    if terminal(board):
        return utility(board)
    
    v = -math.inf
    for action in actions(board):
        v = max(v, min_value(result(board, action)))
    return v


def min_value(board):
    """
    Helper function for Minimax: returns minimum utility.
    """
    if terminal(board):
        return utility(board)
    
    v = math.inf
    for action in actions(board):
        v = min(v, max_value(result(board, action)))
    return v