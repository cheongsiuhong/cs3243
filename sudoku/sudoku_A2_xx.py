import sys
import copy
import deque

# A unit is a list of squares that must all have different digits
list_of_units = rows + cols + blocks
# units[square] returns all units that the square belongs to
units = dict((square,
              [unit for unit in list_of_units if square in unit])
             for square in squares)
# peers[square] returns a list of squares that are in the same units as the given square
peers = dict((square,
              # Remove duplicate squares from list
              list(
                  set(sum(units[square], [])) - set([square]) # A square is not a peer of itself
                  ))
             for square in squares)

class Sudoku(object):
    # Two constraints:
    # 1. Shrinking of domains when peers use a values
    # 2. Write the function assign_if_certain() Just assigns a value if domain is size 1. Updates both state representations
    # 3. Write the inference function that does a set left-diff with all its peers and assigns if only 1 value is left

    # Assign values and shrink all domains (Repeatedly)

    ## 1. Assign all values that can be deterministically assigned based off
    ##    what values peers in the same Unit have taken.
    ## 2. Assign all values based off inference via set difference with its
    ##    peers domains.
    ## 3. Perform Back-Tracking Search

    # domain size 1
    # set difference with peers
    # By this point, there is either deterministically a value, to which we assign
    # , update all neighbours, and add them back into the queue.
    # Or there is no deterministic value and we remove him from the queue

    # BFS

    def __init__(self, puzzle):
        self.digits = '123456789'
        self.squares = [(int(x), int(y)) for x in digits for y in digits]
        # Puzzle: The current state of the puzzle
        self.puzzle = puzzle  # List of rows of integers [0-9], 0 == unfilled
        # square_domain: Dict of the domain of each square. Domain is a list
        self.square_domain = initialise_domains()

    # Returns a dictionary of Square => Domain of Square
    def initialise_domains(self):
        domain = dict((square, self.digits) for square in self.squares)
        for row in range(9):
            for col in range(9):
                # If a value was assigned
                val = self.puzzle[row][col]
                if val != 0:
                    domain[(row, col)] = str(val)
        return domain


    # Converts the square_domain dictionary to a puzzle (list of lists)
    # - Strict: ValueError if the domain of any square is not of length 1
    def domains_to_puzzle(self, strict=True):
        rows = []
        for i in range(1, 10):
            row = []
            for j in range(1, 10):
                domain = self.square_domain[(i, j)]
                if strict and len(domain) != 1:
                    err_str = "The domain of {} is: {}".format((i, j), domain)
                    raise ValueError(err_str)
                row.append(int(domain))
            rows.append(row)
        return rows

    # Returns True if self.puzzle is a valid sudoku state and False otherwise
    # Does NOT check for uniqueness of values
    def goal_test(self):
        # All units must sum to exactly 45: sum([1 to 9])
        # Check if rows sum to 45
        row_valid = all(map(lambda x: sum(x) == 45, self.get_rows()))
        # Check if columns sum to 45
        col_valid = all(map(lambda x: sum(x) == 45, self.get_cols()))
        # Check if blocks sum to 45
        blocks_valid = all(map(lambda x: sum(x) == 45, self.get_blocks()))
        return row_valid and col_valid and blocks_valid

    # Transpose a Matrix represented by a list of lists
    def transpose(self, matrix):
        return list(zip(*matrix))

    def get_rows(self):
        return copy.deepcopy(self.puzzle)

    def get_cols(self):
        return self.transpose(self.get_rows())

    def get_blocks(self):
        block_indexes = [] # List of lists of indexes for a block
        for X in ('123', '456', '789'):
            for Y in ('123', '456', '789'):
                block_indexes.append([(int(x), int(y)) for x in X for y in Y])
        blocks = []
        for indexes in block_indexes:
            block = []
            for row, col in indexes:
                block.append(self.puzzle[row][col])
            blocks.append(block)
        return blocks

    # Returns the Value of a Square only if its domain is strictly of length 1
    def value_of(self, square):
        domain = self.square_domain[square]
        if len(domain) == 1:
            return int(domain)
        else:
            err_str = "Square {} has a domain: {}".format(square, domain)
            raise ValueError(err_str)

    # AC-3 Algorithm that updates puzzle and square_domain in place
    # Constraint 1: AllDiff in all units
    # Constraint 2: An extension of AllDiff used to infer the value of a square
    # via Set-Difference between the domain of the square and all its peers
    def propagate_constraints(self):
        # Start from a square that already has a value assigned
        current_square = self.get_an_assigned_square()
        current_value = self.value_of(current_square)

        # Queue of start_square's peer squares
        queue = deque(self.get_peers(start_square))
        while len(queue) > 0:
            pass
            # add to queue if length is one


    def solve(self):
        values = dict((square, digits) for square in squares)

        for i in range(9):
            for j in range(9):
                digit = str(self.puzzle[i][j])
                if digit != '0':
                    self.assign((i + 1, j + 1), digit, values)

        self.ans = self.values_to_puzzle(values)
        return self.ans

    #
    def assign(self, square, number, values):
        rest = values[square].replace(number, '')
        for digit in rest:
            if not self.eliminate(square, digit, values):
                return False
        return values

    def eliminate(self, square, number, values):
        # Number not in domain
        if number not in values[square]:
            return values
        # Remove number from domain
        values[square] = values[square].replace(number, '')
        # Domain is empty after removal
        if len(values[square]) == 0:
            return False
        # Domain has only one value left, remove the value from domains of all peers
        if len(values[square]) == 1:
            last_digit = values[square]
            for peer in peers[square]:
                if not self.eliminate(peer,last_digit, values):
                    return False

        return values

    # DFS on a fixed ordering of the Squares (Variables)
    def backtrack_search(self):
        pass

    def update_peers(self):
        pass

    def set_value(self):
        pass

    def decrement_domain(self):
        pass

    def get_peers(self):
        pass

    def validity_check(self):
        pass

    def solve(self):
        # Infer values according to the already provided values
        self.propagate_constraints()    # AC-3 algorithm
        self.backtrack_search()         # Backtracking (DFS) algorithm
        return self.domains_to_puzzle()


if __name__ == "__main__":
    # STRICTLY do NOT modify the code in the main function here
    if len(sys.argv) != 3:
        print("\nUsage: python sudoku_A2_xx.py input.txt output.txt\n")
        raise ValueError("Wrong number of arguments!")

    try:
        f = open(sys.argv[1], 'r')
    except IOError:
        print("\nUsage: python sudoku_A2_xx.py input.txt output.txt\n")
        raise IOError("Input file not found!")

    puzzle = [[0 for i in range(9)] for j in range(9)]
    lines = f.readlines()

    i, j = 0, 0
    for line in lines:
        for number in line:
            if '0' <= number <= '9':
                puzzle[i][j] = int(number)
                j += 1
                if j == 9:
                    i += 1
                    j = 0

    sudoku = Sudoku(puzzle)
    ans = sudoku.solve()

    with open(sys.argv[2], 'a') as f:
        for i in range(9):
            for j in range(9):
                f.write(str(ans[i][j]) + " ")
            f.write("\n")
