import tkinter as tk
from tkinter import messagebox
import time
from game import ConnectFour
from ai import ConnectFourAI

class ConnectFourGUI:
    """
    Graphical user interface for Connect Four game
    Uses tkinter for rendering and handling user input
    """
    def __init__(self):
        # Initialize main window
        self.window = tk.Tk()
        self.window.title("Connect Four")
        self.game = ConnectFour()
        self.ai = ConnectFourAI(self.game)
        
        # Add tracking for last move
        self.last_move = None  # Will store (row, col) of last move
        
        # Set up display constants
        self.CELL_SIZE = 60  # Size of each cell in pixels
        self.RADIUS = self.CELL_SIZE // 2 - 5  # Size of game pieces
        
        # Create main game canvas
        self.canvas = tk.Canvas(
            self.window, 
            width=self.game.COLS * self.CELL_SIZE,
            height=self.game.ROWS * self.CELL_SIZE,
            bg='blue'
        )
        self.canvas.pack(pady=20)
        
        # Initialize board and bind events
        self.draw_board()
        self.canvas.bind('<Motion>', self.on_hover)  # Mouse movement
        self.canvas.bind('<Button-1>', self.on_click)  # Mouse click
        
        # Add player selection frame
        self.player_frame = tk.Frame(self.window)
        self.player_frame.pack(pady=10)
        
        # Add radio buttons for player selection
        self.player_choice = tk.StringVar(value="human")
        tk.Radiobutton(
            self.player_frame,
            text="You Start (Red)",
            variable=self.player_choice,
            value="human",
            command=self.confirm_start
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Radiobutton(
            self.player_frame,
            text="AI Starts (Yellow)",
            variable=self.player_choice,
            value="ai",
            command=self.confirm_start
        ).pack(side=tk.LEFT, padx=10)
        
        # Add restart button after player selection
        restart_button = tk.Button(
            self.window, 
            text="Restart Game", 
            command=self.confirm_restart
        )
        restart_button.pack(pady=10)
        
        # Add flag to track if AI is thinking
        self.ai_thinking = False
    
    def draw_board(self):
        """
        Draw the game board and pieces
        Creates circles for each cell and highlights last move
        """
        self.canvas.delete("all")  # Clear the canvas
        for row in range(self.game.ROWS):
            for col in range(self.game.COLS):
                x = col * self.CELL_SIZE + self.CELL_SIZE//2
                y = row * self.CELL_SIZE + self.CELL_SIZE//2
                
                # Determine cell color based on occupant
                color = 'white'  # Empty cell
                if self.game.board[row][col] == 1:
                    color = 'red'  # Human piece
                elif self.game.board[row][col] == 2:
                    color = 'yellow'  # AI piece
                
                # Draw highlight for last move
                if self.last_move and (row, col) == self.last_move:
                    # Draw highlight circle
                    self.canvas.create_oval(
                        x - self.RADIUS - 3,
                        y - self.RADIUS - 3,
                        x + self.RADIUS + 3,
                        y + self.RADIUS + 3,
                        fill='lightblue',
                        outline='blue',
                        width=2
                    )
                
                # Draw the piece
                self.canvas.create_oval(
                    x - self.RADIUS,
                    y - self.RADIUS,
                    x + self.RADIUS,
                    y + self.RADIUS,
                    fill=color,
                    outline='black'
                )
    
    def on_hover(self, event):
        """
        Handle mouse hover events
        Shows preview of where piece will be placed
        Disabled while AI is thinking
        """
        # Don't show hover effect if AI is thinking
        if self.ai_thinking:
            return
            
        col = event.x // self.CELL_SIZE
        self.canvas.delete("hover")
        
        if 0 <= col < self.game.COLS and self.game.is_valid_move(col):
            x = col * self.CELL_SIZE + self.CELL_SIZE//2
            # Always show red hover for human player
            self.canvas.create_oval(
                x - self.RADIUS,
                self.RADIUS,
                x + self.RADIUS,
                self.RADIUS * 3,
                fill='red',
                outline='black',
                tags="hover"
            )
    
    def on_click(self, event):
        """
        Handle mouse click events
        Makes a move in the clicked column if valid
        Prevents moves while AI is thinking
        """
        # Ignore clicks if AI is thinking
        if self.ai_thinking:
            return
            
        col = event.x // self.CELL_SIZE
        if 0 <= col < self.game.COLS and self.game.is_valid_move(col):
            self.make_move(col)
    
    def make_move(self, col):
        """
        Execute a move in the given column
        Updates display and triggers AI response
        """
        # Human is always red (1), AI is always yellow (2)
        if self.player_choice.get() == "human":
            # Human starts - use red (1)
            if self.game.make_move(col, 1):
                self.draw_board()
                self.window.update()
                
                if self.check_game_end():
                    return
                
                # Set thinking flag and disable hover effect
                self.ai_thinking = True
                self.canvas.delete("hover")
                self.window.update()
                
                # Schedule AI move
                self.window.after(100, self.ai_move)
        else:
            # AI starts - human still uses red (1)
            if self.game.make_move(col, 1):
                self.draw_board()
                self.window.update()
                
                if self.check_game_end():
                    return
                
                # Set thinking flag and disable hover effect
                self.ai_thinking = True
                self.canvas.delete("hover")
                self.window.update()
                
                # Schedule AI move
                self.window.after(100, self.ai_move)
    
    def ai_move(self):
        """
        Execute AI's move
        Gets best move from AI and updates display
        """
        try:
            # AI always uses yellow (2)
            col = self.ai.get_best_move()
            if self.game.make_move(col, 2):
                self.draw_board()
                self.check_game_end()
        finally:
            # Always reset thinking flag when AI is done
            self.ai_thinking = False
    
    def check_game_end(self) -> bool:
        """
        Check if game is over
        Shows appropriate message and restarts if game is over
        Returns True if game is over, False otherwise
        """
        winner = self.game.check_winner()
        if winner is not None:
            # Show winner message
            message = "You win!" if winner == 1 else "AI wins!"
            messagebox.showinfo("Game Over", message)
            self.restart_game()
            return True
        elif self.game.is_board_full():
            # Show tie message
            messagebox.showinfo("Game Over", "It's a tie!")
            self.restart_game()
            return True
        return False
    
    def restart_game(self):
        """
        Reset the game to initial state
        """
        self.game = ConnectFour()
        self.ai = ConnectFourAI(self.game)
        self.ai.set_player_number(2)
        self.last_move = None  # Reset last move
        self.draw_board()
        
        if self.player_choice.get() == "ai":
            self.window.after(500, self.ai_move)
    
    def confirm_start(self):
        """
        Show confirmation dialog before starting new game
        """
        player = "You" if self.player_choice.get() == "human" else "AI"
        if messagebox.askyesno("Confirm Start", f"{player} will start the game.\nAre you ready?"):
            self.restart_game()
        else:
            # Reset radio button to previous state if user cancels
            self.player_choice.set("human")
    
    def confirm_restart(self):
        """
        Show confirmation dialog before restarting game
        """
        if messagebox.askyesno("Confirm Restart", "Are you sure you want to restart the game?"):
            self.restart_game()
    
    def run(self):
        """
        Start the game
        Begins tkinter main loop
        """
        self.window.mainloop() 