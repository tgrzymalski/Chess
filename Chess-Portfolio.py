# Author: Tyler Grzymalski
# Github username: tgrzymalski
# Date: 12/08/2024
# Description: Fog of War Chess. Enemy pieces are obscured unless capturable. Game ends when a King is captured.
#              Standard moves are allowed, but no checks, checkmates, castling, en passant, or pawn promotion.

class ChessVar:
    """
    This is going to create and manage the board
    """
    def __init__(self):
        """Generates an empty board with default parameters and fills the board with ChessPiece objects"""
        self._board = [[None for _ in range(8)] for _ in range(8)]
        self._state = "UNFINISHED"
        self._turn = "white"
        self.initialize_pieces()

    def get_game_state(self):
        """Returns the state of the game (UNFINISHED, WHITE_WON, BLACK_WON)"""
        return self._state

    def get_board(self, perspective):
        """
        Iterates through the board and checks all possible potential moves of pieces. If a valid move can take an
        enemy piece, the location of that enemy piece is stored in a set.
        The board iterates through all spots and if there is a ChessPiece object, it labels that spot respectively,
        (p for black, P for white, * for obscured or blank for empty) taking into account the previously assembled
        set of capturable positions.
        Returns the board based on the requested perspective ('white', 'black', 'audience').
        """
        rows = range(8)
        cols = range(8)
        whole_board = []

        capturable_positions = set()
        for row in rows:
            for col in cols:
                piece = self._board[row][col]
                if piece and piece._color == perspective:
                    for next_row in range(8):
                        for next_col in range(8):
                            if piece.valid_move((row, col), (next_row, next_col), self._board):
                                target_piece = self._board[next_row][next_col]
                                if target_piece and target_piece.get_color() != piece.get_color():
                                    capturable_positions.add((next_row, next_col))

        for row in rows:
            board_row = []
            for col in cols:
                piece = self._board[row][col]
                if piece:
                    if perspective == 'audience':
                        if piece._color == 'black':
                            symbol = piece._symbol.lower()
                        else:
                            symbol = piece._symbol.upper()
                    else:
                        if piece._color == perspective or (row, col) in capturable_positions:
                            if piece._color == 'black':
                                symbol = piece._symbol.lower()
                            else:
                                symbol = piece._symbol.upper()
                        else:
                            symbol = "*"
                    board_row.append(symbol)
                else:
                    board_row.append(' ')
            whole_board.append(board_row)
        return whole_board

    def initialize_pieces(self):
        """Creates and places the pieces on the board in their starting positions."""
        def place_piece(row, col, piece):
            """Helper function to actually place the pieces"""
            self._board[row][col] = piece

        # Place pawns
        for col in range(8):
            place_piece(6, col, Pawn('white'))  # White pawns
            place_piece(1, col, Pawn('black'))  # Black pawns

        place_piece(7, 0, Rook('white'))
        place_piece(7, 7, Rook('white'))
        place_piece(0, 0, Rook('black'))
        place_piece(0, 7, Rook('black'))

        place_piece(7, 1, Knight('white'))
        place_piece(7, 6, Knight('white'))
        place_piece(0, 1, Knight('black'))
        place_piece(0, 6, Knight('black'))

        place_piece(7, 2, Bishop('white'))
        place_piece(7, 5, Bishop('white'))
        place_piece(0, 2, Bishop('black'))
        place_piece(0, 5, Bishop('black'))

        place_piece(7, 3, Queen('white'))
        place_piece(0, 3, Queen('black'))

        place_piece(7, 4, King('white'))
        place_piece(0, 4, King('black'))

    def make_move(self, cur_pos, next_pos):
        """
        Uses converted positions to ensure the current position has a piece, that piece is the current players color,
        and that the proposed move is valid.
        If those criteria are met, the method checks if the proposed move spot has
        an enemy King and if so, ends the game.
        If not, the move is completed and the turn ends.
        """
        current = self.alg_to_list(cur_pos)
        next_spot = self.alg_to_list(next_pos)

        if current and next_spot:
            piece = self._board[current[0]][current[1]]
            if piece is None:
                print("Invalid position!")
                return False
            elif piece and piece.get_color() == self._turn and piece.valid_move(current, next_spot, self._board):
                if (self._board[next_spot[0]][next_spot[1]] is not None and
                        self._board[next_spot[0]][next_spot[1]].get_symbol() == 'k'):
                    self._board[next_spot[0]][next_spot[1]] = piece
                    self._board[current[0]][current[1]] = None
                    self._state = 'WHITE WINS'
                    return True
                elif (self._board[next_spot[0]][next_spot[1]] is not None and
                      self._board[next_spot[0]][next_spot[1]].get_symbol() == 'K'):
                    self._board[next_spot[0]][next_spot[1]] = piece
                    self._board[current[0]][current[1]] = None
                    self._state = 'BLACK WINS'
                    return True
                else:
                    self._board[next_spot[0]][next_spot[1]] = piece
                    self._board[current[0]][current[1]] = None
                    self.get_board(self._turn)
                    self._turn = 'black' if self._turn == 'white' else 'white'
                    return True
            else:
                print("Invalid move!")
                return False

    def alg_to_list(self, pos):
        """Converts algebraic notation to board indices."""
        dictionary = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
        if pos[0] in dictionary:
            return [8 - int(pos[1]), dictionary[pos[0]]]
        return None


