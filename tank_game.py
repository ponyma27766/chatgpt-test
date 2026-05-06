"""简单的 Tkinter 坦克大战小游戏。

运行：
    python tank_game.py

操作：
    方向键移动坦克
    空格键发射子弹
"""

from __future__ import annotations

import random
import tkinter as tk
from dataclasses import dataclass


WIDTH = 800
HEIGHT = 600
TANK_SIZE = 28
ENEMY_SIZE = 26
BULLET_SIZE = 6
PLAYER_SPEED = 5
ENEMY_SPEED = 2
BULLET_SPEED = 9
ENEMY_FIRE_CHANCE = 0.012
TARGET_FPS_MS = 16  # ~60 FPS


@dataclass
class Bullet:
    x: float
    y: float
    dx: float
    dy: float
    owner: str
    alive: bool = True

    def update(self) -> None:
        self.x += self.dx
        self.y += self.dy
        if self.x < -BULLET_SIZE or self.x > WIDTH + BULLET_SIZE:
            self.alive = False
        if self.y < -BULLET_SIZE or self.y > HEIGHT + BULLET_SIZE:
            self.alive = False

    def rect(self) -> tuple[float, float, float, float]:
        half = BULLET_SIZE / 2
        return (self.x - half, self.y - half, self.x + half, self.y + half)


@dataclass
class Tank:
    x: float
    y: float
    direction: tuple[int, int]
    speed: int
    alive: bool = True

    def move(self, dx: int, dy: int) -> None:
        self.direction = (dx, dy)
        self.x = min(max(self.x + dx * self.speed, TANK_SIZE / 2), WIDTH - TANK_SIZE / 2)
        self.y = min(max(self.y + dy * self.speed, TANK_SIZE / 2), HEIGHT - TANK_SIZE / 2)

    def rect(self, size: int) -> tuple[float, float, float, float]:
        half = size / 2
        return (self.x - half, self.y - half, self.x + half, self.y + half)


class TankGame:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("坦克大战")

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#1f1f1f")
        self.canvas.pack()

        self.info_var = tk.StringVar(value="分数: 0")
        tk.Label(root, textvariable=self.info_var, font=("Arial", 12)).pack(fill="x")

        self.player = Tank(WIDTH / 2, HEIGHT - 60, (0, -1), PLAYER_SPEED)
        self.enemies: list[Tank] = []
        self.bullets: list[Bullet] = []
        self.keys: set[str] = set()
        self.score = 0
        self.running = True

        self.spawn_wave(6)

        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind("<KeyRelease>", self.on_key_release)

        self.loop()

    def spawn_wave(self, count: int) -> None:
        for _ in range(count):
            x = random.randint(40, WIDTH - 40)
            y = random.randint(40, HEIGHT // 3)
            self.enemies.append(Tank(x, y, (0, 1), ENEMY_SPEED))

    def on_key_press(self, event: tk.Event) -> None:
        key = event.keysym
        self.keys.add(key)
        if key == "space" and self.player.alive and self.running:
            self.fire(self.player, "player")
        if key.lower() == "r" and not self.running:
            self.restart()

    def on_key_release(self, event: tk.Event) -> None:
        self.keys.discard(event.keysym)

    def fire(self, tank: Tank, owner: str) -> None:
        dx, dy = tank.direction
        if dx == 0 and dy == 0:
            dy = -1 if owner == "player" else 1
        self.bullets.append(
            Bullet(
                x=tank.x + dx * (TANK_SIZE // 2),
                y=tank.y + dy * (TANK_SIZE // 2),
                dx=dx * BULLET_SPEED,
                dy=dy * BULLET_SPEED,
                owner=owner,
            )
        )

    def update_player(self) -> None:
        if not self.player.alive:
            return
        dx = ("Right" in self.keys) - ("Left" in self.keys)
        dy = ("Down" in self.keys) - ("Up" in self.keys)
        if dx != 0 or dy != 0:
            self.player.move(dx, dy)

    def update_enemies(self) -> None:
        for enemy in self.enemies:
            if not enemy.alive:
                continue
            if random.random() < 0.03:
                enemy.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            dx, dy = enemy.direction
            enemy.move(dx, dy)

            # 敌方随机开火
            if random.random() < ENEMY_FIRE_CHANCE:
                self.fire(enemy, "enemy")

    @staticmethod
    def overlaps(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> bool:
        return not (a[2] < b[0] or a[0] > b[2] or a[3] < b[1] or a[1] > b[3])

    def handle_collisions(self) -> None:
        player_rect = self.player.rect(TANK_SIZE)
        for bullet in self.bullets:
            if not bullet.alive:
                continue
            brect = bullet.rect()
            if bullet.owner == "player":
                for enemy in self.enemies:
                    if enemy.alive and self.overlaps(brect, enemy.rect(ENEMY_SIZE)):
                        enemy.alive = False
                        bullet.alive = False
                        self.score += 10
                        break
            else:
                if self.player.alive and self.overlaps(brect, player_rect):
                    self.player.alive = False
                    bullet.alive = False
                    self.running = False

        # 清理死亡对象
        self.enemies = [e for e in self.enemies if e.alive]
        self.bullets = [b for b in self.bullets if b.alive]

        if not self.enemies and self.running:
            self.spawn_wave(6)

    def draw(self) -> None:
        self.canvas.delete("all")

        if self.player.alive:
            self.draw_tank(self.player, TANK_SIZE, "#00d26a")

        for enemy in self.enemies:
            self.draw_tank(enemy, ENEMY_SIZE, "#ff5f5f")

        for bullet in self.bullets:
            x1, y1, x2, y2 = bullet.rect()
            color = "#ffd166" if bullet.owner == "player" else "#f94144"
            self.canvas.create_oval(x1, y1, x2, y2, fill=color, outline="")

        self.info_var.set(f"分数: {self.score}  |  剩余敌人: {len(self.enemies)}")

        if not self.running:
            self.canvas.create_text(
                WIDTH / 2,
                HEIGHT / 2,
                text="游戏结束\n按 R 重新开始",
                fill="white",
                font=("Arial", 28, "bold"),
                justify="center",
            )

    def draw_tank(self, tank: Tank, size: int, color: str) -> None:
        x1, y1, x2, y2 = tank.rect(size)
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#111", width=2)

        dx, dy = tank.direction
        if dx == 0 and dy == 0:
            dy = -1
        barrel_len = size * 0.7
        self.canvas.create_line(
            tank.x,
            tank.y,
            tank.x + dx * barrel_len,
            tank.y + dy * barrel_len,
            fill="#222",
            width=4,
        )

    def loop(self) -> None:
        if self.running:
            self.update_player()
            self.update_enemies()

            for bullet in self.bullets:
                bullet.update()

            self.handle_collisions()

        self.draw()
        self.root.after(TARGET_FPS_MS, self.loop)

    def restart(self) -> None:
        self.player = Tank(WIDTH / 2, HEIGHT - 60, (0, -1), PLAYER_SPEED)
        self.enemies.clear()
        self.bullets.clear()
        self.score = 0
        self.running = True
        self.spawn_wave(6)


def main() -> None:
    root = tk.Tk()
    TankGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
