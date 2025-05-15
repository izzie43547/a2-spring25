#!/usr/bin/env python3
"""
Dr. Mario Game Implementation
Main entry point for the game.
"""

import os
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
                # Ensure the row has the correct number of columns
                if len(row) < cols:
                    row = row.ljust(cols)
                initial_field.append(row[:cols])
        
        # Initialize game state
        game_state = GameState(rows, cols, initial_field)
        
        # Display initial state
        display_field(game_state)
        
        # Display initial state
        display_field(game_state)
        
        # Main game loop
        while True:
            try:
                # Get user input - read directly from sys.stdin to avoid newline issues
                command_str = sys.stdin.readline().strip()
                
                # Check for quit command first - exit without any output
                if command_str.upper() == 'Q':
                    # Exit immediately with no output
                    os._exit(0)
                    
                # Parse the command if not empty
                if command_str:
                    command, args = parse_command(command_str)
                else:
                    command, args = '', []
                    
                # Handle empty command (apply gravity)
                if not command_str.strip():
                    if game_state.faller:
                        game_state.apply_gravity()
                    # Display the field after processing empty line
                    display_field(game_state)
                    continue
                    
                # Handle other commands
                if command == 'F':
                    if not args or len(args) != 2 or not all(c.upper() in 'RBY' for c in args):
                        display_field(game_state)
                        continue
                    if game_state.faller is None:
                        game_state.create_faller(args[0].upper(), args[1].upper())
                        display_field(game_state)
                    else:
                        display_field(game_state)
                else:
                    if game_state.faller:
                        if command in ('A', 'B'):
                            game_state.rotate_faller(command)
                            display_field(game_state)
                        elif command in ('<', '>'):
                            game_state.move_faller(command)
                            display_field(game_state)
                        elif command == 'V' and args and len(args) == 3:
                            try:
                                row = int(args[0])
                                col = int(args[1])
                                color = args[2].lower()
                                if color in ('r', 'b', 'y'):
                                    game_state.add_virus(row, col, color)
                                    display_field(game_state)
                            except (ValueError, IndexError):
                                display_field(game_state)
                
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
    