import random
import numpy as np
import pygame
import mss

"""
    ▮ : hidden block
    P : flag ( The shape is similar haha )
    B : 💣
    0 ~ 8 : Number of mines nearby
"""


class Minesweeper(object):
    def __init__(self, ROWS=9, COLS=9, MINES=10, SIZE=100, display=False):
        """
        Initialize Minesweeper
        :param ROWS: int , Number of rows of the board
        :param COLS: int , Number of cols of the board
        :param MINES: int , Number of mines generated on the board
        :param SIZE: int , Size of display
        :param display: bool , Chooses weather to display the game with pygame
        """
        self.ROWS = ROWS
        self.COLS = COLS
        self.MINES = MINES
        self.display = display
        self.SIZE = SIZE

        self.game_field = np.zeros((self.ROWS, self.COLS), dtype=object)  # The complete game state
        self.state_field = np.zeros((self.ROWS, self.COLS), dtype=object)  # The state the player sees
        self.state_last = np.copy(self.state_field)

        self.won = 0  # Number of times a player wins a game
        self.lost = 0  # Number of times a player lost a game

        if display:
            self.initGUI()

        self.initGame()

    def initGame(self):
        """
        Initialize Game
        :return: void
        """
        self.game_field = self.initBoard()
        self.state_field = np.ones((self.ROWS, self.COLS), dtype=object) * "▮"

        self.action(0, 0)  # An initial starting point was specified for learning.

    def initBoard(self):
        """
        Initialize board
        :return: 2-dimensional numpy array , Game board with all information entered
        """
        ROWS = self.ROWS
        COLS = self.COLS
        board = np.zeros((ROWS, COLS), dtype=object)
        mines = self.MINES

        while mines > 0:
            (mine_row, mine_col) = (random.randint(0, ROWS - 1), random.randint(0, COLS - 1))

            if board[mine_row][mine_col] != "B":
                board[mine_row][mine_col] = "B"
                board = self.set_around(mine_row, mine_col, board)
                mines -= 1

        return board

    def set_around(self, mine_row, mine_col, board):
        """
        Increases the number around the mine by 1
        :param mine_row: int , mine's x position
        :param mine_col: int , mine's y position
        :param board: 2-dimensional numpy array , Array containing game board information
        :return: 2-dimensional numpy array , Game board with updated information
        """
        for row in range(mine_row - 1, mine_row + 2):
            for col in range(mine_col - 1, mine_col + 2):
                if (row < 0 or row >= self.ROWS) or (col < 0 or col >= self.COLS) or (board[row][col] == "B"):
                    continue

                board[row][col] += 1

        return board

    def initScreen(self):
        """
        Render board pattern and text
        :return: void
        """
        # Render hidden tiles
        for row in range(0, self.ROWS):
            for col in range(0, self.COLS):
                self.screen.blit(self.tile_dict[9], (self.TILE_ROW * row, self.TILE_COL * col))

        pygame.display.flip()

    def initGUI(self):
        """
        Initialize GUI
        :return:
        """
        pygame.init()
        pygame.mixer.quit()  # Fixes bug with high PyGame CPU usage

        # Scale to resolutions
        with mss.mss() as sct:
            img = np.array(sct.grab(sct.monitors[1]))
            self.SIZE = int(self.SIZE * img.shape[1] / 3840)
            SIZE = self.SIZE

        self.TILE_ROW = 32
        self.TILE_COL = 32
        self.GAME_WIDTH = self.TILE_ROW * self.ROWS
        self.GAME_HEIGHT = self.TILE_COL * self.COLS
        self.myfont = pygame.font.SysFont("Segoe UI", 32)
        self.font_color = (255, 255, 255)  # White
        self.screen = pygame.display.set_mode((self.GAME_WIDTH, self.GAME_HEIGHT))
        pygame.display.set_caption("Minesweeper | Won : {}  Lost : {}".format(self.won, self.lost))

        # Load Minesweeper tileset
        self.tile_mine = pygame.image.load('img/mine.jpg').convert()
        self.tile_0 = pygame.image.load('img/0.jpg').convert()
        self.tile_1 = pygame.image.load('img/1.jpg').convert()
        self.tile_2 = pygame.image.load('img/2.jpg').convert()
        self.tile_3 = pygame.image.load('img/3.jpg').convert()
        self.tile_4 = pygame.image.load('img/4.jpg').convert()
        self.tile_5 = pygame.image.load('img/5.jpg').convert()
        self.tile_6 = pygame.image.load('img/6.jpg').convert()
        self.tile_7 = pygame.image.load('img/7.jpg').convert()
        self.tile_8 = pygame.image.load('img/8.jpg').convert()
        self.tile_hidden = pygame.image.load('img/hidden.jpg').convert()
        self.tile_explode = pygame.image.load('img/explode.jpg').convert()
        self.tile_flag = pygame.image.load('img/flag.jpg').convert()
        self.tile_dict = {
            -3: self.tile_flag,
            -2: self.tile_explode,
            -1: self.tile_mine,
            0: self.tile_0,
            1: self.tile_1,
            2: self.tile_2,
            3: self.tile_3,
            4: self.tile_4,
            5: self.tile_5,
            6: self.tile_6,
            7: self.tile_7,
            8: self.tile_8,
            9: self.tile_hidden
        }

        self.initScreen()

    def open_tile(self, row, col, type="open"):
        """
        Find out which values to show in the state when a square is pressed
        :param isEmpty:
        :param row:
        :param col:
        :param type: open / flag
        :return:
        """
        if type == "open":
            if self.game_field[row][col] != "B":
                self.state_field[row][col] = self.game_field[row][col]

                if self.display:
                    self.draw(row, col, self.game_field[row][col])

                if self.state_field[row][col] == 0:
                    self.open_continuity(row, col)

        elif type == "flag":
            self.state_field[row][col] = "P"

            if self.display:
                self.draw(row, col, "flag")

    def open_continuity(self, current_row, current_col):
        print("continuity")
        """
        A function that opens tiles in succession
        :param current_row:
        :param current_col:
        :return:
        """
        for row in range(current_row - 1, current_row + 2):
            for col in range(current_col - 1, current_col + 2):
                if (row < 0 or row >= self.ROWS) or (col < 0 or col >= self.COLS):
                    continue

                if self.state_field[row][col] != '▮' or not (0 <= self.game_field[row][col] <= 8):
                    continue
                self.open_tile(row, col)

    def action(self, row, col):
        """
        External action, taken by human or agent
        :param row: The x-position of the coordinates at which the user or agent interacts.
        :param col: The y-position of the coordinates at which the user or agent interacts.
        :return: tuple , {s,r} => s : A game board that a user or agent interacts with , r : compensation for it
        """
        if self.game_field[row][col] == "B":
            self.lost += 1
            print("Win " + str(self.won) + " Lost " + str(self.lost))
            self.initGame()
            return {"s": self.state_field, "r": -1}

        self.open_tile(row, col)
        if self.display:
            pygame.display.flip()

        if np.sum(self.state_field == "P") == self.MINES:
            self.won += 1
            print("Win " + str(self.won) + " Lost " + str(self.lost))
            self.initGame()
            return {"s": self.state_field, "r": 1}

        reward = self.compute_reward()
        return {"s": self.state_field, "r": reward}

    def draw(self, r, c, type):
        type = self.state_field[r][c]

        if type == "P":
            self.screen.blit(self.tile_dict[-3], (self.TILE_ROW * c, self.TILE_COL * r))
        elif type == "▮":
            self.screen.blit(self.tile_dict[9], (self.TILE_ROW * c, self.TILE_COL * r))
        else:
            self.screen.blit(self.tile_dict[type], (self.TILE_ROW * c, self.TILE_COL * r))
        pygame.display.update()

    def compute_reward(self):
        """
        Computes the reward for a given action
        :return: reward
        """

        # Reward = 1 if we get less unknowns, 0 otherwise
        if (np.sum(self.state_last == '▮') - np.sum(self.state_field == '▮')) > 0:
            reward = 1
        else:
            reward = -1

        self.state_last = np.copy(self.state_field)
        return reward

    def printState(self):
        """Prints the current state"""
        grid = self.state_field
        COLS = grid.shape[1]
        ROWS = grid.shape[0]
        for row in range(0, ROWS):
            print(' ')
            for col in range(0, COLS):
                print(grid[row][col], end=' ')

    def printBoard(self):
        """Prints the board """
        grid = self.game_field
        COLS = grid.shape[1]
        ROWS = grid.shape[0]
        for row in range(0, ROWS):
            print(' ')
            for col in range(0, COLS):
                print(grid[row][col], end=' ')


if __name__ == "__main__":
    game = Minesweeper(display=True)

    game.printBoard()
    game.printState()

    while True:
        input_row = int(input('Enter row'))
        input_col = int(input('Enter column'))

        v = game.action(input_row, input_col)
        game.printState()
