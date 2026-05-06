import math
import random
import tkinter as tk

WIDTH, HEIGHT = 900, 600
PLAYER_SPEED = 4
BULLET_SPEED = 8
ENEMY_SPEED = 1.8


class TankBattleGame:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("坦克大战（Tkinter 版）")
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#1f2a1f")
        self.canvas.pack()

        self.keys = set()
        self.game_over = False
        self.score = 0

        self.player = {
            "x": WIDTH / 2,
            "y": HEIGHT - 80,
            "angle": -90,
            "hp": 5,
            "cooldown": 0,
        }

        self.enemies = []
        self.player_bullets = []
        self.enemy_bullets = []
        self.walls = []

        self._spawn_walls()
        for _ in range(5):
            self._spawn_enemy()

        self.root.bind("<KeyPress>", self._on_key_down)
        self.root.bind("<KeyRelease>", self._on_key_up)

        self.loop()

    def _spawn_walls(self):
        for _ in range(12):
            w, h = random.randint(50, 110), random.randint(30, 70)
            x = random.randint(40, WIDTH - w - 40)
            y = random.randint(80, HEIGHT - h - 180)
            self.walls.append((x, y, x + w, y + h))

    def _spawn_enemy(self):
        self.enemies.append(
            {
                "x": random.randint(60, WIDTH - 60),
                "y": random.randint(60, HEIGHT // 2),
                "angle": random.choice([0, 90, 180, 270]),
                "hp": 2,
                "cooldown": random.randint(20, 80),
                "dir_timer": random.randint(30, 100),
            }
        )

    def _on_key_down(self, event):
        self.keys.add(event.keysym.lower())

    def _on_key_up(self, event):
        self.keys.discard(event.keysym.lower())

    def _shoot(self, source, bullet_list, speed, color):
        rad = math.radians(source["angle"])
        bx = source["x"] + math.cos(rad) * 20
        by = source["y"] + math.sin(rad) * 20
        bullet_list.append({"x": bx, "y": by, "vx": math.cos(rad) * speed, "vy": math.sin(rad) * speed, "c": color})

    def _circle_hits_wall(self, x, y, r=12):
        for x1, y1, x2, y2 in self.walls:
            if x1 - r <= x <= x2 + r and y1 - r <= y <= y2 + r:
                return True
        return False

    def _update_player(self):
        p = self.player
        if "left" in self.keys or "a" in self.keys:
            p["angle"] -= 4
        if "right" in self.keys or "d" in self.keys:
            p["angle"] += 4

        nx, ny = p["x"], p["y"]
        rad = math.radians(p["angle"])
        if "up" in self.keys or "w" in self.keys:
            nx += math.cos(rad) * PLAYER_SPEED
            ny += math.sin(rad) * PLAYER_SPEED
        if "down" in self.keys or "s" in self.keys:
            nx -= math.cos(rad) * PLAYER_SPEED
            ny -= math.sin(rad) * PLAYER_SPEED

        nx = min(max(25, nx), WIDTH - 25)
        ny = min(max(25, ny), HEIGHT - 25)

        if not self._circle_hits_wall(nx, ny):
            p["x"], p["y"] = nx, ny

        if p["cooldown"] > 0:
            p["cooldown"] -= 1

        if ("space" in self.keys or "j" in self.keys) and p["cooldown"] == 0:
            self._shoot(p, self.player_bullets, BULLET_SPEED, "#9ad0ff")
            p["cooldown"] = 12

    def _update_enemies(self):
        for e in self.enemies:
            e["dir_timer"] -= 1
            if e["dir_timer"] <= 0:
                e["angle"] += random.choice([-90, 0, 90, 180])
                e["dir_timer"] = random.randint(25, 90)

            # 轻度追踪玩家
            if random.random() < 0.02:
                dx = self.player["x"] - e["x"]
                dy = self.player["y"] - e["y"]
                e["angle"] = math.degrees(math.atan2(dy, dx))

            ex = e["x"] + math.cos(math.radians(e["angle"])) * ENEMY_SPEED
            ey = e["y"] + math.sin(math.radians(e["angle"])) * ENEMY_SPEED
            if 20 < ex < WIDTH - 20 and 20 < ey < HEIGHT - 20 and not self._circle_hits_wall(ex, ey):
                e["x"], e["y"] = ex, ey
            else:
                e["angle"] += random.choice([90, -90, 180])

            if e["cooldown"] > 0:
                e["cooldown"] -= 1
            else:
                if random.random() < 0.06:
                    self._shoot(e, self.enemy_bullets, BULLET_SPEED - 2, "#ff9f9f")
                    e["cooldown"] = random.randint(40, 100)

    def _update_bullets(self):
        def step(bullets):
            kept = []
            for b in bullets:
                b["x"] += b["vx"]
                b["y"] += b["vy"]
                if 0 <= b["x"] <= WIDTH and 0 <= b["y"] <= HEIGHT and not self._circle_hits_wall(b["x"], b["y"], 3):
                    kept.append(b)
            return kept

        self.player_bullets = step(self.player_bullets)
        self.enemy_bullets = step(self.enemy_bullets)

    def _collisions(self):
        # 玩家子弹打敌人
        kept_bullets = []
        for b in self.player_bullets:
            hit = False
            for e in self.enemies:
                if (b["x"] - e["x"]) ** 2 + (b["y"] - e["y"]) ** 2 < 22 ** 2:
                    e["hp"] -= 1
                    hit = True
                    if e["hp"] <= 0:
                        self.score += 1
                    break
            if not hit:
                kept_bullets.append(b)
        self.player_bullets = kept_bullets
        self.enemies = [e for e in self.enemies if e["hp"] > 0]

        while len(self.enemies) < 5:
            self._spawn_enemy()

        # 敌人子弹打玩家
        kept_enemy_bullets = []
        for b in self.enemy_bullets:
            if (b["x"] - self.player["x"]) ** 2 + (b["y"] - self.player["y"]) ** 2 < 22 ** 2:
                self.player["hp"] -= 1
                if self.player["hp"] <= 0:
                    self.game_over = True
            else:
                kept_enemy_bullets.append(b)
        self.enemy_bullets = kept_enemy_bullets

    def _draw_tank(self, x, y, angle, body_color, barrel_color):
        self.canvas.create_oval(x - 18, y - 18, x + 18, y + 18, fill=body_color, outline="black", width=2)
        rad = math.radians(angle)
        bx = x + math.cos(rad) * 26
        by = y + math.sin(rad) * 26
        self.canvas.create_line(x, y, bx, by, fill=barrel_color, width=6)

    def _render(self):
        self.canvas.delete("all")

        for x1, y1, x2, y2 in self.walls:
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="#57614f", outline="#2e352a", width=2)

        self._draw_tank(self.player["x"], self.player["y"], self.player["angle"], "#4ea8de", "#dff3ff")

        for e in self.enemies:
            self._draw_tank(e["x"], e["y"], e["angle"], "#e76f51", "#ffd8cc")

        for b in self.player_bullets + self.enemy_bullets:
            self.canvas.create_oval(b["x"] - 3, b["y"] - 3, b["x"] + 3, b["y"] + 3, fill=b["c"], outline="")

        self.canvas.create_text(10, 10, anchor="nw", fill="white", font=("Arial", 15, "bold"),
                                text=f"分数: {self.score}   生命: {self.player['hp']}")

        if self.game_over:
            self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="black", stipple="gray50")
            self.canvas.create_text(WIDTH / 2, HEIGHT / 2 - 20, fill="#ffdddd", font=("Arial", 36, "bold"),
                                    text="游戏结束")
            self.canvas.create_text(WIDTH / 2, HEIGHT / 2 + 30, fill="white", font=("Arial", 16),
                                    text="按 R 重新开始，按 Esc 退出")

    def _restart(self):
        self.score = 0
        self.player.update({"x": WIDTH / 2, "y": HEIGHT - 80, "angle": -90, "hp": 5, "cooldown": 0})
        self.enemies.clear()
        self.player_bullets.clear()
        self.enemy_bullets.clear()
        for _ in range(5):
            self._spawn_enemy()
        self.game_over = False

    def loop(self):
        if "escape" in self.keys:
            self.root.destroy()
            return

        if self.game_over:
            if "r" in self.keys:
                self._restart()
        else:
            self._update_player()
            self._update_enemies()
            self._update_bullets()
            self._collisions()

        self._render()
        self.root.after(16, self.loop)


if __name__ == "__main__":
    root = tk.Tk()
    TankBattleGame(root)
    root.mainloop()
