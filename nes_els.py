import pygame
import random
import time
import math
from pygame.locals import *

# 初始化 Pygame
pygame.init()

# 设置屏幕大小
WIDTH, HEIGHT = 600, 920
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("俄罗斯方块")

# 定义游戏网格的行列数
GRID_WIDTH, GRID_HEIGHT = 24, 37
BLOCK_SIZE = 25

# 定义颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
PINK = (255, 192, 203)

# 俄罗斯方块的形状
SHAPES = [
    [[1, 1, 1, 1]],  # I 形状
    [[1, 1], [1, 1]],  # O 形状
    [[0, 1, 0], [1, 1, 1]],  # T 形状
    [[1, 0, 0], [1, 1, 1]],  # L 形状
    [[0, 0, 1], [1, 1, 1]],  # J 形状
    [[1, 1, 0], [0, 1, 1]],  # S 形状
    [[0, 1, 1], [1, 1, 0]]  # Z 形状
]

SHAPE_COLORS = [CYAN, YELLOW, MAGENTA, BLUE, GREEN, RED, WHITE]


class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = random.choice([RED, GREEN, BLUE, YELLOW, MAGENTA, CYAN, ORANGE, PINK])
        self.size = random.randint(2, 5)
        self.speed = random.uniform(2, 8)
        self.angle = random.uniform(0, math.pi * 2)
        self.life = random.uniform(0.5, 1.5)
        self.age = 0

    def update(self, dt):
        self.x += math.cos(self.angle) * self.speed * dt * 60
        self.y += math.sin(self.angle) * self.speed * dt * 60
        self.speed *= 0.98
        self.age += dt
        return self.age < self.life

    def draw(self, surface):
        alpha = int(255 * (1 - self.age / self.life))
        color = (self.color[0], self.color[1], self.color[2], alpha)
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, color, (self.size, self.size), self.size)
        surface.blit(s, (int(self.x - self.size), int(self.y - self.size)))


class Fireworks:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.particles = []
        self.active = False
        self.start_time = 0
        self.duration = 5  # 烟花持续5秒

    def add_firework(self, x=None, y=None):
        if x is None:
            x = random.randint(50, self.width - 50)
        if y is None:
            y = random.randint(50, self.height - 50)

        for _ in range(random.randint(50, 100)):
            self.particles.append(Particle(x, y))

    def trigger(self):
        self.active = True
        self.start_time = time.time()
        # 添加多个烟花位置
        for _ in range(20):
            self.add_firework(
                random.randint(100, self.width - 100),
                random.randint(100, self.height - 100))

    def update(self, dt):
        if self.active:
            # 如果持续时间结束，清除所有粒子
            if time.time() - self.start_time > self.duration:
                self.particles = []
                self.active = False
            else:
                # 在持续时间内随机添加新烟花
                if random.random() < 0.1:
                    self.add_firework()

        self.particles = [p for p in self.particles if p.update(dt)]

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)


