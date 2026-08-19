import pygame
import random
import time
import os
import math
from collections import deque
import physics

# Basic Colors
RED = (255, 50, 50)
GREEN = (50, 255, 50)
WHITE = (255, 255, 255)
ORANGE = (255, 165, 0)

# ------------------------------------------------------------
# Realistic Fruit Scaling
# ------------------------------------------------------------
FRUIT_SCALES = {
    "apple": (85, 85),
    "banana": (70, 110),
    "orange": (85, 85),
    "pineapple": (130, 160),
    "coconut": (120, 120),
    "watermelon": (150, 150)
}

HALF_SCALES = {
    "apple": (42, 85),
    "banana": (35, 110),
    "orange": (42, 85),
    "pineapple": (65, 160),
    "coconut": (60, 120),
    "watermelon": (75, 150)
}


class Blade:
    def __init__(self):
        # Stores (x, y, timestamp)
        self.points = deque(maxlen=20)
        self.color = (0, 255, 255)
        self.min_width = 5
        self.max_width = 25
        self.fade_speed = 5

    def update(self, x, y):
        current_time = time.time()
        self.points.append((x, y, current_time))

        while self.points:
            if current_time - self.points[0][2] > 0.15:
                self.points.popleft()
            else:
                break

    def draw(self, screen):
        if len(self.points) < 2:
            return

        points_list = list(self.points)

        for i in range(len(points_list) - 1):
            p1 = points_list[i]
            p2 = points_list[i + 1]

            ratio = i / len(points_list)
            width = int(self.min_width + (self.max_width - self.min_width) * ratio)

            start_pos = (p1[0], p1[1])
            end_pos = (p2[0], p2[1])

            pygame.draw.line(screen, self.color, start_pos, end_pos, width)
            pygame.draw.circle(screen, self.color, end_pos, width // 2)

    def get_segments(self):
        segments = []
        pts = list(self.points)

        for i in range(len(pts) - 1):
            segments.append(
                (
                    (pts[i][0], pts[i][1]),
                    (pts[i + 1][0], pts[i + 1][1])
                )
            )

        return segments


class Fruit(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, fruit_type=None):
        super().__init__()

        types = ["apple", "banana", "coconut", "orange", "pineapple", "watermelon"]

        if fruit_type is None:
            self.fruit_type = random.choice(types)
        else:
            self.fruit_type = fruit_type

        try:
            path = f"assets/fruits/{self.fruit_type}_small.png"

            if not os.path.exists(path):
                path = f"assets/fruits/{self.fruit_type}.png"

            raw_image = pygame.image.load(path).convert_alpha()

            target_size = FRUIT_SCALES.get(self.fruit_type, (85, 85))
            self.image = pygame.transform.scale(raw_image, target_size)

        except Exception as e:
            target_size = (85, 85)
            self.color = random.choice([RED, ORANGE, GREEN])
            self.image = pygame.Surface(target_size, pygame.SRCALPHA)
            pygame.draw.circle(
                self.image,
                self.color,
                (target_size[0] // 2, target_size[1] // 2),
                min(target_size) // 2
            )

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        # Slightly smaller hitbox for forgiving gameplay
        self.radius = min(self.rect.size) // 2 - 5

        self.screen_w = width
        self.screen_h = height

        # Physics
        self.pos_x = float(x)
        self.pos_y = float(y)

        # This prevents spawned fruits from being counted as missed immediately
        self.entered_screen = False

        # Stronger fullscreen physics
        self.gravity = 0.12

        # Choose a target height the fruit should reach on screen
        target_y = random.uniform(self.screen_h * 0.20, self.screen_h * 0.45)

        # Calculate launch speed needed to reach that height
        distance = max(150.0, self.pos_y - target_y)
        launch_speed = math.sqrt(2 * self.gravity * distance)

        self.vel_y = -launch_speed * random.uniform(0.95, 1.08)
        self.vel_x = random.uniform(-2.2, 2.2)

    def update(self):
        self.vel_y += self.gravity
        self.pos_x += self.vel_x
        self.pos_y += self.vel_y

        self.rect.centerx = int(self.pos_x)
        self.rect.centery = int(self.pos_y)

        # Mark fruit as entered once it is visible on screen
        if not self.entered_screen and self.rect.top < self.screen_h:
            self.entered_screen = True

        # Kill only after fully outside screen
        if (
            self.rect.top > self.screen_h + 220
            or self.rect.right < -120
            or self.rect.left > self.screen_w + 120
        ):
            self.kill()

    def check_slice(self, segments):
        center = (self.pos_x, self.pos_y)

        for p1, p2 in segments:
            if physics.check_capsule_circle_collision(
                p1,
                p2,
                15,
                center,
                self.radius
            ):
                return True

        return False


class SlicedFruit(pygame.sprite.Sprite):
    def __init__(self, x, y, fruit_type, half_id, screen_height=600):
        super().__init__()

        try:
            base = f"assets/fruits/{fruit_type}_half_{half_id}"
            path_small = f"{base}_small.png"
            path_large = f"{base}.png"

            path = path_small if os.path.exists(path_small) else path_large

            if os.path.exists(path):
                raw = pygame.image.load(path).convert_alpha()

                target_size = HALF_SCALES.get(fruit_type, (42, 85))
                self.image = pygame.transform.scale(raw, target_size)
            else:
                raise FileNotFoundError(f"Half image not found: {path}")

        except Exception as e:
            print(f"SlicedFruit load error for {fruit_type} half {half_id}: {e}")

            self.image = pygame.Surface((35, 35), pygame.SRCALPHA)
            pygame.draw.arc(self.image, GREEN, (0, 0, 35, 35), 0, 3.14, 20)

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        self.screen_h = screen_height

        # Physics to fly apart
        self.pos_x = float(x)
        self.pos_y = float(y)
        self.gravity = 0.14

        if half_id == 1:
            self.vel_x = random.uniform(-4, -1)
            self.angle_speed = 2
        else:
            self.vel_x = random.uniform(1, 4)
            self.angle_speed = -2

        self.vel_y = random.uniform(-3, -1)

        self.original_image = self.image
        self.angle = 0
        self.alpha = 255

    def update(self):
        self.vel_y += self.gravity
        self.pos_x += self.vel_x
        self.pos_y += self.vel_y

        self.angle += self.angle_speed

        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=(self.pos_x, self.pos_y))

        # Kill only after fully below screen
        if self.rect.top > self.screen_h + 80:
            self.kill()


class Bomb(Fruit):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "bomb")

        try:
            path = "assets/fruits/bomb_small.png"

            if not os.path.exists(path):
                path = "assets/fruits/bomb.png"

            self.image = pygame.image.load(path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (90, 90))

        except Exception as e:
            print(f"Bomb load error: {e}")
            self.image = pygame.Surface((90, 90), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (50, 50, 50), (45, 45), 45)
            pygame.draw.circle(self.image, RED, (45, 45), 10)

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.radius = self.rect.width // 2


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        try:
            path = "assets/vfx/explosion_small.png"

            if not os.path.exists(path):
                path = "assets/vfx/explosion.png"

            self.image = pygame.image.load(path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (150, 150))

        except Exception:
            self.image = pygame.Surface((100, 100))
            self.image.fill(RED)

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.timer = 30
        self.original_image = self.image

    def update(self):
        self.timer -= 1

        alpha = int((self.timer / 30) * 255)
        self.image.set_alpha(alpha)

        if self.timer <= 0:
            self.kill()


