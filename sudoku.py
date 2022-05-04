import pyautogui
from PIL import Image, ImageGrab
from tesserocr import PyTessBaseAPI
import keyboard
import copy
from string import digits
from itertools import product
from random import shuffle, randrange
from datetime import datetime

class Sudoku:
    def __init__(self, show_progress=False, tessdata_path = "C:/Program Files (x86)/Tesseract-OCR/tessdata"):
        """
        Class to generate and solve Sudokus

        Args:
            show_progress (bool): if True, logs progress to console (default False)

            tessdata_path (string): set path for tesseract data (default C:/Program Files (x86)/Tesseract-OCR/tessdata)
            
        """
        self.__grid = [ [0]*9 for i in range(9)]
        self.__solution = [ [0]*9 for i in range(9)]
        self.__tiles = [ [0]*9 for i in range(9)]
        self.__progress = show_progress
        self.__tlx, self.__tly, self.__brx, self.__bry = -1, -1, -1, -1
        self.__solved = False

        self.__api = PyTessBaseAPI(path=tessdata_path)
        self.__api.SetVariable('tessedit_char_whitelist', digits)
    
    def __del__(self):
        if hasattr(self, '__api'):
            self.__api.End()

    class GridError(Exception):
        pass

    def __now(self):
        return datetime.now().strftime("%H:%M:%S")

    def __locate_grid(self):
        if tlc := pyautogui.locateOnScreen('images/top_left.png', grayscale=True):
            pass
        elif tlc :=pyautogui.locateOnScreen('images/top_left1.png', grayscale=True):
            pass
        elif tlc :=pyautogui.locateOnScreen('images/top_left2.png', grayscale=True):
            pass
            

        if brc := pyautogui.locateOnScreen('images/bottom_right.png', grayscale=True):
            pass
        elif brc :=pyautogui.locateOnScreen('images/bottom_right1.png', grayscale=True):
            pass
        elif brc :=pyautogui.locateOnScreen('images/bottom_right2.png', grayscale=True):
            pass
        
        if tlc and brc:
            tlx, tly = tlc.left + 3, tlc.top + 3
            brx, bry = brc.left + 9, brc.top + 9
            self.__tlx, self.__tly, self.__brx, self.__bry = tlx, tly, brx, bry

    def __process_image(self):
        height, width = self.__image.size
        image_data = self.__image.load()
        for x in range(height):
            for y in range(width):
                r,g,b = image_data[x,y]
                if r > 150:
                    image_data[x,y] = 255, 255, 255
                else:
                    image_data[x,y] = 0, 0, 0

    def __get_tiles(self):
        w, h = self.__image.size
        w = w//9*9
        if w < 450:
            raise self.GridError("Grid too small")
        self.__image = self.__image.resize((w, w))
        w, h = self.__image.size
        self.__process_image()
        d = int(w//9)
        self.__grid = product(range(0, h-h%d, d), range(0, w-w%d, d))
        for i, j in self.__grid:
            box = (j+10, i+10, j+d-10, i+d-10)
            self.__tiles[int(i/d)][int(j/d)] = self.__image.crop(box)

    def __merge(self, img1, img2):
        image1_size = img1.size

        new_image = Image.new('RGB',(2*image1_size[0], image1_size[1]), (250,250,250))

        new_image.paste(img1,(0,0))
        new_image.paste(img2,(image1_size[0],0))

        return new_image

    def __get_num(self, image):
        zero = Image.open('images/0.png')
        pil_image = self.__merge(image, zero)

        self.__api.SetImage(pil_image)
        data = self.__api.GetUTF8Text()
        return int(int(data if data else 0)/10)
    
    def __read_grid_image(self):
        self.__grid = []
        for line in self.__tiles:
            ln = []
            for img in line:
                ln.append(self.__get_num(img))
            self.__grid.append(ln)


    def __possible(self, grid, row, col, num):
        for x in range(9):
            if grid[row][x] == num:
                return False
                
        for x in range(9):
            if grid[x][col] == num:
                return False
    
    
        startRow = row - row % 3
        startCol = col - col % 3
        for i in range(3):
            for j in range(3):
                if grid[i + startRow][j + startCol] == num:
                    return False
        return True

    def solutions(self, grid):
        for y in range(9):
            for x in range(9):
                if grid[y][x] == 0:
                    for n in range(1, 10):
                        if self.__possible(grid, y, x, n):
                            grid[y][x] = n
                            if self.count > 1:
                                return
                            self.solutions(grid)
                            grid[y][x] = 0
                    return
        self.count += 1

    def __solve(self, row=0, col=0):
        if col == 9:
            if row == 8:
                return True
            row += 1
            col = 0
        
        if self.__solution[row][col]:
            return self.__solve(row, col+1)

        for num in range(1, 10):
            if self.__possible(self.__solution, row, col, num):
                self.__solution[row][col] = num

                if self.__solve(row, col + 1):
                    return True

            self.__solution[row][col] = 0

        return False

    def __generate(self, difficulity = 0, row=0, col=0):
        if col == 9:
            if row == 8:
                failed = 0
                l = [[x, y] for x in range(9) for y in range(9)]
                shuffle(l)

                for _ in range(40 - (int(difficulity**1.2)*5) if difficulity < 5 and difficulity >= 0 else 0 if difficulity >= 0 else 40):
                    l.pop(randrange(len(l)))
                
                removed = 1
                while removed:
                    for i in l:
                        if failed >= len(l) or len(l) == 1:
                            removed = 0
                            break
                        row, col = i[0], i[1]
                        backup = self.__grid[row][col]
                        self.__grid[row][col] = 0
                        copyGrid = copy.deepcopy(self.__grid)
                        
                        self.count = 0
                        self.solutions(copyGrid)
                        
                        l.remove(i)

                        if self.count != 1:
                            self.__grid[row][col] = backup
                            failed += 1
                        else:
                            failed = 0
                return True
            row += 1
            col = 0

        numbers = [x for x in range(1, 10)]
        shuffle(numbers)
        for num in numbers:
            if self.__possible(self.__grid, row, col, num):
                self.__grid[row][col] = num

                if self.__generate(difficulity, row, col + 1):
                    return True

            self.__grid[row][col] = 0

        return False
    
    def get_grid(self):
        """
        Function to get Sudoku grid from sudoku.com website

        Raises:
            GridError: Grid not found - program was unable to find grid on screen
            GridError: Failed to process grid - program was unable to get values from grid image
            GridError: Grid too small - grid is too small to be accurately processed
        """
        if self.__progress:
            print(self.__now(), "Searching for grid...")
        self.__locate_grid()
        if self.__progress:
            print(self.__now(), "Grid located")
        if self.__tlx > 0:
            self.__image = ImageGrab.grab(bbox=(self.__tlx, self.__tly, self.__brx, self.__bry))
            try:
                if self.__progress:
                    print(self.__now(), "Processing grid...")
                self.__get_tiles()
                self.__read_grid_image()
                if self.__progress:
                    print(self.__now(), "Grid processed")
                self.__solved = False
            except:
                raise self.GridError("Failed to process grid")
        else:
            raise self.GridError("Grid not found")

    def solve(self):
        """
        Solve currently stored grid

        Raises:
            GridError: Sudoku is unsolvable - Sudoku has no valid solutions
        """
        self.__solution = copy.deepcopy(self.__grid)
        if self.__progress:
            print(self.__now(), "Solving sudoku...")
        if not self.__solve():
            raise self.GridError("Sudoku is unsolvable")
        if self.__progress:
            print(self.__now(), "Sudoku solved")
        self.__solved = True

    def generate(self, difficulity = 0):
        """
        Function to generate Sudoku grid

        Args:
            difficulity (int): difficulity of generated Sudoku
                0 - very easy (~39 empty cells),

                1 - easy (~43 empty cells),

                2 - medium (~47 empty cells),

                3 - hard (~50 empty cells),

                4 - very hard (~54 empty cells),

                5 - extreme (~56 empty cells)
        """
        if self.__progress:
            print(self.__now(), "Generating grid...")
        self.__generate(difficulity=difficulity)
        if self.__progress:
            print(self.__now(), "Grid generated")
    

    def write_grid(self, random=False, vertical=False, delay=100):
        """
        Writes currently stored solution to sudoku.com website's grid in lines from left to right

        Args:
            random (bool): if True, writes numbers in random order (default False)
            vertical (bool): it True, writes numbers in columns from top to bottom (default False)
            delay (int): delay in ms to wait between writing numbers (default 100ms)

        Raises:
            GridError: Sudoku not solved - there is no solved sudoku
        """
        if self.__solved:
            pyautogui.PAUSE = delay/1000
            if self.__progress:
                print(self.__now(), "Searching for grid...")
            self.__locate_grid()
            if self.__progress:
                print(self.__now(), "Grid located")
                print(self.__now(), "Starting to write...")
            if self.__tlx > 0:
                offset = (self.__brx - self.__tlx) // 9
                if random:
                    l = [[x, y] for x in range(9) for y in range(9) if self.__grid[y][x] == 0]
                    shuffle(l)
                    for i in l:
                        if keyboard.is_pressed('q') == False:
                            # if self.__grid[j][i] == 0:
                            pyautogui.click(self.__tlx + offset/2 + i[0] * offset, self.__tly + offset/2 + i[1] * offset)
                            pyautogui.press(str(self.__solution[i[1]][i[0]]))
                        else:
                            return
                elif vertical:
                    for i in range(9):
                        for j in range(9):
                            if self.__grid[i][j] == 0:
                                if keyboard.is_pressed('q') == False:
                                    # if self.__grid[j][i] == 0:
                                    pyautogui.click(self.__tlx + offset/2 + i * offset, self.__tly + offset/2 + j * offset)
                                    pyautogui.press(str(self.__solution[j][i]))
                                else:
                                    return
                else:
                    for i in range(9):
                        for j in range(9):
                            if self.__grid[i][j] == 0:
                                if keyboard.is_pressed('q') == False:
                                    # if self.__grid[j][i] == 0:
                                    pyautogui.click(self.__tlx + offset/2 + j * offset, self.__tly + offset/2 + i * offset)
                                    pyautogui.press(str(self.__solution[i][j]))
                                else:
                                    return
                if self.__progress:
                    print(self.__now(), "Writing done")
        else:
            raise self.GridError("Sudoku not solved")

    def print_grid(self):
        """
        Prints currently stored grid to console
        """
        print("Grid:")
        for i in range(len(self.__grid)):
            for j in range(len(self.__grid[i])):
                print(self.__grid[i][j], end=" ")
                if not (j + 1) % 3 and j < 8:
                    print("|", end=" ")
            print()
            if not (i + 1) % 3 and i < 8:
                print("---------------------")

    def print_solution(self):
        """
        Prints currently stored solution to console

        Raises:
            GridError: Sudoku not solved - there is no solved sudoku
        """
        if self.__solved:
            print("Solution:")
            for i in range(len(self.__solution)):
                for j in range(len(self.__solution[i])):
                    print(self.__solution[i][j], end=" ")
                    if not (j + 1) % 3 and j < 8:
                        print("|", end=" ")
                print()
                if not (i + 1) % 3 and i < 8:
                    print("---------------------")
        else:
            raise self.GridError("Sudoku not solved")

    def grid(self):
        """
        Returns Sudoku grid

        Returns:
            grid (2D list): unsolved Sudoku grid
        """
        return self.__grid

    def solution(self):
        """
        Returns Sudoku solution

        Returns:
            solution (2D list): solved Sudoku grid
        """
        if self.__solved:
            return self.__solution
        else:
            raise self.GridError("Sudoku not solved")