## CS3243 Sudoku AY2019/20 Sem 1
# Authors: Cheong Siu Hong (A0188018Y) & Douglas Wei Jing Allwood (A0183939L)
# Date: 17 October 2019

import sys
import copy
from collections import deque
import pprint


class Sudoku(object):

    # 1. Assign all values that can be deterministically assigned based off
    # what values peers in the same Unit have taken.
    # 3. Perform Back-Tracking Search

    def __init__(self, puzzle):
        self.digits = '123456789'
        # List of coordinates
        self.squares = [(int(x), int(y))
                        for x in self.digits for y in self.digits]
        # All the units
        self.rows = [[(int(x), int(y)) for x in self.digits]
                     for y in self.digits]
        self.cols = [[(int(x), int(y)) for y in self.digits]
                     for x in self.digits]
        self.blocks = [[(int(x), int(y)) for x in X for y in Y]
                       for X in ('123', '456', '789') for Y in ('123', '456', '789')]

        # Puzzle: The current state of the puzzle
        self.puzzle = puzzle  # List of rows of integers [0-9], 0 == unfilled
        self.ans = copy.deepcopy(puzzle)

        # square_domain: Dict of the domain of each square. Domain is a list
        self.square_domain = self.initialise_domains()
        self.neighbour_domain = self.initialise_neighbours()
        # A unit is a list of squares that belong in the same row, column or block
        self.units = self.initialise_units()

#### INITIALIZATION ######################################################################

    # Returns a dictionary of Square => Domain of Square
    def initialise_domains(self):
        domain = dict((square, self.digits) for square in self.squares)
        for row in range(9):
            for col in range(9):
                # If a value was assigned
                val = self.puzzle[row][col]
                if val != 0:
                    domain[(row + 1, col + 1)] = str(val)
        return domain

    # Returns a dictionary of Square => Neighbours of Square
    def initialise_neighbours(self):
        nb = dict((square, self.enumerate_neighbours(square))
                  for square in self.squares)
        return nb

    # Returns a dictionary of Square => Units containing Square
    def initialise_units(self):
        u = dict((square, self.enumerate_units(square))
                 for square in self.squares)
        return u

    # Returns all neighbours of a square
    def enumerate_neighbours(self, square):
        row = [copy.deepcopy(r) for r in self.rows if square in r][0]
        col = [copy.deepcopy(c) for c in self.cols if square in c][0]
        block = [copy.deepcopy(b) for b in self.blocks if square in b][0]
        row.remove(square)
        col.remove(square)
        block.remove(square)
        return list(dict.fromkeys(row + col + block))

    # Enumerates all units for a square
    def enumerate_units(self, square):
        row = [copy.deepcopy(r) for r in self.rows if square in r]
        col = [copy.deepcopy(c) for c in self.cols if square in c]
        block = [copy.deepcopy(b) for b in self.blocks if square in b]
        return row + col + block

    # Returns all neighbours of a square
    def get_neighbours(self, square):
        return self.neighbour_domain[square]

#### UTILITY #################################################################################

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

    # Returns the size of a square's domain
    def size_of_domain(self, square):
        return len(self.square_domain[square])

    # True if every domain has one and only one value
    def goal_test(self, square_domain):
        return all(len(square_domain[square]) == 1 for square in square_domain)

    # True if any domain has no values
    def unsolvable_test(self, square_domain):
        return any(len(square_domain[square]) == 0 for square in square_domain)

    # Returns a list of (len, Square) of all Squares that are not yet assigned
    def get_unassigned_squares(self, domains):
        return [(len(domains[square]), square) for square in domains if len(domains[square]) > 1]

#### PREPROCESSING STEPS ##################################################################

    # AC-3 Algorithm that updates puzzle and square_domain in place
    # Constraint: AllDiff in all units
    def propagate_constraints(self):
        assigned_queue = deque(self.get_all_assigned_squares())
        while len(assigned_queue) > 0:
            square = assigned_queue.popleft()
            square_val = self.value_of(square)
            neighbours = self.get_neighbours(square)
            # Only consider updated_neighbours to avoid infinite loop
            # This should raise an error if domain goes to zero for any of the squares
            updated_neighbours = self.shrink_domains(neighbours, square_val)
            for neighbour in updated_neighbours:
                assigned_queue.append(neighbour)
        # Update self.puzzle
        self.puzzle = self.domains_to_puzzle()

    def get_all_assigned_squares(self):
        assigned_squares = []
        for row in range(1, 10):
            for col in range(1, 10):
                square = (row, col)
                if len(self.square_domain[square]) == 1:
                    assigned_squares.append(square)
        return assigned_squares

    def shrink_domains(self, neighbours, value):
        updated_neighbours = []
        for neighbour in neighbours:
            domain = self.square_domain[neighbour]
            if str(value) in domain:
                self.square_domain[neighbour] = domain.replace(str(value), '')
                if self.size_of_domain(neighbour) == 1:
                    updated_neighbours.append(neighbour)
        return updated_neighbours

#### Searching #############################################################################

    # Returns domains if success, False otherwise
    def search(self, domains):
        if self.unsolvable_test(domains):  # Failed
            return False

        if self.goal_test(domains):  # Done
            return domains

        # Get square with the least available value
        num_available_values, square_to_assign = min(
            self.get_unassigned_squares(domains))
        available_values = domains[square_to_assign]

        # Assign each value to the square and recurse
        for digit in available_values:
            domains[square_to_assign] = digit
            new_domains = self.shrink_domains_recursive(
                square_to_assign, digit, domains.copy())

            result = self.search(new_domains)
            if result:
                return result

    # Returns domains after propagation
    def shrink_domains_recursive(self, square, digit, domains):
        for neighbour in self.get_neighbours(square):
            domain = domains[neighbour]
            if digit in domain:
                domains[neighbour] = domain.replace(digit, '')
                # If a square is reduced to one value, propagate contraints to its neighbours
                num_values_left = len(domains[neighbour])
                if num_values_left == 1:
                    self.shrink_domains_recursive(
                        neighbour, domains[neighbour], domains)
                # Early termination
                elif num_values_left == 0:
                    return domains

                # If there is only one square left for the eliminated digit in any enclosing unit,
                # Assign the digit to the square and propagate constraints accordingly
                for unit in self.units[neighbour]:
                    squares_left_for_digit = [
                        square for square in unit if digit in domains[square]]
                    spaces_left = len(squares_left_for_digit)
                    if spaces_left == 1:
                        last_square = squares_left_for_digit[0]
                        domains[last_square] = digit
                        self.shrink_domains_recursive(
                            last_square, digit, domains)

        return domains

#### Solution ################################################################################

    def solve(self):
        self.propagate_constraints()    # AC-3 algorithm: Preprocessing
        # Searching with AC-3 propagation
        self.square_domain = self.search(self.square_domain.copy())
        self.ans = self.domains_to_puzzle()
        return self.ans


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
