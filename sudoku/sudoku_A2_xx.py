import sys
import copy
import deque


class Sudoku(object):

    ## 1. Assign all values that can be deterministically assigned based off
    ##    what values peers in the same Unit have taken.
    ## 3. Perform Back-Tracking Search

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
    def domains_to_puzzle(self):
        rows = []
        for i in range(1, 10):
            row = []
            for j in range(1, 10):
                domain = self.square_domain[(i, j)]
                if len(domain) == 1:
                    row.append(int(domain))
                else:
                    row.append(0)
            rows.append(row)
        return rows

    # Returns the Value of a Square only if its domain is strictly of length 1
    def value_of(self, square):
        domain = self.square_domain[square]
        if len(domain) == 1:
            return int(domain)
        else:
            err_str = "Square {} has a domain: {}".format(square, domain)
            raise ValueError(err_str)

    # AC-3 Algorithm that updates puzzle and square_domain in place
    # Constraint: AllDiff in all units
    def propagate_constraints(self):
        assigned_queue = deque(self.get_all_assigned_squares())
        while len(queue) > 0:
            square = queue.popleft()
            square_val = self.value_of(square)
            neighbours = self.get_neighbours(square)
            # Only consider updated_neighbours to avoid infinite loop
            updated_neighbours = self.shrink_domains(neighbours, square_val)       # This should raise an error if domain goes to zero for any of the squares
            for neighbour in updated_neighbours:
                if self.size_of_domain(neighbour) == 1:
                    assigned_queue.append(neighbour)
        # Update self.puzzle
        self.puzzle = self.domains_to_puzzle()

    def get_all_assigned_squares(self):
        assigned_squares = []
        for row in range(9):
            for col in range(9):
                square = (row, col)
                if len(self.square_domain[square]) == 1:
                    assigned_squares.append(square)
        return assigned_squares

    def get_neighbours(self, square):
        row     = filter(lambda x: square in x, self.get_rows())[0]
        col     = filter(lambda x: square in x, self.get_cols())[0]
        block   = filter(lambda x: square in x, self.get_blocks())[0]
        row.remove(square)
        col.remove(square)
        block.remove(square)
        return row + col + block

    def shrink_domains(self, neighbours, value):
        updated_neighbours = []
        for neighbour in neighbours:
            domain = self.square_domain[neighbour]
            if str(value) in domain:
                self.square_domain[neighbour] = domain.replace(str(value), '')
                updated_neighbours.append(neighbour)
        return updated_neighbours

    def size_of_domain(self, neighbour):
        return len(self.square_domain[neighbour])

    def backtrack_search(self, state, domains):
        # The graph has been preprocessed
        # Get all the squares that have not been assigned sort in descending order
        incomplete_squares = self.get_incomplete_squares(state)  ########## If any domains are empty, return an empty list
        if len(incomplete_squares) == 0:
            return self.goal_test(state)
        square = incomplete_squares.pop()
        for value in domains[square]:
            new_state = copy.deepcopy(state)
            new_domains = copy.deepcopy(domains)
            new_state[square[0]][square[1]] = int(value)    # type(value): str
            new_domains[square] = value                     # type(value): str
            # Create a new copy where this value has been assigned to the Square
            # Call backtrack_search
            # If true, return state
        pass


    def solve(self):
        self.propagate_constraints()    # AC-3 algorithm: Preprocessing
        # Backtracking (DFS) algorithm
        state, domains = self.backtrack_search(self.puzzle, self.square_domain)



    # (True, State) if self.puzzle is a valid sudoku state, else (False, State)
    # Does NOT check for uniqueness of values
    def goal_test(self, state):
        # All units must sum to exactly 45: sum([1 to 9])
        # Check if rows sum to 45
        row_valid = all(map(lambda x: sum(x) == 45, self.get_rows(state)))
        # Check if columns sum to 45
        col_valid = all(map(lambda x: sum(x) == 45, self.get_cols(state)))
        # Check if blocks sum to 45
        blocks_valid = all(map(lambda x: sum(x) == 45, self.get_blocks(state)))
        return row_valid and col_valid and blocks_valid, state

    # Transpose a Matrix represented by a list of lists
    def transpose(self, matrix):
        return list(zip(*matrix))

    def get_rows(self, state):
        return copy.deepcopy(state)

    def get_cols(self, state):
        return self.transpose(self.get_rows(state))

    def get_blocks(self, state):
        block_indexes = [] # List of lists of indexes for a block
        for X in ('123', '456', '789'):
            for Y in ('123', '456', '789'):
                block_indexes.append([(int(x), int(y)) for x in X for y in Y])
        blocks = []
        for indexes in block_indexes:
            block = []
            for row, col in indexes:
                block.append(state[row][col])
            blocks.append(block)
        return blocks

    ############################# Siuhongs Methods #############################

    # def solve(self):
    #     values = dict((square, digits) for square in squares)
    #
    #     for i in range(9):
    #         for j in range(9):
    #             digit = str(self.puzzle[i][j])
    #             if digit != '0':
    #                 self.assign((i + 1, j + 1), digit, values)
    #
    #     self.ans = self.values_to_puzzle(values)
    #     return self.ans

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
