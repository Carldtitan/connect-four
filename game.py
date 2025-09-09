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
        """
        Check if a move is valid in the given column
        Returns True if the top cell in column is empty
        """
        return self.board[0][col] == 0
    
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
        Attempt to make a move in the specified column
        Returns True if successful, False if invalid
        """
        row = self.get_next_open_row(col)
        if row is not None:
            self.board[row][col] = player
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