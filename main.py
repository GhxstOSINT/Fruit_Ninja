import pygame
import sys
import random
import time
import cv2
import numpy as np
import os
import ctypes

# ------------------------------------------------------------
# Windows DPI awareness for accurate fullscreen resolution
# ------------------------------------------------------------
try:
    if os.name == "nt":
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            ctypes.windll.user32.SetProcessDPIAware()
except Exception:
    pass

os.environ["SDL_VIDEO_CENTERED"] = "1"

# Modules
from audio_manager import AudioManager
from input_manager import MouseInput, HandInput
from ui_manager import SceneManager
from game_engine import ClassicMode, SurvivalMode
from game_objects import Blade, Fruit, Bomb, SlicedFruit, Explosion, SplashEffect

# Colors
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)

# Config
FPS = 60
MIN_CUT_VELOCITY = 100
COMBO_WINDOW = 0.5


class ComboPopup:
    def __init__(self, x, y, count, total_points):
        self.x = x
        self.y = y
        self.count = count
        self.total_points = total_points
        self.timer = 45

    def update(self):
        self.timer -= 1
        self.y -= 1.5

    def draw(self, screen, font):
        alpha = int((self.timer / 45) * 255)
        if alpha < 0:
            alpha = 0

        text = f"{self.count}x COMBO +{self.total_points}"

        shadow = font.render(text, True, (0, 0, 0))
        shadow.set_alpha(alpha)

        surf = font.render(text, True, YELLOW)
        surf.set_alpha(alpha)

        rect = surf.get_rect(center=(self.x, self.y))
        screen.blit(shadow, (rect.x + 2, rect.y + 2))
        screen.blit(surf, rect)