class ChessPiece:
    """
    Generates a template piece with a default color and symbol
    """
    def __init__(self, color, symbol):
        """Labels a piece black or white and takes a symbol"""
        self._color = color
        self._symbol = symbol

    def get_symbol(self):
        """Returns the symbol for the piece"""
        return self._symbol

    def get_color(self):
        """Returns the color for the piece"""
        return self._color


class Pawn(ChessPiece):
    """
    Child class of ChessPiece, pawns can move two spaces if the pawn is at the starting space, or else one space
    vertically.
    UNLESS capturing an enemy piece, which must be done diagonally.
    """
    def __init__(self, color):
        """Assigns the symbol P"""
        super().__init__(color, 'P')

    def valid_move(self, cur_pos, next_pos, board):
        """
        Checks what direction the piece can move and eligibility for moving two spaces.
        Checks against diagonal movement verifies proposed move is on the board, and that the proposed move is
        within one (or two) spaces.
        If the proposed move is diagonal, it verifies one space movement and enemy occupancy of the
        proposed move location.
        """
        direction = -1 if self._color == 'white' else 1
        start_row = 6 if self._color == 'white' else 1

        current_row, current_col = cur_pos
        next_row, next_col = next_pos

        if current_col == next_col:
            if next_row == current_row + direction and board[next_row][next_col] is None:
                if not (0 <= current_row < 8 and 0 <= current_col < 8):
                    return False
                return True
            if (current_row == start_row and next_row == current_row + direction + direction and
                    board[current_row + direction][current_col] is None and board[next_row][next_col] is None):
                if not (0 <= current_row < 8 and 0 <= current_col < 8):
                    return False
                return True

        if abs(current_col - next_col) == 1 and next_row == current_row + direction:
            target_piece = board[next_row][next_col]
            if target_piece and target_piece.get_color() != self._color:
                return True

        return False


