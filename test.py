from matplotlib.pyplot import grid
from numpy import diff
from sudoku import Sudoku

if __name__ == '__main__':
    sudoku = Sudoku(show_progress=True)
    
    sudoku.generate()
    sudoku.print_grid()
    sudoku.solve()
    sudoku.print_solution()

    # sudoku.get_grid()
    # sudoku.solve()
    # sudoku.write_grid(random=True, delay=10)