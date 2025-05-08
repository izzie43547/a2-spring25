# user_interface.py

import shlex
from game_logic import GameState
from typing import List, Tuple, Optional

def display_field(game_state: GameState) -> None:
    """
    Displays the current state of the game field.

    Args:
        game_state (GameState): The current game state.
    """
    rows, cols = game_state.get_dimensions()
    faller_segments = {}
    if game_state.faller:
        for r, c, color in game_state.faller['segments']:
            faller_segments[(r, c)] = color

    for r in range(rows):
        row_str = "|"
        for c in range(cols):
            cell = game_state.field[r][c]
            if (r, c) in faller_segments:
                color = faller_segments[(r, c)]
                if game_state.faller['orientation'] == 'horizontal':
                    left_c = min(fc for _, fc, _ in game_state.faller['segments'])
                    if c == left_c:
                        row_str += f"[{color}-"
                    else:
                        row_str += f"-{color}]"
                else:
                    row_str += f"[{color}]"
            elif cell == ' ':
                row_str += "   "
            elif len(cell) == 1 and cell.isupper():
                row_str += f" {cell} "
            elif cell.startswith('L') and len(cell) == 2:
                row_str += f"|{cell[1]}-"
            elif cell.startswith('R') and len(cell) == 2:
                row_str += f"-{cell[1]}|"
            elif len(cell) == 1 and cell.islower():
                row_str += f" {cell} "
            elif len(cell) == 3 and cell.startswith('*') and cell.endswith('*'):
                row_str += f"*{cell[1]}*"
            elif len(cell) == 2 and cell[0] in ('L', 'R') and cell[1].isupper():
                row_str += f"{cell[0]}{cell[1]}{cell[0]}" if cell[0] == '|' else f"{cell[0]}{cell[1]}{cell[0]}"
            elif len(cell) == 1 and cell.isupper():
                row_str += f"|{cell}|"
            else:
                row_str += "   "
        row_str += "|"
        print(row_str)
    print("-" * (3 * cols) + " ")
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
        return False
        
    if command == 'Q':
        return False
    elif command == 'F':
        if args and len(args) == 2 and all(c in 'RBY' for c in args):
            game_state.create_faller(args[0], args[1])
        else:
            print("Invalid F command format. Use 'F <color1> <color2>'.")
    elif command == 'A':
        game_state.rotate_faller('A')
    elif command == 'B':
        game_state.rotate_faller('B')
    elif command == '<':
        game_state.move_faller('<')
    elif command == '>':
        game_state.move_faller('>')
    elif command == 'V':
        if args and len(args) == 3:
            try:
                row = int(args[0])
                col = int(args[1])
                color = args[2].lower()  # Convert to lowercase for validation
                if color in 'rby':
                    game_state.add_virus(row, col, color)
                else:
                    print("Invalid virus color. Use 'r', 'R', 'b', 'B', 'y', or 'Y'.")
            except ValueError:
                print("Invalid V command arguments. Use 'V <row> <col> <color>'.")
        else:
            print("Invalid V command format. Use 'V <row> <col> <color>'.")
    elif command == '':
        game_state.apply_gravity()
    else:
        print(f"Unknown command: {command}")
    return True

def run_game() -> None:
    """
    Runs the Dr. Mario game.
    """
    rows = int(input())
    cols = int(input())
    initial_config_type = input().upper()

    initial_field = None
    if initial_config_type == 'CONTENTS':
        initial_field = [input() for _ in range(rows)]
    elif initial_config_type == 'EMPTY':
        pass
    else:
        print("Invalid initial configuration type.")
        return

    game_state = GameState(rows, cols, initial_field)

    while not game_state.game_over:
        display_field(game_state)
        command_str = get_user_command()
        command, args = parse_command(command_str)
        if not handle_command(game_state, command, args):
            break

    if game_state.game_over:
        print("GAME OVER")

if __name__ == '__main__':
    run_game()
    