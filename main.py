from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color, PushMatrix, PopMatrix, Rotate
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.properties import NumericProperty, ListProperty, BooleanProperty
import random
import time
import math

# 游戏常量
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
COLORS = [
    [0, 255, 255],  # I - 青色
    [255, 255, 0],  # O - 黄色
    [255, 0, 255],  # T - 紫色
    [255, 165, 0],  # L - 橙色
    [0, 0, 255],  # J - 蓝色
    [0, 255, 0],  # S - 绿色
    [255, 0, 0]  # Z - 红色
]

SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 0, 0], [1, 1, 1]],  # L
    [[0, 0, 1], [1, 1, 1]],  # J
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]]  # Z
]


class TetrisBlock(Widget):
    color = ListProperty([1, 1, 1])

    def __init__(self, x, y, color, **kwargs):
        super().__init__(**kwargs)
        self.pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
        self.size = (BLOCK_SIZE, BLOCK_SIZE)
        self.color = color
        with self.canvas:
            Color(*self.color)
            self.rect = Rectangle(pos=self.pos, size=self.size)


class TetrisGame(Widget):
    score = NumericProperty(0)
    game_over = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.board = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_shape = []
        self.current_color = []
        self.shape_pos = [0, 0]
        self.next_shape = random.randint(0, 6)
        self.last_drop = time.time()
        self.drop_interval = 0.5
        self.setup_ui()
        self.new_shape()

    def setup_ui(self):
        # 游戏区域边框
        with self.canvas:
            Color(0.5, 0.5, 0.5)
            Rectangle(pos=(0, 0), size=(GRID_WIDTH * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE))

        # 分数显示
        self.score_label = Label(
            text=f"Score: {self.score}",
            pos=(GRID_WIDTH * BLOCK_SIZE + 20, GRID_HEIGHT * BLOCK_SIZE - 50),
            font_size='20sp'
        )
        self.add_widget(self.score_label)

    def new_shape(self):
        shape_idx = self.next_shape
        self.next_shape = random.randint(0, 6)
        self.current_shape = SHAPES[shape_idx]
        self.current_color = [c / 255 for c in COLORS[shape_idx]]  # 转换到Kivy的0-1颜色范围
        self.shape_pos = [GRID_WIDTH // 2 - len(self.current_shape[0]) // 2, GRID_HEIGHT - 1]

        if self.check_collision():
            self.game_over = True

    def check_collision(self):
        for y, row in enumerate(self.current_shape):
            for x, cell in enumerate(row):
                if cell:
                    board_x = self.shape_pos[0] + x
                    board_y = self.shape_pos[1] - y
                    if (board_x < 0 or board_x >= GRID_WIDTH or
                            board_y < 0 or
                            (board_y < GRID_HEIGHT and self.board[board_y][board_x])):
                        return True
        return False

    def rotate_shape(self):
        rotated = [list(row) for row in zip(*self.current_shape[::-1])]
        old_shape = self.current_shape
        self.current_shape = rotated
        if self.check_collision():
            self.current_shape = old_shape

    def move_left(self):
        self.shape_pos[0] -= 1
        if self.check_collision():
            self.shape_pos[0] += 1

    def move_right(self):
        self.shape_pos[0] += 1
        if self.check_collision():
            self.shape_pos[0] -= 1

    def move_down(self):
        self.shape_pos[1] -= 1
        if self.check_collision():
            self.shape_pos[1] += 1
            self.lock_shape()
            return True
        return False

    def lock_shape(self):
        for y, row in enumerate(self.current_shape):
            for x, cell in enumerate(row):
                if cell:
                    board_y = self.shape_pos[1] - y
                    if 0 <= board_y < GRID_HEIGHT:
                        block = TetrisBlock(
                            self.shape_pos[0] + x,
                            board_y,
                            self.current_color
                        )
                        self.add_widget(block)
                        self.board[board_y][self.shape_pos[0] + x] = block
        self.clear_lines()
        self.new_shape()

    def clear_lines(self):
        lines_cleared = 0
        for y in range(GRID_HEIGHT):
            if all(self.board[y]):
                lines_cleared += 1
                # 移除该行所有方块
                for x in range(GRID_WIDTH):
                    self.remove_widget(self.board[y][x])
                    self.board[y][x] = None
                # 下移上方行
                for yy in range(y + 1, GRID_HEIGHT):
                    for x in range(GRID_WIDTH):
                        if self.board[yy][x]:
                            self.board[yy][x].y -= BLOCK_SIZE
                            self.board[yy - 1][x] = self.board[yy][x]
                            self.board[yy][x] = None

        # 计分
        if lines_cleared == 1:
            self.score += 100
        elif lines_cleared == 2:
            self.score += 300
        elif lines_cleared == 3:
            self.score += 500
        elif lines_cleared >= 4:
            self.score += 800

        self.score_label.text = f"Score: {self.score}"

    def update(self, dt):
        if self.game_over:
            return

        if time.time() - self.last_drop > self.drop_interval:
            if self.move_down():
                self.last_drop = time.time()

    def on_touch_down(self, touch):
        if self.game_over:
            return True

        if touch.x < self.width / 3:
            self.move_left()
        elif touch.x > 2 * self.width / 3:
            self.move_right()
        else:
            self.rotate_shape()
        return True


class TetrisApp(App):
    def build(self):
        game = TetrisGame()
        Window.size = (GRID_WIDTH * BLOCK_SIZE + 200, GRID_HEIGHT * BLOCK_SIZE)
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game


if __name__ == "__main__":
    TetrisApp().run()