class SplashEffect(pygame.sprite.Sprite):
    FRUIT_SPLASH_MAP = {
        "apple": "red",
        "watermelon": "red",
        "banana": "yellow",
        "pineapple": "yellow",
        "orange": "orange",
        "coconut": "transparent"
    }

    def __init__(self, x, y, fruit_type, velocity=0):
        super().__init__()

        splash_color = self.FRUIT_SPLASH_MAP.get(fruit_type, "transparent")

        if velocity > 400:
            size_variant = ""
            scale_size = (180, 180)
        else:
            size_variant = "_small"
            scale_size = (120, 120)

        try:
            path = f"assets/vfx/splash_{splash_color}{size_variant}.png"

            if not os.path.exists(path):
                path = f"assets/vfx/splash_{splash_color}_small.png"
                scale_size = (120, 120)

            raw_image = pygame.image.load(path).convert_alpha()
            self.image = pygame.transform.scale(raw_image, scale_size)
            self.original_image = self.image.copy()

        except Exception:
            self.image = pygame.Surface((100, 100), pygame.SRCALPHA)

            color_map = {
                "red": (255, 50, 50),
                "yellow": (255, 255, 50),
                "orange": (255, 165, 0)
            }

            color = color_map.get(splash_color, (200, 200, 200))
            pygame.draw.circle(self.image, (*color, 150), (50, 50), 50)
            self.original_image = self.image.copy()

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        self.lifetime = 20
        self.age = 0

        angle = random.randint(-15, 15)
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.age += 1

        alpha = int(255 * (1 - self.age / self.lifetime))

        if alpha < 0:
            alpha = 0

        self.image = self.original_image.copy()
        self.image.set_alpha(alpha)

        if self.age >= self.lifetime:
            self.kill()