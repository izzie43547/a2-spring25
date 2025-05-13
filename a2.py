#!/usr/bin/env python3
"""
Dr. Mario Game Implementation
Main entry point for the game.
"""

import sys
from game_logic import GameState
from ui import display_field, handle_command, parse_command

def main() -> None:
    """
    Main entry point for the Dr. Mario game.
    """
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
                # Display current state
                display_field(game_state)
                
                # Get and process user input
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
                        if not args or len(args) != 2 or not all(c.upper() in 'RBY' for c in args):
                            continue
                        if game_state.faller is None:
                            game_state.create_faller(args[0].upper(), args[1].upper())
                    else:
                        if game_state.faller:
                            if command in ('A', 'B'):
                                game_state.rotate_faller(command)
                            elif command in ('<', '>'):
                                game_state.move_faller(command)
                            elif command == 'V' and args and len(args) == 3:
                                try:
                                    row = int(args[0])
                                    col = int(args[1])
                                    color = args[2].lower()
                                    if color in ('r', 'b', 'y'):
                                        game_state.add_virus(row, col, color)
                                except (ValueError, IndexError):
                                    continue
                
            except (EOFError, KeyboardInterrupt):
                return
            except Exception as e:
                # Ignore invalid commands for the validity checker
                continue
                
    except Exception as e:
        # Print error and exit on any other exception
        print(f"Error: {e}", file=sys.stderr)
        return

if __name__ == '__main__':
    main()
    