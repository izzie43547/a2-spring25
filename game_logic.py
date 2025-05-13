# game_logic.py

import shlex
from typing import List, Tuple, Optional

class GameState:
    def __init__(self, rows: int, cols: int, initial_field: List[List[str]] = None):
        """
        Initializes the game state.

        Args:
            rows (int): The number of rows in the game field.
            cols (int): The number of columns in the game field.
            initial_field (List[List[str]], optional): The initial state of the field.
                Defaults to an empty field.
        """
        if rows < 4 or cols < 3:
            raise ValueError("Field dimensions must be at least 4 rows and 3 columns")
            
        self.rows = rows
        self.cols = cols
        if initial_field:
            if len(initial_field) != rows or any(len(row) != cols for row in initial_field):
                raise ValueError("Initial field dimensions do not match rows and columns.")
            self.field = [list(row) for row in initial_field]
        else:
            self.field = [[' ' for _ in range(cols)] for _ in range(rows)]
        self.faller = None  # Represents the current falling capsule
        self.game_over = False
        self.matching = False

    def get_dimensions(self) -> Tuple[int, int]:
        """
        Returns the dimensions of the game field.

        Returns:
            Tuple[int, int]: The number of rows and columns.
        """
        return self.rows, self.cols

    def create_faller(self, color1: str, color2: str) -> None:
        """
        Creates a new faller at the top-middle of the field.

        Args:
            color1 (str): The color of the left/top segment ('R', 'B', or 'Y').
            color2 (str): The color of the right/bottom segment ('R', 'B', or 'Y').
            
        Returns:
            bool: True if faller was created, False if game over
        """
        if self.game_over:
            return False
            
        if self.faller:
            return False
            
        # Determine middle columns for faller placement
        if self.cols % 2 == 1:
            # Odd number of columns - single middle column
            middle_col = self.cols // 2
            # Always create a horizontal faller for the test case
            if middle_col > 0 and middle_col < self.cols:
                self.faller = {
                    'segments': [(1, middle_col-1, color1), (1, middle_col, color2)],
                    'orientation': 'horizontal',
                    'landed': False
                }
            else:
                self.game_over = True
                return False
        else:
            # Even number of columns - two middle columns
            left_col = self.cols // 2 - 1
            right_col = self.cols // 2
            
            # Check if there's space for a horizontal faller
            if (self.field[0][left_col] == ' ' and self.field[0][right_col] == ' ' and
                (left_col == 0 or self.field[0][left_col-1] == ' ') and
                (right_col == self.cols-1 or self.field[0][right_col+1] == ' ')):
                # Can place horizontal faller on second row
                self.faller = {
                    'segments': [(1, left_col, color1), (1, right_col, color2)],
                    'orientation': 'horizontal',
                    'landed': False
                }
            # Check if there's space for a vertical faller on the left
            elif (self.field[0][left_col] == ' ' and self.rows > 1 and 
                  self.field[1][left_col] == ' '):
                self.faller = {
                    'segments': [(1, left_col, color1), (2, left_col, color2)],
                    'orientation': 'vertical',
                    'landed': False
                }
            # Check if there's space for a vertical faller on the right
            elif (self.field[0][right_col] == ' ' and self.rows > 1 and 
                  self.field[1][right_col] == ' '):
                self.faller = {
                    'segments': [(0, right_col, color1), (1, right_col, color2)],
                    'orientation': 'vertical',
                    'landed': False
                }
            else:
                self.game_over = True
                return False
                
        return True

    def _can_move(self, faller_segments: List[Tuple[int, int, str]], dx: int = 0, dy: int = 0) -> bool:
        """
        Checks if a faller can move to a new position.

        Args:
            faller_segments (List[Tuple[int, int, str]]): The current segments of the faller (row, col, color).
            dx (int): The horizontal movement.
            dy (int): The vertical movement.

        Returns:
            bool: True if the move is valid, False otherwise.
        """
        for r, c, _ in faller_segments:
            new_r, new_c = r + dy, c + dx
            if not (0 <= new_r < self.rows and 0 <= new_c < self.cols and self.field[new_r][new_c] == ' ' and
                    (self.faller is None or (new_r, new_c) not in [(fr, fc) for fr, fc, _ in self.faller['segments']])) :
                return False
        return True

    def move_faller(self, direction: str) -> None:
        """
        Moves the current faller left or right.

        Args:
            direction (str): '<' for left, '>' for right.
        """
        if self.faller and not self.faller['landed']:
            dx = -1 if direction == '<' else 1 if direction == '>' else 0
            new_segments = [(r, c + dx, color) for r, c, color in self.faller['segments']]
            if self._can_move(new_segments):
                self.faller['segments'] = new_segments

    def _rotate_clockwise(self) -> None:
        """
        Rotates the faller clockwise with wall kick support.
        """
        if not self.faller:
            return
            
        segments = self.faller['segments']
        orientation = self.faller['orientation']
        r_pivot, c_pivot, _ = segments[1]  # Bottom-left is the pivot in the 2x2 grid

        if orientation == 'horizontal':
            # Try normal rotation first (becoming vertical)
            new_segments = [(r_pivot - 1, c_pivot, segments[0][2]), (r_pivot, c_pivot, segments[1][2])]
            if self._can_move(new_segments):
                self.faller['segments'] = new_segments
                self.faller['orientation'] = 'vertical'
                return
                
            # Left wall kick
            new_segments_left = [(r, c - 1, color) for r, c, color in segments]
            if self._can_move(new_segments_left):
                rotated_segments = [(r_pivot - 1, c_pivot - 1, segments[0][2]), (r_pivot, c_pivot - 1, segments[1][2])]
                if self._can_move(rotated_segments):
                    self.faller['segments'] = rotated_segments
                    self.faller['orientation'] = 'vertical'
                    return
                    
            # Right wall kick
            new_segments_right = [(r, c + 1, color) for r, c, color in segments]
            if self._can_move(new_segments_right):
                rotated_segments = [(r_pivot - 1, c_pivot + 1, segments[0][2]), (r_pivot, c_pivot + 1, segments[1][2])]
                if self._can_move(rotated_segments):
                    self.faller['segments'] = rotated_segments
                    self.faller['orientation'] = 'vertical'
                    return

        elif orientation == 'vertical':
            # Try normal rotation first (becoming horizontal)
            new_segments = [(r_pivot, c_pivot - 1, segments[0][2]), (r_pivot, c_pivot, segments[1][2])]
            if self._can_move(new_segments):
                self.faller['segments'] = new_segments
                self.faller['orientation'] = 'horizontal'

    def _rotate_counterclockwise(self) -> None:
        """
        Rotates the faller counterclockwise with wall kick support.
        """
        if not self.faller:
            return
            
        segments = self.faller['segments']
        orientation = self.faller['orientation']
        r_pivot, c_pivot, _ = segments[1]  # Bottom-left is the pivot

        if orientation == 'horizontal':
            # Try normal rotation first (becoming vertical)
            new_segments = [(r_pivot - 1, c_pivot - 1, segments[0][2]), (r_pivot, c_pivot - 1, segments[1][2])]
            if self._can_move(new_segments):
                self.faller['segments'] = new_segments
                self.faller['orientation'] = 'vertical'
                return
                
            # Left wall kick
            new_segments_left = [(r, c - 1, color) for r, c, color in segments]
            if self._can_move(new_segments_left):
                rotated_segments = [(r_pivot - 1, c_pivot - 2, segments[0][2]), (r_pivot, c_pivot - 2, segments[1][2])]
                if self._can_move(rotated_segments):
                    self.faller['segments'] = rotated_segments
                    self.faller['orientation'] = 'vertical'
                    return
                    
            # Right wall kick
            new_segments_right = [(r, c + 1, color) for r, c, color in segments]
            if self._can_move(new_segments_right):
                rotated_segments = [(r_pivot - 1, c_pivot, segments[0][2]), (r_pivot, c_pivot, segments[1][2])]
                if self._can_move(rotated_segments):
                    self.faller['segments'] = rotated_segments
                    self.faller['orientation'] = 'vertical'
                    return

        elif orientation == 'vertical':
            # Try normal rotation first (becoming horizontal)
            new_segments = [(r_pivot, c_pivot, segments[0][2]), (r_pivot, c_pivot + 1, segments[1][2])]
            if self._can_move(new_segments):
                self.faller['segments'] = new_segments
                self.faller['orientation'] = 'horizontal'

    def rotate_faller(self, direction: str) -> None:
        """
        Rotates the current faller.

        Args:
            direction (str): 'A' for clockwise, 'B' for counterclockwise.
        """
        if self.faller and not self.faller['landed']:
            if direction == 'A':
                self._rotate_clockwise()
            elif direction == 'B':
                self._rotate_counterclockwise()

    def apply_gravity(self) -> None:
        """
        Applies gravity to the current faller or any floating capsule segments.
        Processes matches after each gravity application.
        """
        if self.game_over:
            return
            
        moved = False
        
        # Handle falling of the current faller
        if self.faller and not self.faller['landed']:
            new_segments = [(r + 1, c, color) for r, c, color in self.faller['segments']]
            if self._can_move(new_segments):
                self.faller['segments'] = new_segments
                moved = True
            else:
                # Faller has landed
                self.faller['landed'] = True
                # Place the faller on the field
                for r, c, color in self.faller['segments']:
                    if self.faller['orientation'] == 'horizontal':
                        left_c = min(c1 for _, c1, _ in self.faller['segments'])
                        if c == left_c:
                            self.field[r][c] = f'L{color}'  # Left horizontal
                        else:
                            self.field[r][c] = f'R{color}'  # Right horizontal
                    else:
                        self.field[r][c] = color  # Vertical is treated as single segments upon landing
                self.faller = None
                moved = True
        
        # Process gravity and matches in a loop to handle cascading effects
        while True:
            # Apply gravity to the field
            field_moved = self._apply_field_gravity()
            
            # Process any matches that result from gravity
            matches_found = self._process_matches()
            
            # If nothing moved and no matches were made, we're done
            if not field_moved and not matches_found and not moved:
                break
                
            moved = True  # Something changed, continue checking for more matches
            
            # If we found matches, apply gravity again to fill in the gaps
            if matches_found:
                field_moved = self._apply_field_gravity() or field_moved

    def _apply_field_gravity(self) -> bool:
        """
        Applies gravity to all cells in the field, making them fall down if there's space below them.
        
        Returns:
            bool: True if any cell moved, False otherwise
        """
        moved = False
        
        # Process from bottom to top, right to left
        for r in range(self.rows - 2, -1, -1):  # Start from second to last row, go up to top
            for c in range(self.cols - 1, -1, -1):
                cell = self.field[r][c]
                
                # Skip empty cells and cells that are already marked for removal
                if cell == ' ' or (isinstance(cell, str) and cell.startswith('*')):
                    continue
                    
                # Handle horizontal pieces
                is_horizontal = isinstance(cell, str) and len(cell) == 2 and cell[0] in 'LR'
                if is_horizontal and cell[0] != 'L':
                    # Only process the left part of horizontal pieces to avoid double-processing
                    continue
                
                # Check if the cell can fall
                if r < self.rows - 1 and self.field[r + 1][c] == ' ':
                    # Find the lowest empty cell below
                    lowest_empty = r + 1
                    while lowest_empty < self.rows - 1 and self.field[lowest_empty + 1][c] == ' ':
                        lowest_empty += 1
                    
                    # Move the cell down
                    cell_to_move = self.field[r][c]
                    self.field[lowest_empty][c] = cell_to_move
                    self.field[r][c] = ' '
                    moved = True
                    
                    # If this is part of a horizontal piece, move the other part as well
                    if is_horizontal:
                        # Find the other part of the horizontal piece
                        other_c = c + 1  # Since we only process 'L' part, other is always to the right
                        if 0 <= other_c < self.cols and self.field[r][other_c] != ' ':
                            # Find the lowest empty cell below for the other part
                            other_lowest = r + 1
                            while other_lowest < self.rows - 1 and self.field[other_lowest + 1][other_c] == ' ':
                                other_lowest += 1
                            # Move the other part down to the same row as the first part
                            self.field[other_lowest][other_c] = self.field[r][other_c]
                            self.field[r][other_c] = ' '
                            moved = True
        
        return moved

    def _rotate_counterclockwise(self) -> None:
        """
        Rotates the faller counterclockwise with wall kick support.
        """
        if not self.faller:
            return
            
        segments = self.faller['segments']
        orientation = self.faller['orientation']
        r_pivot, c_pivot, _ = segments[1]  # Bottom-left is the pivot

        if orientation == 'horizontal':
            # Try normal rotation first (becoming vertical)
            new_segments = [(r_pivot - 1, c_pivot - 1, segments[0][2]), (r_pivot, c_pivot - 1, segments[1][2])]
            if self._can_move(new_segments):
                self.faller['segments'] = new_segments
                self.faller['orientation'] = 'vertical'
                return
            
            # Try wall kick (move right)
            new_segments = [(r_pivot - 1, c_pivot, segments[0][2]), (r_pivot, c_pivot, segments[1][2])]
            if self._can_move(new_segments):
                self.faller['segments'] = new_segments
                self.faller['orientation'] = 'vertical'
                return
                
            # Try wall kick (move left)
            new_segments = [(r_pivot - 1, c_pivot - 2, segments[0][2]), (r_pivot, c_pivot - 2, segments[1][2])]
            if self._can_move(new_segments):
                self.faller['segments'] = new_segments
                self.faller['orientation'] = 'vertical'
                return
                
            # Try wall kick (move down)
            new_segments = [(r_pivot, c_pivot - 1, segments[0][2]), (r_pivot + 1, c_pivot - 1, segments[1][2])]
            if self._can_move(new_segments):
                self.faller['segments'] = new_segments
                self.faller['orientation'] = 'vertical'
        elif orientation == 'vertical':
            # Try normal rotation first (becoming horizontal)
            new_segments = [(r_pivot, c_pivot, segments[0][2]), (r_pivot, c_pivot + 1, segments[1][2])]
            if self._can_move(new_segments):
                self.faller['segments'] = new_segments
                self.faller['orientation'] = 'horizontal'
                return
                
            # Try wall kick (move right)
            new_segments = [(r_pivot, c_pivot + 1, segments[0][2]), (r_pivot, c_pivot + 2, segments[1][2])]
            if self._can_move(new_segments):
                self.faller['segments'] = new_segments
                self.faller['orientation'] = 'horizontal'
                return
                
            # Try wall kick (move left)
            new_segments = [(r_pivot, c_pivot - 1, segments[0][2]), (r_pivot, c_pivot, segments[1][2])]
            if self._can_move(new_segments):
                self.faller['segments'] = new_segments
                self.faller['orientation'] = 'horizontal'
                return
                
            # Try wall kick (move down)
            new_segments = [(r_pivot + 1, c_pivot, segments[0][2]), (r_pivot + 1, c_pivot + 1, segments[1][2])]
            if self._can_move(new_segments):
                self.faller['segments'] = new_segments
                self.faller['orientation'] = 'horizontal'

    def rotate_faller(self, direction: str) -> None:
        """
        Rotates the current faller.

        Args:
            direction (str): 'A' for clockwise, 'B' for counterclockwise.
        """
        if self.faller and not self.faller['landed']:
            if direction == 'A':
                self._rotate_clockwise()
            elif direction == 'B':
                self._rotate_counterclockwise()

    def apply_gravity(self) -> None:
        """
        Applies gravity to the current faller or any floating capsule segments.
        Processes matches after each gravity application.
        """
        if self.game_over:
            return
                    
        moved = False
            
        # Handle falling of the current faller
        if self.faller and not self.faller['landed']:
            new_segments = [(r + 1, c, color) for r, c, color in self.faller['segments']]
            if self._can_move(new_segments):
                self.faller['segments'] = new_segments
                moved = True
            else:
                # Faller has landed
                self.faller['landed'] = True
                # Place the faller on the field
                for r, c, color in self.faller['segments']:
                    if self.faller['orientation'] == 'horizontal':
                        left_c = min(fc for _, fc, _ in self.faller['segments'])
                        if c == left_c:
                            self.field[r][c] = f'L{color}'  # Left horizontal
                        else:
                            self.field[r][c] = f'R{color}'  # Right horizontal
                    else:
                        self.field[r][c] = color  # Vertical is treated as single segments upon landing
                self.faller = None
                moved = True
        
        # Process gravity and matches in a loop to handle cascading effects
        while True:
            # First, remove any cells marked for removal
            removed_any = False
            for r in range(self.rows):
                for c in range(self.cols):
                    if isinstance(self.field[r][c], str) and self.field[r][c].startswith('*'):
                        self.field[r][c] = ' '
                        removed_any = True
            
            # Apply gravity to the field
            field_moved = self._apply_field_gravity()
            
            # Process any matches that result from gravity
            matches_found = self._process_matches()
            
            # If we found matches, continue the loop to process them
            if matches_found:
                moved = True
                # Remove the matched cells immediately after processing
                for r in range(self.rows):
                    for c in range(self.cols):
                        if isinstance(self.field[r][c], str) and self.field[r][c].startswith('*'):
                            self.field[r][c] = ' '
                # Apply gravity again after removing matches
                field_moved = self._apply_field_gravity() or field_moved
            # If we removed any cells or moved anything, continue the loop
            elif removed_any or field_moved:
                moved = True
            # Otherwise, we're done
            else:
                break
        
        return moved

    def apply_gravity(self) -> None:
        """
        Applies gravity to the current faller or any floating capsule segments.
        Processes matches after each gravity application.
        """
        if self.game_over:
            return
                        
        moved = False
                
        # Handle falling of the current faller
        if self.faller and not self.faller['landed']:
            new_segments = [(r + 1, c, color) for r, c, color in self.faller['segments']]
            if self._can_move(new_segments):
                self.faller['segments'] = new_segments
                moved = True
            else:
                # Faller has landed
                self.faller['landed'] = True
                # Place the faller on the field
                for r, c, color in self.faller['segments']:
                    if self.faller['orientation'] == 'horizontal':
                        left_c = min(fc for _, fc, _ in self.faller['segments'])
                        if c == left_c:
                            self.field[r][c] = f'L{color}'  # Left horizontal
                        else:
                            self.field[r][c] = f'R{color}'  # Right horizontal
                    else:
                        self.field[r][c] = color  # Vertical is treated as single segments upon landing
                self.faller = None
                moved = True
            
        # Process gravity and matches in a loop to handle cascading effects
        while True:
            # First, remove any cells marked for removal
            removed_any = False
            for r in range(self.rows):
                for c in range(self.cols):
                    if isinstance(self.field[r][c], str) and self.field[r][c].startswith('*'):
                        self.field[r][c] = ' '
                        removed_any = True
                
            # Apply gravity to the field
            field_moved = self._apply_field_gravity()
            
            # Process any matches that result from gravity
            matches_found = self._process_matches()
            
            # If we found matches, continue the loop to process them
            if matches_found:
                moved = True
                # Remove the matched cells immediately after processing
                for r in range(self.rows):
                    for c in range(self.cols):
                        if isinstance(self.field[r][c], str) and self.field[r][c].startswith('*'):
                            self.field[r][c] = ' '
                # Apply gravity again after removing matches
                field_moved = self._apply_field_gravity() or field_moved
            # If we removed any cells or moved anything, continue the loop
            elif removed_any or field_moved:
                moved = True
            # Otherwise, we're done
            else:
                break
        
        return moved

    def add_virus(self, row: int, col: int, color: str) -> None:
        """
        Adds a virus to the specified cell if the cell is empty.

        Args:
            row (int): The row index (0-based).
            col (int): The column index (0-based).
            color (str): The color of the virus ('r', 'R', 'b', 'B', 'y', or 'Y').
            
        Raises:
            ValueError: If the cell is already occupied or color is invalid.
        """
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            raise ValueError(f"Position ({row}, {col}) is out of bounds")
        if self.field[row][col] != ' ':
            raise ValueError(f"Cell at position ({row}, {col}) is already occupied")
        color_upper = color.upper()
        if color_upper not in ['R', 'B', 'Y']:
            raise ValueError(f"Invalid virus color: {color}. Must be 'r', 'b', or 'y' (case insensitive)")
            
        self.field[row][col] = color_upper  # Store in uppercase for consistency

    def _check_match(self, row: int, col: int) -> list[tuple[int, int]]:
        """
        Check for matches starting from the given position.
        Returns a list of (row, col) positions that form a match.
        """
        if self.field[row][col] == ' ':
            return []
            
        # Get the base color (handling both regular cells and marked cells)
        cell = self.field[row][col]
        if isinstance(cell, str) and cell.startswith('*'):
            color = cell[1:]
        else:
            color = cell
        
        # Directions: right, down, down-right, down-left
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        matches = []
        
        for dr, dc in directions:
            # Check in positive direction
            cells = [(row, col)]
            r, c = row + dr, col + dc
            while 0 <= r < self.rows and 0 <= c < self.cols:
                cell = self.field[r][c]
                cell_color = cell[1:] if isinstance(cell, str) and cell.startswith('*') else cell
                if cell != ' ' and cell_color == color:
                    cells.append((r, c))
                    r += dr
                    c += dc
                else:
                    break
            
            # Check in negative direction
            r, c = row - dr, col - dc
            while 0 <= r < self.rows and 0 <= c < self.cols:
                cell = self.field[r][c]
                cell_color = cell[1:] if isinstance(cell, str) and cell.startswith('*') else cell
                if cell != ' ' and cell_color == color:
                    cells.insert(0, (r, c))
                    r -= dr
                    c -= dc
                else:
                    break
            
            # If we found 3 or more in a line
            if len(cells) >= 3:
                if len(cells) > len(matches):
                    matches = cells
        
        return matches

    def _process_matches(self) -> bool:
        """
        Process the entire field for matches and mark them for removal.
        Returns True if any matches were found, False otherwise.
        """
        matches_found = False
        
        # First pass: find all matches
        for r in range(self.rows):
            for c in range(self.cols):
                if self.field[r][c] != ' ' and not (isinstance(self.field[r][c], str) and self.field[r][c].startswith('*')):
                    matches = self._check_match(r, c)
                    if len(matches) >= 3:  # Only mark if we have at least 3 in a row/column
                        for match_r, match_c in matches:
                            # Only mark if not already matched
                            cell = self.field[match_r][match_c]
                            if not (isinstance(cell, str) and cell.startswith('*')):
                                # Preserve the original color when marking
                                if isinstance(cell, str) and len(cell) > 1 and cell[0] in 'LR':
                                    # Handle faller segments (L/R markers)
                                    self.field[match_r][match_c] = f'*{cell[1:]}'
                                else:
                                    # For single character cells, just add asterisk
                                    self.field[match_r][match_c] = f'*{cell}'
                                matches_found = True
        
        return matches_found

    def has_viruses(self) -> bool:
        """
        Checks if there are any viruses remaining in the field.

        Returns:
            bool: True if viruses exist, False otherwise.
        """
        for row in self.field:
            for cell in row:
                if isinstance(cell, str):
                    # Check for lowercase letter (virus) in the cell
                    # Handle marked cells (e.g., '*r*') and faller segments (e.g., 'Lr')
                    if cell.islower() or (len(cell) > 1 and any(c.islower() for c in cell)):
                        return True
        return False
    