# user_interface.py

import shlex
from game_logic import GameState
from typing import List, Tuple, Optional

def display_field(game_state: GameState) -> None:
    """
    Displays the current state of the game field in the expected format.

    Args:
        game_state (GameState): The current game state.
    """
    rows, cols = game_state.get_dimensions()
    
    # Print top border with proper spacing
    print("|" + " " * (cols * 3 - 1) + "|")
    
    for r in range(rows):
        row_str = "|"
        for c in range(cols):
            cell = game_state.field[r][c]
            
            # Handle empty cell
            if cell == ' ':
                row_str += "   "
            # Handle marked cells (for removal)
            elif isinstance(cell, str) and cell.startswith('*'):
                row_str += f"*{cell[1]}*"
            # Handle horizontal pieces
            elif isinstance(cell, str) and len(cell) == 2 and cell[0] in 'LR':
                if cell[0] == 'L':
                    row_str += f"|{cell[1]}"
                    if c + 1 < cols and isinstance(game_state.field[r][c+1], str) and len(game_state.field[r][c+1]) == 2 and game_state.field[r][c+1][0] == 'R':
                        row_str += f"{game_state.field[r][c+1][1]}|"
                    else:
                        row_str += " |"
                    c += 1  # Skip the next cell
                else:
                    row_str += f"{cell[1]}|"
            # Handle single character cells (viruses or colors)
            else:
                if isinstance(cell, str) and cell.islower():  # Virus
                    row_str += f" {cell} "
                else:  # Regular color block
                    row_str += f" {cell} "
        
        # Ensure the row has the correct width and ends with a |
        while len(row_str) < cols * 3 + 1:
            row_str += " "
        if not row_str.endswith('|'):
            row_str = row_str.rstrip() + "|"
        print(row_str)
    
    # Print bottom border with proper spacing
    print(" " + "-" * (cols * 3) + " ")
    
    # Check for level cleared
    if not game_state.has_viruses():
        print("LEVEL CLEARED")

def get_user_command() -> str:
    """
    Gets a command from the user.

    Returns:
        str: The user's command.
    """
    return input()

def parse_command(command: str) -> Tuple[str, Optional[List[str]]]:
    """
    Parses the user command.

    Args:
        command (str): The raw command string.

    Returns:
        Tuple[str, Optional[List[str]]]: The command and its arguments (if any).
    """
    try:
        parts = shlex.split(command)
        if not parts:
            return "", None
        return parts[0].upper(), parts[1:] if len(parts) > 1 else None
    except ValueError:
        print("Invalid command format. Use proper spacing between arguments.")
        return "", None

def show_help() -> None:
    """Displays help information about available commands."""
    print("\n=== DR. MARIO COMMANDS ===")
    print("F <color1> <color2> - Create a new faller with two colored segments")
    print("                       Colors must be R (red), B (blue), or Y (yellow)")
    print("< or >              - Move faller left or right")
    print("A or B              - Rotate faller left (A) or right (B)")
    print("V <row> <col> <color> - Add a virus at specified position")
    print("                       Row and column are 0-based indices")
    print("<enter>             - Apply gravity (make pieces fall)")
    print("Q                   - Quit the game")
    print("H                   - Show this help")
    print("=======================\n")
    input("Press Enter to continue...")

def handle_command(game_state: GameState, command: str, args: Optional[List[str]]) -> bool:
    """
    Handles the user command and updates the game state.

    Args:
        game_state (GameState): The current game state.
        command (str): The command to execute.
        args (Optional[List[str]]): The arguments for the command.

    Returns:
        bool: True if the game should continue, False if it should end.
    """
    if game_state.game_over:
        print("GAME OVER - No more moves possible!")
        return False
        
    try:
        if command == 'Q':
            print("Thanks for playing!")
            return False
            
        elif command == 'H':
            show_help()
            return True
            
        elif command == 'F':
            if not args or len(args) != 2 or not all(c.upper() in 'RBY' for c in args):
                raise ValueError("Invalid F command. Use 'F <color1> <color2>' where colors are R, B, or Y.")
            if game_state.faller is not None:
                raise ValueError("A faller already exists. Move or rotate it first.")
            if not game_state.create_faller(args[0].upper(), args[1].upper()):
                game_state.game_over = True
                print("Game Over - No space for new faller!")
                return False
                
        elif command in ('A', 'B'):
            if game_state.faller is None:
                raise ValueError("No active faller. Create one with 'F <color1> <color2>'")
            game_state.rotate_faller(command)
            
        elif command in ('<', '>'):
            if game_state.faller is None:
                raise ValueError("No active faller. Create one with 'F <color1> <color2>'")
            game_state.move_faller(command)
            
        elif command == 'V':
            if not args or len(args) != 3:
                raise ValueError("Invalid V command. Use 'V <row> <col> <color>'")
            try:
                row = int(args[0])
                col = int(args[1])
                color = args[2].lower()
                if color[0] not in 'rby':
                    raise ValueError("Color must be r, b, or y")
                game_state.add_virus(row, col, color)
            except ValueError as e:
                raise ValueError(f"Invalid virus placement: {e}")
                
        elif command == '':
            game_state.apply_gravity()
            
        else:
            print(f"Unknown command: {command}")
            print("Type 'H' for help with commands.")
            
    except Exception as e:
        print(f"Error: {e}")
        print("Type 'H' for help with commands.")
        input("Press Enter to continue...")
        
    return True

def show_welcome() -> None:
    """Displays the welcome message and game instructions."""
    print("=" * 50)
    print("DR. MARIO".center(50))
    print("=" * 50)
    print("\nWelcome to Dr. Mario!")
    print("\nGAME OBJECTIVE:")
    print("  - Clear all viruses by matching 4 or more of the same color")
    print("  - Create matches horizontally, vertically, or diagonally")
    print("  - Use the controls to move and rotate falling capsules")
    print("\nType 'H' during the game for help with commands.")
    print("-" * 50)

def run_game() -> None:
    """
    Runs the Dr. Mario game with the expected test output format.
    """
    # Read game configuration from input
    try:
        # Read rows and columns
        rows = int(input())
        cols = int(input())
        
        # Read initial configuration type
        config = input().strip().upper()
        
        initial_field = None
        if config == 'CONTENTS':
            initial_field = []
            for _ in range(rows):
                row = input().strip()
                initial_field.append(row.upper() if row.strip() else ' ' * cols)
        
        # Initialize game state
        game_state = GameState(rows, cols, initial_field)
        
        # Main game loop
        while True:
            # Display current game state
            display_field(game_state)
            
            # Check for win/lose conditions
            if game_state.game_over or not game_state.has_viruses():
                break
                
            # Get and process user input
            command_str = get_user_command()
            command, args = parse_command(command_str)
            
            # Handle quit command
            if command == 'Q' or not handle_command(game_state, command, args):
                break
                
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        return
    except Exception as e:
        # Print error and exit on any other exception
        print(f"Error: {e}", file=sys.stderr)
        run_game()

# Export required functions for a2.py
__all__ = ['display_field', 'handle_command', 'parse_command']

if __name__ == '__main__':
    run_game()