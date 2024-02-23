import random
from collections import deque

import numpy as np

"""
 B : Bomb, 지뢰
 U : Unknown, 아직 확인하지 않은 타일
 0 ~ 8 : 해당 타일을 기준으로 3 x 3 구역에서 존재하는 지뢰의 갯수
 P : Flag , 깃발
"""


class Minesweeper(object):
    def __init__(self, ROWS=9, COLUMNS=9, MINES=10, GUI=False):
        self.ROWS = ROWS
        self.COLUMNS = COLUMNS
        self.MINES_COUNT = MINES
        self.GRID = self.init_grid()  # 게임의 데이터 ( 지뢰의 위치, 근처의 지뢰 수 등 ) 을 저장하는 2차원 배열
        self.PLAYER_FIELD = self.init_field()  # 사용자에게 보여지는 화면을 저장하는 2차원 배열
        self.DONE = False

        self.move_count = 0  # 사용자가 상호작용한 횟수
        self.won = 0  # 사용자가 게임에서 이긴 횟수
        self.lost = 0  # 사용자가 게임에서 진 횟수

    def init_grid(self):
        """ 게임의 데이터를 저장하는 2차원 배열을 초기화하는 함수 """
        grid = np.zeros((self.ROWS, self.COLUMNS), dtype=object)
        mines = self.MINES_COUNT

        while mines > 0:
            row, col = random.randint(0, self.ROWS - 1), random.randint(0, self.COLUMNS - 1)

            if grid[row][col] != 'B':
                grid[row][col] = 'B'
                grid = self.add_neighbors(row, col, grid)
                mines -= 1

        return grid

    def add_neighbors(self, current_row, current_col, grid):
        """ 2차원 배열에서 지뢰 주변의 3 x 3 그리드의 값을 1씩 더해주는 함수 """
        for row in range(current_row - 1, current_row + 2):
            for col in range(current_col - 1, current_col + 2):
                if 0 <= row < self.ROWS and 0 <= col < self.COLUMNS and grid[row][col] != "B":
                    grid[row][col] += 1

        return grid

    def init_field(self):
        """ 사용자에게 보여지는 2차원 배열을 초기화하는 함수 """
        board = np.full((self.ROWS, self.COLUMNS), "U", dtype=object)
        return board

    def auto_reveal(self, current_row, current_col, player_field):
        for row in range(current_row - 1, current_row + 2):
            for col in range(current_col - 1, current_col + 2):
                if 0 <= row < self.ROWS and 0 <= col < self.COLUMNS:
                    pos = row * len(self.PLAYER_FIELD) + col
                    if self.GRID[row, col] != "B" and player_field[pos] == 'U':
                        player_field[pos] = self.GRID[row, col]

                        if player_field[pos] == 0:
                            player_field = self.auto_reveal(row, col, player_field)

        return player_field

    def reset(self):
        """ 게임의 상태를 초기화 시켜주는 함수 """
        self.GRID = self.init_grid()
        self.PLAYER_FIELD = self.init_field()
        self.DONE = False
        self.move_count = 0

    def step(self, action):
        action_pos = action[0] * len(self.PLAYER_FIELD) + action[1]

        flattened_player_field = self.PLAYER_FIELD.flatten()
        flattened_grid = self.GRID.flatten()
        flattened_player_field[action_pos] = flattened_grid[action_pos]

        num_flag_tiles = np.count_nonzero(flattened_player_field == "P")

        if flattened_player_field[action_pos] == "B":
            """ 지뢰를 클릭했을 때 """
            done = True
            reward = -1
        elif num_flag_tiles == self.MINES_COUNT:
            """ 깃발의 개수와 지뢰의 갯수가 같을 때 """
            done = True
            reward = 1.0
        elif flattened_player_field[action_pos] == 0:
            flattened_player_field = self.auto_reveal(action[0], action[1], flattened_player_field)
            num_flag_tiles = np.count_nonzero(flattened_player_field == "P")

            if num_flag_tiles == self.MINES_COUNT:
                done = True
                reward = 1.0
            else:
                done = False
                reward = 0.1
        else:
            done = False
            reward = 0.1

        updated_player_field = flattened_player_field.reshape(self.ROWS, self.COLUMNS)
        self.PLAYER_FIELD = updated_player_field
        self.DONE = done
        self.move_count += 1

        return updated_player_field, reward, done

    def print_field(self):
        for row in range(0, self.ROWS):
            for col in range(0, self.COLUMNS):
                print(self.PLAYER_FIELD[row, col], end=" ")
            print(" ")

    def print_grid(self):
        for row in range(0, self.ROWS):
            for col in range(0, self.COLUMNS):
                print(self.GRID[row, col], end=" ")
            print(" ")


if __name__ == "__main__":
    game = Minesweeper(9, 9, 10)
    game.print_grid()

    while not game.DONE:
        x = int(input('X축 입력 : '))
        y = int(input('Y축 입력 : '))

        game.step((x, y))
        game.print_field()