class Rook(ChessPiece):
    """
    Child class of ChessPiece, rooks can move vertically or horizontally until obstructed.
    """
    def __init__(self, color):
        """Assigns the symbol R"""
        super().__init__(color, 'R')

    def valid_move(self, cur_pos, next_pos, board):
        """
        Checks that the move will either be horizontal or vertical.
        Checks what directional adjustments need to be made to get to next position.
        If horizontal (or vertical), movement will be limited to that plane so long as it stays on the board and
        does not run into other pieces.
        If there is a piece at next position, it verifies that it is an enemy piece being taken.
        """
        if cur_pos[0] != next_pos[0] and cur_pos[1] != next_pos[1]:
            return False

        row_step = 0 if cur_pos[0] == next_pos[0] else (1 if next_pos[0] > cur_pos[0] else -1)
        col_step = 0 if cur_pos[1] == next_pos[1] else (1 if next_pos[1] > cur_pos[1] else -1)

        current_row, current_col = cur_pos
        while cur_pos != next_pos:
            current_row += row_step
            current_col += col_step
            cur_pos = [current_row, current_col]
            if not (0 <= current_row < 8 and 0 <= current_col < 8):
                return False
            if cur_pos != next_pos and board[current_row][current_col] is not None:
                return False
        target_piece = board[next_pos[0]][next_pos[1]]
        if target_piece is None:
            return True
        if target_piece.get_color() != self._color:
            return True


class Bishop(ChessPiece):
    """
    Child class of ChessPiece, bishops can move diagonally until obstructed.
    """
    def __init__(self, color):
        """Assigns the symbol B"""
        super().__init__(color, 'B')

    def valid_move(self, cur_pos, next_pos, board):
        """
        Verifies that the proposed move is exclusively diagonal.
        Checks what directional adjustments need to be made to get to next position.
        Increments (or decrements) the rows/columns to reach next position so long as there are no obstructions and
        the move remains on the board.
        If there is a piece at next position, it verifies that it is an enemy piece being taken.
        """
        if cur_pos[0] == next_pos[0] or cur_pos[1] == next_pos[1]:
            return False

        row_step = 1 if next_pos[0] > cur_pos[0] else -1
        col_step = 1 if next_pos[1] > cur_pos[1] else -1

        current_row, current_col = cur_pos
        while cur_pos != next_pos:
            current_row += row_step
            current_col += col_step
            if not (0 <= current_row < 8 and 0 <= current_col < 8):
                return False
            cur_pos = [current_row, current_col]
            if cur_pos != next_pos and board[current_row][current_col] is not None:
                return False

        target_piece = board[next_pos[0]][next_pos[1]]
        if target_piece is None:
            return True
        if target_piece.get_color() != self._color:
            return True
        return False


class Knight(ChessPiece):
    """
    Child class of ChessPiece, knights can move in an L shape.
    """
    def __init__(self, color):
        """Assigns the symbol N"""
        super().__init__(color, 'N')

    def valid_move(self, cur_pos, next_pos, board):
        """
        Makes a check that the proposed move is some form of an L shape, potentially overstepping other pieces.
        Checks to make sure the next position is either vacant or occupied by an enemy piece.
        """
        current_row, current_col = cur_pos
        if [current_row + 2, current_col + 1] != next_pos:
            if [current_row + 2, current_col - 1] != next_pos:
                if [current_row + 1, current_col + 2] != next_pos:
                    if [current_row + 1, current_col - 2] != next_pos:
                        if [current_row - 2, current_col + 1] != next_pos:
                            if [current_row - 2, current_col - 1] != next_pos:
                                if [current_row - 1, current_col + 2] != next_pos:
                                    if [current_row - 1, current_col - 2] != next_pos:
                                        return False

        target_piece = board[next_pos[0]][next_pos[1]]
        if target_piece is None:
            return True
        if target_piece.get_color() != self._color:
            return True


