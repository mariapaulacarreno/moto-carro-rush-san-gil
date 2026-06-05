import pygame
import random
from pathlib import Path

ASSET_DIR = Path(__file__).resolve().parents[1] / "assets" / "images"


def load_image(name, size=None):
    path = ASSET_DIR / name
    try:
        image = pygame.image.load(path).convert_alpha()
        if size:
            image = pygame.transform.smoothscale(image, size)
        return image
    except Exception:
        width, height = size if size else (60, 60)
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        if "coin" in name:
            pygame.draw.circle(surface, (255, 215, 0), (width // 2, height // 2), min(width, height) // 2)
            pygame.draw.circle(surface, (255, 255, 255), (width // 2, height // 2), min(width, height) // 2, 3)
        elif "hole" in name or "hueco" in name:
            pygame.draw.ellipse(surface, (35, 35, 35), surface.get_rect())
            pygame.draw.ellipse(surface, (70, 70, 70), surface.get_rect(), 4)
        else:
            surface.fill((50, 120, 200))
        return surface


class GameObject(pygame.sprite.Sprite):
    def __init__(self, image, x, y, speed):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

    def update(self, dt):
        self.rect.y += self.speed * dt
        if self.rect.top > 900:
            self.kill()


class Player(GameObject):
    def __init__(self, x, y):
        image = load_image("motocarro.png", (80, 120))
        super().__init__(image, x, y, speed=0)
        self.move_speed = 360
        self.lives = 3
        self.gas = 100
        self.score = 0

    def update(self, dt, keys, screen_width):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.move_speed * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.move_speed * dt
        self.rect.x = max(0, min(self.rect.x, screen_width - self.rect.width))


class Obstacle(GameObject):
    def __init__(self, x, y, speed, kind="hole"):
        if kind == "hole":
            image = load_image("hole.png", (90, 40))
        else:
            image = load_image("obstacle.png", (70, 70))
        super().__init__(image, x, y, speed)
        self.kind = kind


class Coin(GameObject):
    def __init__(self, x, y, speed):
        image = load_image("coin.png", (40, 40))
        super().__init__(image, x, y, speed)


def random_obstacle(screen_width, min_speed=180, max_speed=260):
    x = random.randint(50, screen_width - 50)
    kind = random.choice(["hole", "obstacle"])
    speed = random.uniform(min_speed, max_speed)
    return Obstacle(x, -60, speed, kind=kind)


def random_coin(screen_width, min_speed=160, max_speed=220):
    x = random.randint(40, screen_width - 40)
    speed = random.uniform(min_speed, max_speed)
    return Coin(x, -40, speed)
