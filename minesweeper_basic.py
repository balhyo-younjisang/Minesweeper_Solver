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
        self.BOARD_FIELD = self.init_board()  # 게임의 데이터 ( 지뢰의 위치, 근처의 지뢰 수 등 ) 을 저장하는 2차원 배열
        self.PLAYER_FIELD = self.init_game()  # 사용자에게 보여지는 화면을 저장하는 2차원 배열
        self.MOVE_COUNT = 0  # 사용자가 상호작용한 횟수
        
        self.won = 0  # 사용자가 게임에서 이긴 횟수
        self.lost = 0  # 사용자가 게임에서 진 횟수

    def init_board(self):
        """ 게임의 데이터를 저장하는 2차원 배열을 생성 후 초기화하여 리턴 """
        board = np.zeros((self.ROWS, self.COLUMNS), dtype=object)  # 데이터를 저장할 2차원 배열
        mines = self.MINES_COUNT  # 설치할 지뢰의 수

        while mines > 0:
            mine_row, mine_col = random.randint(0, self.ROWS - 1), random.randint(0, self.COLUMNS - 1)
            if board[mine_row][mine_col] != 'B':  # 지뢰의 위치가 중복되지 않은 경우에만 지뢰의 위치 저장
                board[mine_row][mine_col] = 'B'
                board = self.set_neighbors(mine_row, mine_col, board)
                mines -= 1

        return board

    def init_game(self):
        """ 사용자에게 보여지는 화면을 저장하는 2차우너 배열을 생성 후 초기화하여 리턴 """
        player_board = np.full((self.ROWS, self.COLUMNS),"U", dtype=object)

        return player_board

    def set_neighbors(self, mine_row, mine_col, board):
        """ 지뢰가 설치된 위치를 중심으로 3 x 3 구역에 1을 더하여 리턴 """
        for row in range(mine_row - 1, mine_row + 2):
            for col in range(mine_col - 1, mine_col + 2):
                if 0 <= row < self.ROWS and 0 <= col < self.COLUMNS and board[row][col] != 'B':
                    board[row][col] += 1

        return board

    def reset(self):
        """ 게임이 끝났을 때 다음 게임을 위해 초기화 """
        self.BOARD_FIELD = self.init_board()
        self.PLAYER_FIELD = self.init_game()
        self.MOVE_COUNT = 0
        action = np.ravel_multi_index((0, 0), (self.ROWS, self.COLUMNS))
        state = self.step(action)

        return state

    def step(self, action):
        """ 사용자가 상호작용 시 실행되는 함수 """
        flatten_board = self.BOARD_FIELD.flatten()  # 게임 데이터가 저장된 2차원 배열 평탄화
        flatten_player_field = self.PLAYER_FIELD.flatten()  # 사용자에게 보여지는 2차원 배열 평탄화
        count_hidden_tiles = np.count_nonzero(flatten_player_field == "U")  # 아직 제거되지 않은 타일을 수를 저장
    
        done = False
        reward = None

        if flatten_board[action] == "B":
            # 폭탄이 있는 타일을 제거하였을 때
            done = True
            reward = -1
            self.lost += 1
        elif count_hidden_tiles == self.MINES_COUNT:
            # 남아있는 제거되지 않은 타일의 개수가 지뢰의 갯수와 같을 때
            done = True
            reward = 1
            self.won += 1
        elif flatten_player_field[action] == 0:
            # 제거한 타일이 0일 때 연쇄적으로 주변 타일을 제거
            flatten_player_field = self.reveal_continuity(action, self.PLAYER_FIELD)

            count_hidden_tiles = np.count_nonzero(flatten_player_field == "U")
            if count_hidden_tiles == self.MINES_COUNT:
                done = True
                reward = 1
                self.won += 1
            else:
                done = False
                reward = 0.1
        else:
            done = False
            reward = 0.1
        
        # 변수 업데이트
        player_field = flatten_player_field.reshape(self.ROWS, self.COLUMNS)
        self.PLAYER_FIELD = player_field
        self.MOVE_COUNT += 1

        return player_field, reward, done

    def reveal_continuity(self, action, player_field):
        """ 연쇄적으로 주변 타일을 제거하는 함수"""
        x, y = np.unravel_index(action, (self.ROWS, self.COLUMNS))
        update_field = player_field.copy()

        for k in range(-1, 2):
            for h in range(-1, 2):
                x += k
                y += h

                if 0 <= x < self.ROWS and 0 <= y < self.COLUMNS:
                    if update_field[x, y] == "U" and self.BOARD_FIELD[x, y] != "B":
                        update_field[x, y] = self.BOARD_FIELD[x, y]

                        if self.BOARD_FIELD[x, y] == 0:
                            update_field = self.reveal_continuity((x, y), update_field)

        return update_field.flatten()

    def print_player_field(self):
        """ 플레이어가 현재 진행상황을 볼 수 있게 출력하는 함수 """
        for row in range(0, self.ROWS):
            for col in range(0, self.COLUMNS):
                print(self.PLAYER_FIELD[row, col], end=" ")
            print("")