class Queen(ChessPiece):
    """
    Child class of ChessPiece, the queen can move vertically, horizontally, or diagonally until obstructed.
    """
    def __init__(self, color):
        """Assigns the symbol Q"""
        super().__init__(color, 'Q')

    def valid_move(self, cur_pos, next_pos, board):
        """
        Moves either exclusively vertically, horizontally, or diagonally so long as no pieces obstruct the path to
        the next position.
        Checks to make sure the next position is either vacant or occupied by an enemy piece.
        """
        if cur_pos[0] == next_pos[0] or cur_pos[1] == next_pos[1]:
            row_step = 0 if cur_pos[0] == next_pos[0] else (1 if next_pos[0] > cur_pos[0] else -1)
            col_step = 0 if cur_pos[1] == next_pos[1] else (1 if next_pos[1] > cur_pos[1] else -1)

            current_row, current_col = cur_pos
            while cur_pos != next_pos:
                current_row += row_step
                current_col += col_step
                cur_pos = [current_row, current_col]
                if not (0 <= current_row < 8 and 0 <= current_col < 8):
                    return False
                if cur_pos != next_pos and board[current_row][current_col] is not None:
                    return False
            target_piece = board[next_pos[0]][next_pos[1]]
            if target_piece is None:
                return True
            if target_piece.get_color() != self._color:
                return True

        if cur_pos[0] != next_pos[0] and cur_pos[1] != next_pos[1]:
            row_step = 1 if next_pos[0] > cur_pos[0] else -1
            col_step = 1 if next_pos[1] > cur_pos[1] else -1

            current_row, current_col = cur_pos
            while cur_pos != next_pos:
                current_row += row_step
                current_col += col_step
                cur_pos = [current_row, current_col]
                if not (0 <= current_row < 8 and 0 <= current_col < 8):
                    return False
                if cur_pos != next_pos and board[current_row][current_col] is not None:
                    return False
            target_piece = board[next_pos[0]][next_pos[1]]
            if target_piece is None:
                return True
            if target_piece.get_color() != self._color:
                return True


class King(ChessPiece):
    """
    Child class of ChessPiece, the king can move to any square within one distance of itself.
    """
    def __init__(self, color):
        """Assigns the symbol K"""
        super().__init__(color, 'K')

    def valid_move(self, cur_pos, next_pos, board):
        """
        Moves either vertically, horizontally, or diagonally one square.
        Checks to make sure the next position is either vacant or occupied by an enemy piece.
        """
        moves = 0
        if cur_pos[0] == next_pos[0] or cur_pos[1] == next_pos[1]:
            row_step = 0 if cur_pos[0] == next_pos[0] else (1 if next_pos[0] > cur_pos[0] else -1)
            col_step = 0 if cur_pos[1] == next_pos[1] else (1 if next_pos[1] > cur_pos[1] else -1)

            current_row, current_col = cur_pos
            while cur_pos != next_pos:
                moves += 1
                current_row += row_step
                current_col += col_step
                cur_pos = [current_row, current_col]
                if not (0 <= current_row < 8 and 0 <= current_col < 8):
                    return False
                if (cur_pos != next_pos and board[current_row][current_col] is not None) or moves > 1:
                    return False
            target_piece = board[next_pos[0]][next_pos[1]]
            if target_piece is None:
                return True
            if target_piece.get_color() != self._color:
                return True

        if cur_pos[0] != next_pos[0] and cur_pos[1] != next_pos[1]:
            row_step = 1 if next_pos[0] > cur_pos[0] else -1
            col_step = 1 if next_pos[1] > cur_pos[1] else -1

            current_row, current_col = cur_pos
            while cur_pos != next_pos:
                moves += 1
                current_row += row_step
                current_col += col_step
                cur_pos = [current_row, current_col]
                if not (0 <= current_row < 8 and 0 <= current_col < 8):
                    return False
                if (cur_pos != next_pos and board[current_row][current_col] is not None) or moves > 1:
                    return False
            target_piece = board[next_pos[0]][next_pos[1]]
            if target_piece is None:
                return True
            if target_piece.get_color() != self._color:
                return True



def main():
    game = ChessVar()

    while game.get_game_state() == "UNFINISHED":
        for i in ChessVar.get_board(game, game._turn):
            print(i)
        print(f"{game._turn.capitalize()}'s turn.")
        move = input("Enter your move (e.g., e2 e4): ")
        try:
            cur_pos, next_pos = move.split()
            if not game.make_move(cur_pos, next_pos):
                print("Invalid move. Try again.")
        except ValueError:
            print("Invalid input format. Please use e.g., e2 e4")

    print(f"Game Over! {game.get_game_state()}")

if __name__ == "__main__":
    main()