from typing import List, Tuple, Optional
import numpy as np

class ConnectFour:
    """
    Main game logic class for Connect Four
    Handles the game board and basic game mechanics
    """
    def __init__(self):
        # Initialize game board dimensions
        self.ROWS = 6
        self.COLS = 7
        # Create empty board using numpy (0 represents empty cell)
        self.board = np.zeros((self.ROWS, self.COLS), dtype=int)
        # Track current player (1 for human, 2 for AI)
        self.current_player = 1
        
    def is_valid_move(self, col: int) -> bool:
        # Column must be in range and the top cell must be empty
        return 0 <= col < self.COLS and self.board[0, col] == 0

    
    def get_next_open_row(self, col: int) -> Optional[int]:
        """
        Find the next available row in the given column
        Returns row index or None if column is full
        Searches from bottom to top due to gravity
        """
        for row in range(self.ROWS-1, -1, -1):
            if self.board[row][col] == 0:
                return row
        return None
    
    def make_move(self, col: int, player: int) -> bool:
        """
        Drop a piece for `player` into column `col`.
    
        - Reject if it's not `player`'s turn
        - Reject if column is invalid or full
        - Place the piece at the lowest empty row
        - Toggle `current_player` only after a legal move
        """
        # Enforce turn
        if player != self.current_player:
            return False
    
        # Enforce legality
        if not self.is_valid_move(col):
            return False
    
        # Find next open row (from bottom)
        for row in range(self.ROWS - 1, -1, -1):
            if self.board[row, col] == 0:
                self.board[row, col] = player
                # Toggle turn
                self.current_player = 2 if self.current_player == 1 else 1
                return True
    
        return False

    
    def check_winner(self) -> Optional[int]:
        """
        Check if there's a winner on the board
        Returns player number (1 or 2) if there's a winner
        Returns None if no winner
        Checks all possible winning combinations:
        - Horizontal
        - Vertical 
        - Both diagonals
        """
        # Check horizontal
        for row in range(self.ROWS):
            for col in range(self.COLS-3):
                if (self.board[row][col] != 0 and 
                    self.board[row][col] == self.board[row][col+1] == 
                    self.board[row][col+2] == self.board[row][col+3]):
                    return self.board[row][col]
        
        # Check vertical
        for row in range(self.ROWS-3):
            for col in range(self.COLS):
                if (self.board[row][col] != 0 and 
                    self.board[row][col] == self.board[row+1][col] == 
                    self.board[row+2][col] == self.board[row+3][col]):
                    return self.board[row][col]
        
        # Check diagonal (positive slope)
        for row in range(self.ROWS-3):
            for col in range(self.COLS-3):
                if (self.board[row][col] != 0 and 
                    self.board[row][col] == self.board[row+1][col+1] == 
                    self.board[row+2][col+2] == self.board[row+3][col+3]):
                    return self.board[row][col]
        
        # Check diagonal (negative slope)
        for row in range(3, self.ROWS):
            for col in range(self.COLS-3):
                if (self.board[row][col] != 0 and 
                    self.board[row][col] == self.board[row-1][col+1] == 
                    self.board[row-2][col+2] == self.board[row-3][col+3]):
                    return self.board[row][col]
        
        return None
    
    def is_board_full(self) -> bool:
        """
        Check if the game board is completely full
        Returns True if no more moves are possible
        """
        return not any(self.board[0][col] == 0 for col in range(self.COLS))
    
    def get_current_player(self) -> int:
        return self.current_player

    def reset(self, starting_player: int = 1) -> None:
        self.board[:, :] = 0
        self.current_player = starting_player
