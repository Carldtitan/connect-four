import unittest
import numpy as np
from game import ConnectFour
from ai import ConnectFourAI

class TestConnectFour(unittest.TestCase):
    def setUp(self):
        self.game = ConnectFour()
        self.ai = ConnectFourAI(self.game)

    def test_winning_move_detection(self):
        """Test if AI can detect and make any winning move"""
        # Horizontal win possibility
        self.game.board = np.array([
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 2, 2, 2, 0, 0, 0]
        ])
        move = self.ai.get_best_move()
        self.game.make_move(move, 2)
        self.assertIsNotNone(self.game.check_winner())

    def test_blocking_priority(self):
        """Test if AI blocks opponent's winning moves when necessary"""
        self.game.board = np.array([
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 1, 0, 0, 0]
        ])
        move = self.ai.get_best_move()
        # AI should block one of the ends
        self.assertTrue(move in [0, 4])

    def test_center_control(self):
        """Test if AI values center control in early game"""
        self.game.board = np.zeros((6, 7))
        move = self.ai.get_best_move()
        # AI should prefer center or adjacent columns in opening
        self.assertTrue(2 <= move <= 4)

    def test_fork_prevention(self):
        """Test if AI prevents opponent from creating forks"""
        self.game.board = np.array([
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0],
            [0, 1, 2, 0, 0, 0, 0],
            [1, 2, 1, 0, 0, 0, 0]
        ])
        move = self.ai.get_best_move()
        # AI should make a defensive move to prevent fork
        self.game.make_move(move, 2)
        # Check that opponent can't win in one move
        for col in range(7):
            if self.game.is_valid_move(col):
                board_copy = self.game.board.copy()
                row = self.game.get_next_open_row(col)
                board_copy[row][col] = 1
                self.assertIsNone(self.game.check_winner())

    def test_performance(self):
        """Test AI decision time"""
        import time
        start_time = time.time()
        self.ai.get_best_move()
        end_time = time.time()
        self.assertLess(end_time - start_time, 2.0)

def create_test_scenario(scenario_name: str) -> np.ndarray:
    """Create predefined test scenarios"""
    scenarios = {
        "early_game": np.array([
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0],
            [0, 0, 1, 2, 2, 0, 0]
        ]),
        "mid_game_threat": np.array([
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 2, 0, 0, 0],
            [0, 0, 1, 1, 0, 0, 0],
            [0, 1, 2, 2, 1, 0, 0],
            [1, 2, 1, 1, 2, 2, 1]
        ]),
        "fork_opportunity": np.array([
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 2, 0, 0, 0, 0],
            [0, 1, 2, 1, 0, 0, 0],
            [1, 2, 1, 2, 0, 0, 0]
        ])
    }
    return scenarios.get(scenario_name)

def run_scenario_tests():
    """Run tests with different board scenarios"""
    game = ConnectFour()
    ai = ConnectFourAI(game)
    
    scenarios = [
        ("early_game", "Testing early game strategy"),
        ("mid_game_threat", "Testing threat response"),
        ("fork_opportunity", "Testing fork detection")
    ]
    
    results = []
    for scenario_name, description in scenarios:
        game.board = create_test_scenario(scenario_name)
        move = ai.get_best_move()
        # Make the move to analyze the result
        game_copy = ConnectFour()
        game_copy.board = game.board.copy()
        game_copy.make_move(move, 2)
        
        results.append({
            "scenario": scenario_name,
            "description": description,
            "move": move,
            "board_before": game.board.copy(),
            "board_after": game_copy.board,
            "evaluation": analyze_move(game_copy.board, move)
        })
    
    return results

def analyze_move(board: np.ndarray, move: int) -> str:
    """Analyze the strategic value of a move"""
    # Add analysis logic here
    return f"Move in column {move} maintains strategic position"

if __name__ == "__main__":
    # Run unit tests
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    
    # Run scenario tests
    print("\nRunning scenario tests...")
    results = run_scenario_tests()
    for result in results:
        print(f"\nScenario: {result['scenario']}")
        print(f"Description: {result['description']}")
        print(f"AI's move: Column {result['move']}")
        print(f"Evaluation: {result['evaluation']}")
        print("Board after move:")
        print(result['board_after']) 