def main():
    pygame.init()

    # ------------------------------------------------------------
    # Fullscreen setup
    # ------------------------------------------------------------
    try:
        screen = pygame.display.set_mode(
            (0, 0),
            pygame.FULLSCREEN | pygame.NOFRAME | pygame.DOUBLEBUF
        )
        WIDTH, HEIGHT = screen.get_size()

        if WIDTH <= 0 or HEIGHT <= 0:
            raise Exception("Invalid fullscreen size")

    except Exception:
        info = pygame.display.Info()
        WIDTH, HEIGHT = info.current_w, info.current_h
        screen = pygame.display.set_mode(
            (WIDTH, HEIGHT),
            pygame.FULLSCREEN
        )

    pygame.display.set_caption("Fruit Ninja - Fullscreen")
    clock = pygame.time.Clock()

    # Systems
    audio = AudioManager()
    ui = SceneManager(WIDTH, HEIGHT)

    # Load Background
    try:
        bg_raw = pygame.image.load("assets/background/game_background.jpg").convert()
        bg_img = pygame.transform.scale(bg_raw, (WIDTH, HEIGHT))

        dark = pygame.Surface((WIDTH, HEIGHT))
        dark.set_alpha(80)
        dark.fill((0, 0, 0))
        bg_img.blit(dark, (0, 0))

    except Exception as e:
        print(f"Background load error: {e}")
        bg_img = pygame.Surface((WIDTH, HEIGHT))
        bg_img.fill((50, 50, 50))

    # Game State Variables
    input_provider = None
    game_mode = None
    blade = Blade()

    all_sprites = pygame.sprite.Group()
    fruits = pygame.sprite.Group()

    # VFX State
    shake_timer = 0

    # Spawn timer
    spawn_timer = 0

    # Combo state
    combo_popups = []
    combo_count = 0
    last_slice_time = 0.0

    # Start Music
    audio.play_music("menu")

    running = True
    while running:
        mx, my = pygame.mouse.get_pos()
        click = False

        # Shake Logic
        shake_x, shake_y = 0, 0
        if shake_timer > 0:
            shake_timer -= 1
            shake_x = random.randint(-5, 5)
            shake_y = random.randint(-5, 5)

        # Event Loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and ui.current_scene == "GAME":
                    ui.is_paused = not ui.is_paused

                if event.key == pygame.K_F11:
                    running = False

        # ------------------------------------------------------------
        # SCENE LOGIC
        # ------------------------------------------------------------

        if ui.current_scene == "MENU":
            screen.blit(bg_img, (0, 0))
            action = ui.handle_input("MENU", mx, my, click)
            ui.draw_menu(screen)

            if action == "GOTO_MODE":
                ui.push_scene("MODE_SEL")
                audio.play_sfx("start")

        elif ui.current_scene == "MODE_SEL":
            screen.blit(bg_img, (0, 0))
            action = ui.handle_input("MODE_SEL", mx, my, click)
            ui.draw_mode_select(screen)

            if action == "MODE_CLASSIC":
                game_mode = ClassicMode()
                ui.push_scene("INPUT_SEL")
                audio.play_sfx("start")

            elif action == "MODE_SURVIVAL":
                game_mode = SurvivalMode()
                ui.push_scene("INPUT_SEL")
                audio.play_sfx("start")

            elif action == "BACK":
                ui.pop_scene()
                audio.play_sfx("start")

        elif ui.current_scene == "INPUT_SEL":
            screen.blit(bg_img, (0, 0))
            action = ui.handle_input("INPUT_SEL", mx, my, click)
            ui.draw_input_select(screen)

            if action:
                if action == "INPUT_MOUSE":
                    input_provider = MouseInput(WIDTH, HEIGHT)
                    ui.push_scene("GAME")
                    audio.play_music("game_slow")

                    all_sprites.empty()
                    fruits.empty()
                    blade = Blade()

                    combo_popups = []
                    combo_count = 0
                    last_slice_time = 0.0
                    spawn_timer = 20

                elif action == "INPUT_HAND":
                    input_provider = HandInput(WIDTH, HEIGHT)
                    ui.push_scene("GAME")
                    audio.play_music("game_slow")

                    all_sprites.empty()
                    fruits.empty()
                    blade = Blade()

                    combo_popups = []
                    combo_count = 0
                    last_slice_time = 0.0
                    spawn_timer = 20

                elif action == "BACK":
                    ui.pop_scene()
                    audio.play_sfx("start")

        elif ui.current_scene == "GAME":

            # --------------------------------------------------------
            # PAUSED MENU
            # --------------------------------------------------------
            if ui.is_paused:
                screen.blit(bg_img, (0, 0))

                all_sprites.draw(screen)
                blade.draw(screen)

                hud = ui.font_small.render(game_mode.get_status(), True, WHITE)
                screen.blit(hud, (20, 20))

                action = ui.handle_input("PAUSE", mx, my, click)
                ui.draw_pause(screen)

                if action == "RESUME":
                    ui.is_paused = False
                    audio.play_sfx("start")

                elif action == "BACK":
                    ui.is_paused = False

                    if input_provider:
                        input_provider.cleanup()
                        input_provider = None

                    ui.pop_scene()
                    audio.play_music("menu")

                    combo_popups = []
                    combo_count = 0
                    last_slice_time = 0.0
                    spawn_timer = 0

            # --------------------------------------------------------
            # NORMAL GAMEPLAY
            # --------------------------------------------------------
            else:
                ix, iy, velocity, _ = input_provider.get_input()

                screen.blit(bg_img, (0, 0))

                current_time = time.time()

                # Reset combo if time window expired
                if last_slice_time == 0 or current_time - last_slice_time > COMBO_WINDOW:
                    combo_count = 0

                if ix is not None:
                    blade.update(ix, iy)

                # Spawn fruits automatically
                spawn_timer -= 1
                if spawn_timer <= 0:
                    margin = max(150, int(WIDTH * 0.10))

                    if WIDTH > margin * 2:
                        spawn_x = random.randint(margin, WIDTH - margin)
                    else:
                        spawn_x = WIDTH // 2

                    # Spawn fully below screen
                    spawn_y = HEIGHT + 140

                    if random.randint(1, 6) == 1:
                        b = Bomb(spawn_x, spawn_y, WIDTH, HEIGHT)
                        all_sprites.add(b)
                        fruits.add(b)
                    else:
                        f = Fruit(spawn_x, spawn_y, WIDTH, HEIGHT)
                        all_sprites.add(f)
                        fruits.add(f)

                    spawn_timer = random.randint(25, 55)

                all_sprites.update()

                # Collisions
                segments = blade.get_segments()

                if velocity > MIN_CUT_VELOCITY and segments:
                    for entity in list(fruits):
                        if entity.check_slice(segments):

                            # BOMB
                            if isinstance(entity, Bomb):
                                audio.play_sfx("bomb")

                                boom = Explosion(entity.pos_x, entity.pos_y)
                                all_sprites.add(boom)

                                entity.kill()
                                game_mode.on_bomb()

                                shake_timer = 20

                                # Bomb resets combo
                                combo_count = 0
                                last_slice_time = 0.0

                            # FRUIT
                            else:
                                audio.play_sfx("splat")

                                base_points = game_mode.on_slice(entity)

                                # Time-based combo logic
                                if (
                                    combo_count > 0
                                    and last_slice_time > 0
                                    and current_time - last_slice_time <= COMBO_WINDOW
                                ):
                                    combo_count += 1
                                else:
                                    combo_count = 1

                                last_slice_time = current_time

                                # Combo scoring
                                if combo_count >= 2:
                                    total_points = base_points * combo_count
                                    extra_points = total_points - base_points

                                    if extra_points > 0:
                                        game_mode.score += extra_points

                                    audio.play_sfx("combo")
                                    combo_popups.append(
                                        ComboPopup(
                                            int(entity.pos_x),
                                            int(entity.pos_y),
                                            combo_count,
                                            total_points
                                        )
                                    )

                                splash = SplashEffect(
                                    entity.pos_x,
                                    entity.pos_y,
                                    entity.fruit_type,
                                    velocity
                                )
                                all_sprites.add(splash)

                                h1 = SlicedFruit(
                                    entity.pos_x,
                                    entity.pos_y,
                                    entity.fruit_type,
                                    1,
                                    HEIGHT
                                )
                                h2 = SlicedFruit(
                                    entity.pos_x,
                                    entity.pos_y,
                                    entity.fruit_type,
                                    2,
                                    HEIGHT
                                )

                                all_sprites.add(h1)
                                all_sprites.add(h2)

                                entity.kill()

                # Check dropped fruits
                for entity in list(fruits):
                    # Bombs should not count as missed
                    if isinstance(entity, Bomb):
                        if entity.rect.top > HEIGHT + 220:
                            entity.kill()
                        continue

                    # Only count as missed after it has entered the screen once
                    if (
                        getattr(entity, "entered_screen", False)
                        and entity.rect.top > HEIGHT + 100
                    ):
                        game_mode.on_miss()

                        # Missing a fruit resets combo
                        combo_count = 0
                        last_slice_time = 0.0

                        entity.kill()

                # Check Game Over
                if game_mode.game_over:
                    ui.current_scene = "OVER"
                    audio.play_sfx("over")
                    audio.stop_music()

                    combo_popups = []
                    combo_count = 0
                    last_slice_time = 0.0

                # Draw game objects
                all_sprites.draw(screen)
                blade.draw(screen)

                # Draw combo popups
                for popup in combo_popups:
                    popup.update()
                    popup.draw(screen, ui.font_med)

                combo_popups = [p for p in combo_popups if p.timer > 0]

                # Active combo HUD
                if (
                    combo_count >= 2
                    and last_slice_time > 0
                    and current_time - last_slice_time <= COMBO_WINDOW
                ):
                    combo_txt = ui.font_med.render(f"{combo_count}x COMBO", True, YELLOW)
                    screen.blit(
                        combo_txt,
                        (
                            WIDTH // 2 - combo_txt.get_width() // 2,
                            int(HEIGHT * 0.12)
                        )
                    )

                # Camera feed in bottom-right corner
                if isinstance(input_provider, HandInput):
                    frame = input_provider.get_frame()

                    if frame is not None:
                        try:
                            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            img_rgb = np.rot90(img_rgb)

                            surf = pygame.surfarray.make_surface(img_rgb)
                            surf = pygame.transform.flip(surf, True, False)

                            # Dynamic PiP size for fullscreen
                            pip_h = max(160, int(HEIGHT * 0.22))
                            pip_w = int(pip_h * 4 / 3)

                            surf_scaled = pygame.transform.scale(surf, (pip_w, pip_h))

                            pygame.draw.rect(
                                surf_scaled,
                                CYAN,
                                (0, 0, pip_w, pip_h),
                                3
                            )

                            pip_x = WIDTH - pip_w - 20
                            pip_y = HEIGHT - pip_h - 20

                            screen.blit(surf_scaled, (pip_x, pip_y))

                            lbl = ui.font_small.render("CAMERA", True, WHITE)
                            screen.blit(lbl, (pip_x + 6, pip_y + 6))

                        except Exception:
                            pass

                # HUD
                hud = ui.font_small.render(game_mode.get_status(), True, WHITE)
                screen.blit(hud, (20, 20))

                # Pause hint
                hint = ui.font_small.render(
                    "ESC Pause | F11 Quit",
                    True,
                    (150, 150, 150)
                )
                screen.blit(
                    hint,
                    (WIDTH - hint.get_width() - 20, 20)
                )

        elif ui.current_scene == "OVER":
            screen.blit(bg_img, (0, 0))
            all_sprites.draw(screen)

            action = ui.handle_input("OVER", mx, my, click)
            ui.draw_game_over(screen, game_mode.score)

            if action == "GOTO_MENU":
                if input_provider:
                    input_provider.cleanup()
                    input_provider = None

                ui.current_scene = "MENU"
                ui.scene_stack.clear()
                audio.play_music("menu")

                combo_popups = []
                combo_count = 0
                last_slice_time = 0.0
                spawn_timer = 0

            elif action == "RESTART":
                ui.current_scene = "GAME"
                audio.play_music("game_slow")

                if isinstance(game_mode, ClassicMode):
                    game_mode = ClassicMode()
                else:
                    game_mode = SurvivalMode()

                all_sprites.empty()
                fruits.empty()
                blade = Blade()

                combo_popups = []
                combo_count = 0
                last_slice_time = 0.0
                spawn_timer = 20

        pygame.display.flip()
        clock.tick(FPS)

    # Cleanup logic
    if input_provider:
        input_provider.cleanup()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()