class Tetris:
    def __init__(self):
        self.board = [[BLACK] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
        self.game_over = False
        self.current_shape = None
        self.shape_position = (0, 0)
        self.last_drop_time = time.time()
        self.last_move_time = time.time()
        self.drop_interval = 0.5
        self.fast_drop_interval = 0.5 / 15
        # 将左右移动间隔时间增加一倍（放慢移动速度）
        self.move_interval = 0.2  # 原为0.1
        self.fast_move_interval = 0.1  # 原为0.05
        self.keys_pressed = {}
        self.score = 0
        self.score_font = pygame.font.SysFont('Arial', 40, bold=True)
        self.reward_font = pygame.font.SysFont('Arial', 30)
        self.big_reward_font = pygame.font.SysFont('Arial', 60, bold=True)
        self.reward_effect = False
        self.reward_start_time = 0
        self.reward_colors = [RED, GREEN, BLUE, YELLOW, MAGENTA, CYAN, ORANGE, PURPLE, PINK]
        self.reward_text = ""
        self.fireworks = Fireworks(WIDTH, HEIGHT)
        self.last_score_check = 0

    def new_shape(self):
        shape_index = random.randint(0, len(SHAPES) - 1)
        self.current_shape = SHAPES[shape_index]
        self.shape_color = SHAPE_COLORS[shape_index]
        self.shape_position = (GRID_WIDTH // 2 - len(self.current_shape[0]) // 2, 0)

    def rotate_shape(self):
        self.current_shape = [list(row) for row in zip(*self.current_shape[::-1])]

    def check_collision(self):
        x, y = self.shape_position
        for i, row in enumerate(self.current_shape):
            for j, cell in enumerate(row):
                if cell:
                    if x + j < 0 or x + j >= GRID_WIDTH or y + i >= GRID_HEIGHT or self.board[y + i][x + j] != BLACK:
                        return True
        return False

    def place_shape(self):
        x, y = self.shape_position
        for i, row in enumerate(self.current_shape):
            for j, cell in enumerate(row):
                if cell:
                    self.board[y + i][x + j] = self.shape_color

    def clear_lines(self):
        new_board = [row for row in self.board if any(cell == BLACK for cell in row)]
        lines_cleared = (GRID_HEIGHT - len(new_board))
        self.board = [[BLACK] * GRID_WIDTH for _ in range(lines_cleared)] + new_board

        if lines_cleared > 0:
            # 得分放大10倍
            score_to_add = 0
            if lines_cleared == 1:
                score_to_add = 100 * 10  # 原为100，现为1000
            elif lines_cleared == 2:
                score_to_add = 300 * 10  # 原为300，现为3000
            elif lines_cleared == 3:
                score_to_add = 500 * 10  # 原为500，现为5000
            elif lines_cleared >= 4:
                score_to_add = 800 * 10 * (lines_cleared - 3)  # 原为800，现为8000

            self.score += score_to_add

            # 检查是否触发奖励特效
            prev_score = self.score - score_to_add
            if prev_score < 10000 <= self.score:  # 原为1000，现为10000
                self.reward_effect = True
                self.reward_start_time = time.time()
                self.reward_text = "真棒!"
            elif prev_score < 50000 <= self.score:  # 原为5000，现为50000
                self.reward_effect = True
                self.reward_start_time = time.time()
                self.reward_text = "真了不起!"
            elif prev_score < 100000 <= self.score:  # 原为10000，现为100000
                self.reward_effect = True
                self.reward_start_time = time.time()
                self.reward_text = "哇哦......好崇拜你啊"
                self.fireworks.trigger()  # 触发烟花效果

            # 每次清除3行或以上时有30%概率触发烟花
            if lines_cleared >= 3 and random.random() < 0.3:
                self.fireworks.trigger()

    def move_left(self):
        self.shape_position = (self.shape_position[0] - 1, self.shape_position[1])
        if self.check_collision():
            self.shape_position = (self.shape_position[0] + 1, self.shape_position[1])

    def move_right(self):
        self.shape_position = (self.shape_position[0] + 1, self.shape_position[1])
        if self.check_collision():
            self.shape_position = (self.shape_position[0] - 1, self.shape_position[1])

    def move_down(self, hard_drop=False):
        if hard_drop:
            y = self.shape_position[1]
            while True:
                y += 1
                self.shape_position = (self.shape_position[0], y)
                if self.check_collision():
                    y -= 1
                    break
            self.shape_position = (self.shape_position[0], y)
            self.place_shape()
            self.clear_lines()
            self.new_shape()
            if self.check_collision():
                self.game_over = True
        else:
            self.shape_position = (self.shape_position[0], self.shape_position[1] + 1)
            if self.check_collision():
                self.shape_position = (self.shape_position[0], self.shape_position[1] - 1)
                self.place_shape()
                self.clear_lines()
                self.new_shape()
                if self.check_collision():
                    self.game_over = True


def main():
    clock = pygame.time.Clock()
    game = Tetris()
    game.new_shape()

    while not game.game_over:
        dt = clock.tick(60) / 1000.0
        current_time = time.time()

        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.game_over = True
            elif event.type == pygame.KEYDOWN:
                game.keys_pressed[event.key] = True
                if event.key == pygame.K_LEFT:
                    game.move_left()
                    game.last_move_time = current_time
                elif event.key == pygame.K_RIGHT:
                    game.move_right()
                    game.last_move_time = current_time
                elif event.key == pygame.K_DOWN:
                    game.move_down()
                    game.last_drop_time = current_time
                elif event.key == pygame.K_UP:
                    game.rotate_shape()
                elif event.key == pygame.K_SPACE:
                    game.move_down(hard_drop=True)
                    game.last_drop_time = current_time
            elif event.type == pygame.KEYUP:
                if event.key in game.keys_pressed:
                    del game.keys_pressed[event.key]

        # 处理持续按键
        move_now = False
        if current_time - game.last_move_time > (
                game.fast_move_interval if any(
                    k in game.keys_pressed for k in [K_LEFT, K_RIGHT]) else game.move_interval):
            move_now = True
            game.last_move_time = current_time

        if K_LEFT in game.keys_pressed and move_now:
            game.move_left()
        if K_RIGHT in game.keys_pressed and move_now:
            game.move_right()

        # 自动下落
        drop_interval = game.fast_drop_interval if K_DOWN in game.keys_pressed else game.drop_interval
        if current_time - game.last_drop_time > drop_interval:
            game.move_down()
            game.last_drop_time = current_time

        # 更新烟花
        game.fireworks.update(dt)

        # 绘制
        screen.fill(BLACK)

        # 绘制游戏板
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                pygame.draw.rect(screen, game.board[y][x],
                                 (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

        # 绘制当前方块
        x, y = game.shape_position
        for i, row in enumerate(game.current_shape):
            for j, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, game.shape_color,
                                     ((x + j) * BLOCK_SIZE, (y + i) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

        # 绘制烟花
        game.fireworks.draw(screen)

        # 绘制得分
        score_text = game.score_font.render(f"得分: {game.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(WIDTH // 2, 30))
        screen.blit(score_text, score_rect)

        # 绘制奖励特效
        if game.reward_effect:
            if time.time() - game.reward_start_time < 5:  # 显示5秒
                # 彩色闪烁效果
                color_index = int((time.time() - game.reward_start_time) * 10) % len(game.reward_colors)
                if game.score >= 100000:
                    reward_surface = game.big_reward_font.render(game.reward_text, True,
                                                                 game.reward_colors[color_index])
                else:
                    reward_surface = game.reward_font.render(game.reward_text, True, game.reward_colors[color_index])
                text_rect = reward_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                screen.blit(reward_surface, text_rect)
            else:
                game.reward_effect = False

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()