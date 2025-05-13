"""User interface module for Dr. Mario game.

This module handles the display and input/output operations for the game.
"""

import shlex
from typing import List, Optional, Tuple

from game_logic import GameState


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
            elif (isinstance(cell, str) and len(cell) == 2
                    and cell[0] in 'LR'):
                if cell[0] == 'L':
                    row_str += f"|{cell[1]}"
                    if (c + 1 < cols and
                            isinstance(game_state.field[r][c+1], str) and
                            len(game_state.field[r][c+1]) == 2 and
                            game_state.field[r][c+1][0] == 'R'):
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

    # Print bottom border
    print("-" * (cols * 3 + 1))
    print(" " + "-" * (cols * 3) + " ")
    
    # Check for level cleared
    if not game_state.has_viruses():
        print("LEVEL CLEARED")


def get_user_command() -> str:
    """Get a command from the user.

    Returns:
        str: The user's command.
    """
    return input("> ").strip()


def parse_command(command: str) -> Tuple[str, Optional[List[str]]]:
    """Parse the user command.

    Args:
        command: The raw command string.

    Returns:
        A tuple containing the command and its arguments.
    """
    if not command.strip():
        return '', None

    parts = shlex.split(command.strip())
    if not parts:
        return '', None

    cmd = parts[0].upper()
    args = parts[1:] if len(parts) > 1 else None
    return cmd, args


def show_help() -> None:
    """Display help information about available commands.
    
    Shows all available commands and their usage.
    """
    print("Available commands:")
    print("  F <color1> <color2> - Create a new faller")
    print("  < or > - Move faller left or right")
    print("  A or B - Rotate faller")
    print("  V <row> <col> <color> - Add a virus")
    print("  Q - Quit the game")
    print("  ? - Show this help")
    print()
    input("Press Enter to start...")


def handle_command(
    game_state: GameState,
    command: str,
    args: Optional[List[str]]
) -> bool:
    """Handle user command and update the game state.

    Args:
        game_state (GameState): The current game state.
        command (str): The command to execute.
        args (Optional[List[str]]): The arguments for the command.

    Returns:
        bool: True if the game should continue, False if it should end.
    """
    if not command:
        # Apply gravity for empty command
        if game_state.faller:
            game_state.apply_gravity()
        return True

    if command == 'Q':
        return False

    if command == 'H':
        show_help()
        return True

    if command == 'F':
        if (not args or len(args) != 2 or 
                not all(c.upper() in 'RBY' for c in args)):
            print("Invalid arguments. Usage: F <color1> <color2> "
                  "(colors: R, B, Y)")
            return True

        if game_state.faller is None:
            game_state.create_faller(args[0].upper(), args[1].upper())
        else:
            print("A faller is already active!")
        return True

    if command in ('<', '>'):
        if game_state.faller:
            game_state.move_faller(command)
        else:
            print("No active faller!")
        return True

    if command in ('A', 'B'):
        if game_state.faller:
            game_state.rotate_faller(command)
        else:
            print("No active faller!")
        return True

    if command == 'V':
        if not args or len(args) != 3:
            print("Invalid arguments. Usage: V <row> <col> <color>")
            return True

        try:
            row = int(args[0])
            col = int(args[1])
            color = args[2].lower()
            if color not in ('r', 'b', 'y'):
                raise ValueError("Color must be R, B, or Y")

            game_state.add_virus(row, col, color)
        except (ValueError, IndexError) as e:
            print(f"Error: {e}")
        return True

    print(f"Unknown command: {command}. Type 'H' for help.")
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
    """Run the Dr. Mario game with the expected test output format."""
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
                # Preserve the original case of the input
                initial_field.append(row if row.strip() else ' ' * cols)

        # Initialize game state
        game_state = GameState(rows, cols, initial_field)

        # Display initial state
        display_field(game_state)

        # Main game loop
        while True:
            try:
                # Get user input
                command_str = input()
                command, args = parse_command(command_str)

                # Handle quit command
                if command == 'Q':
                    return

                # Handle empty command (apply gravity)
                if not command_str.strip():
                    if game_state.faller:
                        game_state.apply_gravity()
                else:
                    # Handle other commands
                    if command == 'F':
                        if (not args or len(args) != 2 or 
                                not all(c.upper() in 'RBY' for c in args)):
                            continue
                        if game_state.faller is None:
                            game_state.create_faller(
                                args[0].upper(), 
                                args[1].upper()
                            )
                    elif game_state.faller:
                        if command in ('A', 'B'):
                            game_state.rotate_faller(command)
                        elif command in ('<', '>'):
                            game_state.move_faller(command)
                        elif (command == 'V' and args and 
                              len(args) == 3):
                            try:
                                row = int(args[0])
                                col = int(args[1])
                                color = args[2].lower()
                                if color in ('r', 'b', 'y'):
                                    game_state.add_virus(row, col, color)
                            except (ValueError, IndexError):
                                continue

                # Display the updated state
                display_field(game_state)

            except (EOFError, KeyboardInterrupt):
                return
            except Exception:
                # Ignore invalid commands for the validity checker
                continue

    except Exception as e:
        # Print error and exit on any other exception
        print(f"Error: {e}", file=sys.stderr)
        run_game()

# Export required functions for a2.py
__all__ = ['display_field', 'handle_command', 'parse_command']


if __name__ == '__main__':
    run_game()