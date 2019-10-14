import sys
import copy

digits = '123456789'
# A square is a tuple (i ,j) with i and j indicating its coordinate
squares = [(int(x), int(y)) for x in digits for y in digits]
rows = [[(int(x), int(y)) for x in digits] for y in digits]
cols = [[(int(x), int(y)) for y in digits] for x in digits]
blocks = [[(int(x), int(y)) for x in X for y in Y]
          for X in ('123', '456', '789') for Y in ('123', '456', '789')]
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

    def __init__(self, puzzle):
        # you may add more attributes if you need
        self.puzzle = puzzle  # self.puzzle is a list of lists
        self.ans = copy.deepcopy(puzzle)  # self.ans is a list of lists

    def solve(self):
        values = dict((square, digits) for square in squares)

        for i in range(9):
            for j in range(9):
                digit = str(self.puzzle[j][i])
                if digit != '0':
                    self.assign((i + 1, j + 1), digit, values)

        self.ans = self.values_to_puzzle(values)
        return self.ans

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

    def values_to_puzzle(self, values):
        return [[int(values[(i, j)]) for i in range(1, 10)] for j in range(1, 10)]

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
