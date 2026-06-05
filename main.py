import pygame
import random
import sys
from pathlib import Path

from src.classes import Player, random_obstacle, random_coin

# --- Constantes ---
SCREEN_WIDTH = 540
SCREEN_HEIGHT = 900
ASSET_DIR = Path("assets") / "images"
SOUND_DIR = Path("assets") / "sounds"
BACKGROUND_FILE = "background.png"


def draw_text(surface, text, size, x, y, color=(255, 255, 255)):
    font = pygame.font.SysFont(None, size)
    rendered = font.render(text, True, color)
    surface.blit(rendered, (x, y))


def draw_hud(screen, player, level):
    draw_text(screen, f"Vidas: {player.lives}", 28, 16, 12)
    draw_text(screen, f"Nivel: {level}", 28, SCREEN_WIDTH - 150, 12)
    draw_text(screen, f"Monedas: {player.score}", 26, 16, 46)

    bar_x = 16
    bar_y = 78
    bar_width = 260
    bar_height = 18
    pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height), border_radius=8)
    fuel_ratio = max(0.0, min(player.gas / 100.0, 1.0))
    pygame.draw.rect(screen, (50, 200, 90), (bar_x + 2, bar_y + 2, int((bar_width - 4) * fuel_ratio), bar_height - 4), border_radius=6)
    draw_text(screen, f"Gasolina: {int(player.gas)}%", 20, bar_x + 8, bar_y - 22)


def load_background():
    try:
        path = ASSET_DIR / BACKGROUND_FILE
        image = pygame.image.load(path).convert()
        return pygame.transform.scale(image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except Exception:
        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        surface.fill((28, 120, 60))
        return surface


def load_sound(filename):
    path = SOUND_DIR / filename
    try:
        return pygame.mixer.Sound(path)
    except Exception:
        return None


def main():
    pygame.init()
    sound_enabled = True
    try:
        pygame.mixer.init()
    except Exception:
        sound_enabled = False

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Moto-Carro Rush San Gil")
    clock = pygame.time.Clock()

    background = load_background()
    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 130)

    obstacles = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group(player)

    obstacle_timer = 0.0
    coin_timer = 0.0
    elapsed = 0.0
    game_over = False
    show_game_over = False
    people_timer = 0.0
    people_interval = random.uniform(8.0, 14.0)

    sounds = {
        "engine": load_sound("engine.wav") if sound_enabled else None,
        "coin": load_sound("coin.wav") if sound_enabled else None,
        "crash": load_sound("crash.wav") if sound_enabled else None,
        "rain": load_sound("rain.wav") if sound_enabled else None,
        "traffic": load_sound("traffic.wav") if sound_enabled else None,
        "people": load_sound("people.wav") if sound_enabled else None,
    }

    if sounds["engine"]:
        sounds["engine"].play(loops=-1)

    traffic_channel = pygame.mixer.Channel(1) if sound_enabled else None
    rain_channel = pygame.mixer.Channel(2) if sound_enabled else None

    while True:
        dt = clock.tick(60) / 1000.0
        elapsed += dt
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if not game_over:
            player.update(dt, keys, SCREEN_WIDTH)
            player.gas -= 10 * dt
            if player.gas <= 0:
                player.gas = 0
                game_over = True

            level = 1 + min(2, int(elapsed // 20))
            obstacle_rate = max(0.5, 1.0 - (level - 1) * 0.22)
            coin_rate = max(1.0, 1.6 - (level - 1) * 0.3)
            speed_bonus = 1 + (level - 1) * 0.2

            obstacle_timer += dt
            if obstacle_timer >= obstacle_rate:
                obstacle_timer = 0.0
                obstacle = random_obstacle(SCREEN_WIDTH, min_speed=200 * speed_bonus, max_speed=280 * speed_bonus)
                obstacles.add(obstacle)
                all_sprites.add(obstacle)

            coin_timer += dt
            if coin_timer >= coin_rate:
                coin_timer = 0.0
                coin = random_coin(SCREEN_WIDTH, min_speed=170 * speed_bonus, max_speed=240 * speed_bonus)
                coins.add(coin)
                all_sprites.add(coin)

            obstacles.update(dt)
            coins.update(dt)

            collided_obstacles = pygame.sprite.spritecollide(player, obstacles, dokill=True)
            if collided_obstacles:
                player.lives -= len(collided_obstacles)
                if player.lives <= 0:
                    player.lives = 0
                    game_over = True
                if sounds["crash"]:
                    sounds["crash"].play()

            collected_coins = pygame.sprite.spritecollide(player, coins, dokill=True)
            if collected_coins:
                player.score += len(collected_coins)
                player.gas = min(100, player.gas + 22 * len(collected_coins))
                if sounds["coin"]:
                    sounds["coin"].play()

            if traffic_channel and sounds["traffic"]:
                if level >= 2 and not traffic_channel.get_busy():
                    traffic_channel.play(sounds["traffic"], loops=-1)
                if level == 1 and traffic_channel.get_busy():
                    traffic_channel.stop()

            if rain_channel and sounds["rain"]:
                if level >= 3 and not rain_channel.get_busy():
                    rain_channel.play(sounds["rain"], loops=-1)
                if level < 3 and rain_channel.get_busy():
                    rain_channel.stop()

            if sounds["people"]:
                people_timer += dt
                if people_timer >= people_interval:
                    sounds["people"].play()
                    people_timer = 0.0
                    people_interval = random.uniform(8.0, 14.0)

        screen.blit(background, (0, 0))
        all_sprites.draw(screen)
        draw_hud(screen, player, level)

        if game_over:
            if not show_game_over:
                show_game_over = True
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            screen.blit(overlay, (0, 0))
            font = pygame.font.SysFont(None, 64)
            text = font.render("Juego Terminado", True, (255, 80, 80))
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
            screen.blit(text, rect)
            font2 = pygame.font.SysFont(None, 36)
            text2 = font2.render("Presiona ESC para salir", True, (255, 255, 255))
            rect2 = text2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
            screen.blit(text2, rect2)

        pygame.display.flip()


if __name__ == "__main__":
    main()
