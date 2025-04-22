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
        """
        start_col = self.cols // 2
        if self.cols % 2 == 0:
            # Check if the middle two cells in the second row are occupied
            if self.field[1][start_col] != ' ' or self.field[1][start_col + 1] != ' ':
                self.game_over = True
                return
            self.faller = {'segments': [(1, start_col, color1), (1, start_col + 1, color2)], 'orientation': 'horizontal', 'landed': False}
        else:
            # Check if the middle cell in the second row is occupied
            if self.field[1][start_col] != ' ':
                self.game_over = True
                return
            self.faller = {'segments': [(1, start_col, color1), (0, start_col, color2)], 'orientation': 'vertical', 'landed': False}
            # For odd columns, we'll start vertical for simplicity of initial positioning
            self._rotate_clockwise() # Initial rotation to horizontal

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
        Rotates the faller clockwise.
        """
        if self.faller:
            segments = self.faller['segments']
            orientation = self.faller['orientation']
            r_pivot, c_pivot, _ = segments[1] # Bottom-left is the pivot in the 2x2 grid

            if orientation == 'horizontal':
                # Become vertical
                new_segments = [(r_pivot - 1, c_pivot, segments[0][2]), (r_pivot, c_pivot, segments[1][2])]
                if self._can_move(new_segments):
                    self.faller['segments'] = new_segments
                    self.faller['orientation'] = 'vertical'
                else:
                    # Wall kick: try moving left then rotating
                    new_segments_left = [(r, c - 1, color) for r, c, color in segments]
                    if self._can_move(new_segments_left):
                        rotated_segments = [(r_pivot - 1, c_pivot - 1, segments[0][2]), (r_pivot, c_pivot - 1, segments[1][2])]
                        if self._can_move(rotated_segments):
                            self.faller['segments'] = rotated_segments
                            self.faller['orientation'] = 'vertical'
                            return # Rotation successful after wall kick

            elif orientation == 'vertical':
                # Become horizontal
                new_segments = [(r_pivot, c_pivot - 1, segments[0][2]), (r_pivot, c_pivot, segments[1][2])]
                if self._can_move(new_segments):
                    self.faller['segments'] = new_segments
                    self.faller['orientation'] = 'horizontal'

    def _rotate_counterclockwise(self) -> None:
        """
        Rotates the faller counterclockwise.
        """
        if self.faller:
            segments = self.faller['segments']
            orientation = self.faller['orientation']
            r_pivot, c_pivot, _ = segments[1] # Bottom-left is the pivot

            if orientation == 'horizontal':
                # Become vertical
                new_segments = [(r_pivot - 1, c_pivot - 1, segments[0][2]), (r_pivot, c_pivot - 1, segments[1][2])]
                if self._can_move(new_segments):
                    self.faller['segments'] = new_segments
                    self.faller['orientation'] = 'vertical'
                else:
                    # Wall kick (same logic as clockwise for this assignment)
                    new_segments_left = [(r, c - 1, color) for r, c, color in segments]
                    if self._can_move(new_segments_left):
                        rotated_segments = [(r_pivot - 1, c_pivot - 2, segments[0][2]), (r_pivot, c_pivot - 2, segments[1][2])]
                        if self._can_move(rotated_segments):
                            self.faller['segments'] = rotated_segments
                            self.faller['orientation'] = 'vertical'
                            return

            elif orientation == 'vertical':
                # Become horizontal
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
        """
        if self.faller:
            if not self.faller['landed']:
                new_segments = [(r + 1, c, color) for r, c, color in self.faller['segments']]
                if self._can_move(new_segments):
                    self.faller['segments'] = new_segments
                else:
                    self.faller['landed'] = True
                    for r, c, color in self.faller['segments']:
                        # Mark the landed faller segments in the field
                        if self.faller['orientation'] == 'horizontal':
                            left_c = min(c1 for _, c1, _ in self.faller['segments'])
                            if c == left_c:
                                self.field[r][c] = f'L{color}' # Left horizontal
                            else:
                                self.field[r][c] = f'R{color}' # Right horizontal
                        else:
                            self.field[r][c] = color # Vertical is treated as single segments upon landing
                    self.faller = None
                    self._process_matches()
                    self._apply_field_gravity()
            else:
                self._apply_field_gravity() # Apply gravity to any floating pieces
                self._process_matches()

        else:
            self._apply_field_gravity()
            self._process_matches()

    def _apply_field_gravity(self) -> None:
        """
        Applies gravity to any single capsule pieces with empty space below.
        """
        moved = True
        while moved:
            moved = False
            new_field = [row[:] for row in self.field]
            for r in range(self.rows - 2, -1, -1):
                for c in range(self.cols):
                    cell = self.field[r][c]
                    if cell.isalpha() and cell.isupper() and self.field[r + 1][c] == ' ':
                        new_field[r + 1][c] = cell
                        new_field[r][c] = ' '
                        moved = True
            self.field = new_field

    def add_virus(self, row: int, col: int, color: str) -> None:
        """
        Adds a virus to the specified cell.

        Args:
            row (int): The row index (0-based).
            col (int): The column index (0-based).
            color (str): The color of the virus ('r', 'b', or 'y').
        """
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.field[row][col] = color

    def _check_match(self, r: int, c: int) -> List[Tuple[int, int]]:
        """
        Checks for matches of 4 or more in horizontal and vertical directions from a given cell.

        Args:
            r (int): The row index.
            c (int): The column index.

        Returns:
            List[Tuple[int, int]]: A list of coordinates that are part of a match.
        """
        matched = []
        color = self.field[r][c][0].upper() if self.field[r][c].isalpha() else None
        if not color:
            return matched

        # Horizontal check
        horizontal_match = [(r, c)]
        # Check left
        for i in range(c - 1, -1, -1):
            if self.field[r][i][0].upper() == color:
                horizontal_match.append((r, i))
            else:
                break
        # Check right
        for i in range(c + 1, self.cols):
            if self.field[r][i][0].upper() == color:
                horizontal_match.append((r, i))
            else:
                break
        if len(horizontal_match) >= 4:
            matched.extend(horizontal_match)

        # Vertical check
        vertical_match = [(r, c)]
        # Check up
        for i in range(r - 1, -1, -1):
            if self.field[i][c][0].upper() == color:
                vertical_match.append((i, c))
            else:
                break
        # Check down
        for i in range(r + 1, self.rows):
            if self.field[i][c][0].upper() == color:
                vertical_match.append((i, c))
            else:
                break
        if len(vertical_match) >= 4:
            matched.extend(vertical_match)

        return list(set(matched)) # Remove duplicates

    def _process_matches(self) -> None:
        """
        Checks the entire field for matches and marks them for removal.
        """
        matched_cells = set()
        for r in range(self.rows):
            for c in range(self.cols):
                if self.field[r][c] != ' ':
                    matches = self._check_match(r, c)
                    if matches:
                        matched_cells.update(matches)

        # Mark matched cells
        for r, c in matched_cells:
            self.field[r][c] = f'*{self.field[r][c]}*'

        # Remove matched cells
        new_field = [row[:] for row in self.field]
        for r in range(self.rows):
            for c in range(self.cols):
                if self.field[r][c].startswith('*') and self.field[r][c].endswith('*'):
                    new_field[r][c] = ' '
        self.field = new_field

    def has_viruses(self) -> bool:
        """
        Checks if there are any viruses remaining in the field.

        Returns:
            bool: True if viruses exist, False otherwise.
        """
        for row in self.field:
            for cell in row:
                if cell.islower():
                    return True
        return False
    