import numpy as np
from typing import Tuple, Optional

class ConnectFourAI:
    """
    AI player using minimax algorithm with alpha-beta pruning
    Includes heuristic evaluation of board positions
    """
    def __init__(self, game):
        self.game = game
        self.PLAYER = 1  # Human player
        self.AI = 2      # AI player
        self.MAX_DEPTH = 6 # Increased depth for better lookahead
    
    def set_player_number(self, player_num: int):
        """
        Set whether AI is player 1 or 2
        """
        self.AI = player_num
        self.PLAYER = 1 if player_num == 2 else 2
    
    def evaluate_window(self, window: list, player: int) -> int:
        """
        Enhanced window evaluation with better win detection
        """
        score = 0
        opponent = self.PLAYER if player == self.AI else self.AI
        
        # Winning patterns
        if window.count(player) == 4:
            score += 1000000000  # Immediate win - highest priority
        elif window.count(player) == 3 and window.count(0) == 1:
            score += 50000000   # Potential win next move
            # Check if the empty spot is accessible
            empty_index = window.index(0)
            if self._is_accessible_in_window(window, empty_index):
                score *= 2  # Double score for immediately playable wins
        elif window.count(opponent) == 3 and window.count(0) == 1:
            score -= 900000000  # Must block opponent's win
        
        # Building patterns
        elif window.count(player) == 2 and window.count(0) == 2:
            score += 5000
            # Check if both empty spots are accessible
            if all(self._is_accessible_in_window(window, i) for i, val in enumerate(window) if val == 0):
                score *= 2  # Double score for immediately playable threats
                
        return score
    
    def _is_accessible_in_window(self, window: list, pos: int) -> bool:
        """Check if a position in a window is playable (all spaces below are filled)"""
        return all(i == pos or window[i] != 0 for i in range(pos + 1, len(window)))
    
    def score_position(self, board: np.ndarray, player: int) -> int:
        """
        Enhanced position evaluation with stronger center preference
        """
        score = 0
        opponent = self.PLAYER if player == self.AI else self.AI

        # Check for immediate threats first
        for col in range(self.game.COLS):
            row = self.get_next_row(board, col)
            if row is not None:
                board_copy = board.copy()
                board_copy[row][col] = opponent
                if self.is_winning_move(board_copy, row, col, opponent):
                    score -= 1000000000

        # Stronger center control preference
        center_array = [int(i) for i in list(board[:, 3])]
        score += center_array.count(player) * 8000  # Increased from 6000

        # Adjacent to center also more valuable
        for col in [2, 4]:
            col_array = [int(i) for i in list(board[:, col])]
            score += col_array.count(player) * 5000  # Increased from 4000
            
            # Extra bonus for controlling center and adjacent
            if col_array.count(player) > 0 and center_array.count(player) > 0:
                score += 3000

        # Evaluate all possible windows
        for row in range(self.game.ROWS):
            for col in range(self.game.COLS-3):
                # Horizontal windows
                window = list(board[row, col:col+4])
                score += self.evaluate_window(window, player)

                # Check for trapped opponent pieces
                if col < self.game.COLS-4:
                    extended_window = list(board[row, col:col+5])
                    if extended_window.count(opponent) >= 2:
                        score += 3000  # Bonus for trapping opponent

        # Vertical windows
        for col in range(self.game.COLS):
            col_array = [int(i) for i in list(board[:,col])]
            for row in range(self.game.ROWS-3):
                window = col_array[row:row+4]
                score += self.evaluate_window(window, player) * 1.2  # Slightly prefer vertical threats

        return score
        
    def _evaluate_immediate_threats(self, board: np.ndarray, player: int, opponent: int) -> int:
        score = 0
        
        # Check for winning moves and immediate threats
        for col in range(self.game.COLS):
            row = self.get_next_row(board, col)
            if row is not None:
                # Check if we can win
                board_copy = board.copy()
                board_copy[row][col] = player
                if self.is_winning_move(board_copy, row, col, player):
                    score += 1000000000
                
                # Check if opponent can win
                board_copy = board.copy()
                board_copy[row][col] = opponent
                if self.is_winning_move(board_copy, row, col, opponent):
                    score -= 500000000
                    
        return score
        
    def _evaluate_future_threats(self, board: np.ndarray, player: int, opponent: int) -> int:
        score = 0
        
        # Look for two-move win setups
        for col in range(self.game.COLS):
            row = self.get_next_row(board, col)
            if row is not None:
                # Try our first move
                board_copy = board.copy()
                board_copy[row][col] = player
                
                # Check if this creates a fork (two winning moves)
                winning_moves = 0
                for col2 in range(self.game.COLS):
                    row2 = self.get_next_row(board_copy, col2)
                    if row2 is not None:
                        board_copy2 = board_copy.copy()
                        board_copy2[row2][col2] = player
                        if self.is_winning_move(board_copy2, row2, col2, player):
                            winning_moves += 1
                
                if winning_moves >= 2:  # Found a fork
                    score += 100000
                    
        # Look for diagonal threats
        for row in range(self.game.ROWS-3):
            for col in range(self.game.COLS-3):
                window = [board[row+i][col+i] for i in range(4)]
                if window.count(player) == 2 and window.count(0) == 2:
                    # Check if both empty spaces are accessible
                    empty_positions = [(row+i, col+i) for i in range(4) if window[i] == 0]
                    if all(self._is_accessible(board, r, c) for r, c in empty_positions):
                        score += 5000
                        
        return score
        
    def _evaluate_position_control(self, board: np.ndarray, player: int, opponent: int) -> int:
        score = 0
        
        # Center column control (most important)
        center_array = [int(i) for i in list(board[:, 3])]
        score += center_array.count(player) * 8000
        
        # Control of columns adjacent to center
        for col in [2, 4]:
            col_array = [int(i) for i in list(board[:, col])]
            score += col_array.count(player) * 6000
            
            # Detect developing threats
            if col_array.count(player) >= 2:
                score += 3000
                
        # Progressive row weighting (bottom rows worth more)
        for row in range(self.game.ROWS):
            row_weight = (self.game.ROWS - row) * 300
            row_array = [int(i) for i in list(board[row,:])]
            
            # Look for connected pieces
            for col in range(self.game.COLS-1):
                if board[row][col] == player and board[row][col+1] == player:
                    score += 1000 * row_weight
                    
        return score
        
    def _is_accessible(self, board: np.ndarray, row: int, col: int) -> bool:
        """Check if a position can be played (all spaces below are filled)"""
        return all(board[r][col] != 0 for r in range(self.game.ROWS-1, row, -1))
    
    def get_next_row(self, board: np.ndarray, col: int) -> Optional[int]:
        """Helper method to find next available row"""
        for row in range(self.game.ROWS-1, -1, -1):
            if board[row][col] == 0:
                return row
        return None
    
    def allows_opponent_win(self, board: np.ndarray, opponent: int) -> bool:
        """Check if current position allows opponent to win next move"""
        for col in range(self.game.COLS):
            row = self.get_next_row(board, col)
            if row is not None:
                board_copy = board.copy()
                board_copy[row][col] = opponent
                if self.is_winning_move(board_copy, row, col, opponent):
                    return True
        return False
    
    def is_winning_move(self, board: np.ndarray, row: int, col: int, player: int) -> bool:
        """Check if a move is winning"""
        # Check horizontal
        for c in range(max(0, col-3), min(col+1, self.game.COLS-3)):
            if all(board[row][c+i] == player for i in range(4)):
                return True
                
        # Check vertical
        if row <= self.game.ROWS-4:
            if all(board[row+i][col] == player for i in range(4)):
                return True
                
        # Check positive diagonal
        for i in range(-3, 1):
            r, c = row-i, col-i
            if (0 <= r <= self.game.ROWS-4 and 0 <= c <= self.game.COLS-4 and
                all(board[r+j][c+j] == player for j in range(4))):
                return True
                
        # Check negative diagonal
        for i in range(-3, 1):
            r, c = row+i, col-i
            if (3 <= r < self.game.ROWS and 0 <= c <= self.game.COLS-4 and
                all(board[r-j][c+j] == player for j in range(4))):
                return True
                
        return False
    
    def minimax(self, board: np.ndarray, depth: int, alpha: float, beta: float, 
                maximizing_player: bool) -> Tuple[int, int]:
        """
        Minimax algorithm with alpha-beta pruning
        Searches game tree to specified depth
        Returns (column, score) tuple
        Uses alpha-beta pruning to reduce search space
        """
        valid_locations = [col for col in range(self.game.COLS) 
                         if self.game.is_valid_move(col)]
        
        # Check for winning moves first
        for col in valid_locations:
            row = self.game.get_next_open_row(col)
            if row is not None:
                # Check if AI can win immediately
                board_copy = board.copy()
                board_copy[row][col] = self.AI
                if self.is_winning_move(board_copy, row, col, self.AI):
                    return col, float('inf')
        
        # Then check for blocking moves
        for col in valid_locations:
            row = self.game.get_next_open_row(col)
            if row is not None:
                board_copy = board.copy()
                board_copy[row][col] = self.PLAYER
                if self.is_winning_move(board_copy, row, col, self.PLAYER):
                    return col, float('inf') - 1  # Slightly less than winning
        
        # Continue with regular minimax if no immediate wins/blocks
        is_terminal = self.game.check_winner() is not None or self.game.is_board_full()
        if depth == 0 or is_terminal:
            if is_terminal:
                winner = self.game.check_winner()
                if winner == self.AI:
                    return (None, float('inf'))
                elif winner == self.PLAYER:
                    return (None, float('-inf'))
                else:
                    return (None, 0)
            else:
                return (None, self.score_position(board, self.AI))
        
        # Maximizing player (AI)
        if maximizing_player:
            value = float('-inf')
            column = valid_locations[0]
            for col in valid_locations:
                row = self.game.get_next_open_row(col)
                board_copy = board.copy()
                board_copy[row][col] = self.AI
                new_score = self.minimax(board_copy, depth-1, alpha, beta, False)[1]
                if new_score > value:
                    value = new_score
                    column = col
                alpha = max(alpha, value)
                if alpha >= beta:
                    break  # Beta cutoff
            return column, value
        
        # Minimizing player (Human)
        else:
            value = float('inf')
            column = valid_locations[0]
            for col in valid_locations:
                row = self.game.get_next_open_row(col)
                board_copy = board.copy()
                board_copy[row][col] = self.PLAYER
                new_score = self.minimax(board_copy, depth-1, alpha, beta, True)[1]
                if new_score < value:
                    value = new_score
                    column = col
                beta = min(beta, value)
                if alpha >= beta:
                    break  # Alpha cutoff
            return column, value
    
    def get_best_move(self) -> int:
        """
        Get best move with enhanced win detection
        """
        # First check for immediate winning moves
        for col in range(self.game.COLS):
            row = self.get_next_row(self.game.board, col)
            if row is not None:
                board_copy = self.game.board.copy()
                board_copy[row][col] = self.AI
                if self.is_winning_move(board_copy, row, col, self.AI):
                    return col  # Take winning move immediately

        # Then check for opponent's winning moves to block
        for col in range(self.game.COLS):
            row = self.get_next_row(self.game.board, col)
            if row is not None:
                board_copy = self.game.board.copy()
                board_copy[row][col] = self.PLAYER
                if self.is_winning_move(board_copy, row, col, self.PLAYER):
                    return col  # Block opponent's win

        # Look for forced wins (winning moves after current move)
        for col in range(self.game.COLS):
            row = self.get_next_row(self.game.board, col)
            if row is not None:
                board_copy = self.game.board.copy()
                board_copy[row][col] = self.AI
                # Check if this move creates a guaranteed win next turn
                winning_moves = 0
                for next_col in range(self.game.COLS):
                    next_row = self.get_next_row(board_copy, next_col)
                    if next_row is not None:
                        next_board = board_copy.copy()
                        next_board[next_row][next_col] = self.AI
                        if self.is_winning_move(next_board, next_row, next_col, self.AI):
                            winning_moves += 1
                if winning_moves >= 2:  # Found a forcing move
                    return col

        # Use minimax for other moves
        col, _ = self.minimax(self.game.board, self.MAX_DEPTH, float('-inf'), 
                            float('inf'), True)
        return col

    def is_empty_board(self) -> bool:
        """Check if the board is empty"""
        return np.all(self.game.board == 0)

    def _evaluate_window(self, window: list, player: int) -> int:
        opponent = self.PLAYER if player == self.AI else self.AI
        score = 0

        if window.count(player) == 4:
            score += 100000
        elif window.count(player) == 3 and window.count(0) == 1:
            score += 5000
        elif window.count(player) == 2 and window.count(0) == 2:
            score += 500
        
        if window.count(opponent) == 3 and window.count(0) == 1:
            score -= 80000  # Increased penalty for opponent's threats

        return score