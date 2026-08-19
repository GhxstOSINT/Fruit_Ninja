import pygame
import os

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (255, 165, 0)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
CYAN = (0, 255, 255)


class FrameButton:
    """Transparent button with rounded corners and white border"""

    def __init__(self, x, y, w, h, text, action_code, use_image=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action = action_code
        self.hover = False
        self.scale = 1.0
        self.target_scale = 1.0
        self.image = None

        if use_image:
            try:
                path = f"assets/ui/buttons/{use_image}"

                if os.path.exists(path):
                    raw = pygame.image.load(path).convert_alpha()
                    self.image = pygame.transform.scale(raw, (w, h))

            except Exception as e:
                print(f"Button image load error: {e}")

    def draw(self, screen, font):
        self.scale += (self.target_scale - self.scale) * 0.3

        scaled_w = int(self.rect.w * self.scale)
        scaled_h = int(self.rect.h * self.scale)

        scaled_rect = pygame.Rect(
            self.rect.centerx - scaled_w // 2,
            self.rect.centery - scaled_h // 2,
            scaled_w,
            scaled_h
        )

        if self.image:
            if self.scale != 1.0:
                scaled_img = pygame.transform.scale(self.image, (scaled_w, scaled_h))
                screen.blit(scaled_img, scaled_rect)
            else:
                screen.blit(self.image, scaled_rect)
        else:
            if self.hover:
                glow_surf = pygame.Surface(
                    (scaled_w + 10, scaled_h + 10),
                    pygame.SRCALPHA
                )
                pygame.draw.rect(
                    glow_surf,
                    (*WHITE, 30),
                    glow_surf.get_rect(),
                    border_radius=10
                )
                screen.blit(
                    glow_surf,
                    (scaled_rect.x - 5, scaled_rect.y - 5)
                )

            pygame.draw.rect(
                screen,
                WHITE,
                scaled_rect,
                2,
                border_radius=10
            )

            txt_surf = font.render(self.text, True, WHITE)
            text_rect = txt_surf.get_rect(center=scaled_rect.center)
            screen.blit(txt_surf, text_rect)

    def check_hover(self, mx, my):
        self.hover = self.rect.collidepoint(mx, my)
        self.target_scale = 1.05 if self.hover else 1.0
        return self.hover

    def check_click(self, mx, my, click):
        if self.rect.collidepoint(mx, my) and click:
            self.target_scale = 0.95
            return self.action

        return None


class SceneManager:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.current_scene = "MENU"
        self.scene_stack = []
        self.is_paused = False

        # Dynamic UI scaling
        self.ui_scale = height / 600.0

        self.font_big = pygame.font.Font(None, int(80 * self.ui_scale))
        self.font_med = pygame.font.Font(None, int(50 * self.ui_scale))
        self.font_small = pygame.font.Font(None, int(30 * self.ui_scale))

        cx = width // 2
        cy = height // 2

        def s(val):
            return int(val * self.ui_scale)

        # Menu
        self.btn_play = FrameButton(
            cx - s(100),
            cy + s(50),
            s(200),
            s(80),
            "PLAY",
            "GOTO_MODE",
            use_image="btn_play.png"
        )

        # Mode Select
        self.btn_classic = FrameButton(
            cx - s(220),
            cy + s(20),
            s(200),
            s(60),
            "CLASSIC",
            "MODE_CLASSIC"
        )

        self.btn_survival = FrameButton(
            cx + s(20),
            cy + s(20),
            s(200),
            s(60),
            "SURVIVAL",
            "MODE_SURVIVAL"
        )

        self.btn_back_mode = FrameButton(
            cx - s(100),
            cy + s(120),
            s(200),
            s(50),
            "BACK",
            "BACK"
        )

        # Input Select
        self.btn_mouse = FrameButton(
            cx - s(220),
            cy + s(20),
            s(200),
            s(60),
            "MOUSE",
            "INPUT_MOUSE"
        )

        self.btn_hand = FrameButton(
            cx + s(20),
            cy + s(20),
            s(200),
            s(60),
            "CAMERA",
            "INPUT_HAND"
        )

        self.btn_back_input = FrameButton(
            cx - s(100),
            cy + s(120),
            s(200),
            s(50),
            "BACK",
            "BACK"
        )

        # Pause menu
        self.btn_resume = FrameButton(
            cx - s(100),
            cy - s(40),
            s(200),
            s(60),
            "RESUME",
            "RESUME"
        )

        self.btn_back_pause = FrameButton(
            cx - s(100),
            cy + s(40),
            s(200),
            s(60),
            "BACK",
            "BACK"
        )

        # Game Over
        self.btn_replay = FrameButton(
            cx - s(220),
            cy + s(100),
            s(200),
            s(60),
            "REPLAY",
            "RESTART"
        )

        self.btn_home = FrameButton(
            cx + s(20),
            cy + s(100),
            s(200),
            s(60),
            "HOME",
            "GOTO_MENU"
        )

    def push_scene(self, scene):
        if self.current_scene not in self.scene_stack:
            self.scene_stack.append(self.current_scene)

        self.current_scene = scene

    def pop_scene(self):
        if self.scene_stack:
            self.current_scene = self.scene_stack.pop()
            return True

        return False

    def draw_menu(self, screen):
        title = self.font_big.render("FRUIT NINJA V3", True, ORANGE)
        screen.blit(
            title,
            (
                self.width // 2 - title.get_width() // 2,
                int(100 * self.ui_scale)
            )
        )

        sub = self.font_small.render(
            "Slice fruits with hand or mouse!",
            True,
            WHITE
        )
        screen.blit(
            sub,
            (
                self.width // 2 - sub.get_width() // 2,
                int(180 * self.ui_scale)
            )
        )

        self.btn_play.draw(screen, self.font_med)

    def draw_mode_select(self, screen):
        title = self.font_med.render("SELECT MODE", True, WHITE)
        screen.blit(
            title,
            (
                self.width // 2 - title.get_width() // 2,
                int(100 * self.ui_scale)
            )
        )

        self.btn_classic.draw(screen, self.font_med)
        self.btn_survival.draw(screen, self.font_med)
        self.btn_back_mode.draw(screen, self.font_small)

    def draw_input_select(self, screen):
        title = self.font_med.render("SELECT CONTROL", True, WHITE)
        screen.blit(
            title,
            (
                self.width // 2 - title.get_width() // 2,
                int(100 * self.ui_scale)
            )
        )

        self.btn_mouse.draw(screen, self.font_med)
        self.btn_hand.draw(screen, self.font_med)
        self.btn_back_input.draw(screen, self.font_small)

    def draw_pause(self, screen):
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))

        title = self.font_big.render("PAUSED", True, ORANGE)
        screen.blit(
            title,
            (
                self.width // 2 - title.get_width() // 2,
                int(150 * self.ui_scale)
            )
        )

        self.btn_resume.draw(screen, self.font_med)
        self.btn_back_pause.draw(screen, self.font_med)

    def draw_game_over(self, screen, score):
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))

        title = self.font_big.render("GAME OVER", True, RED)
        screen.blit(
            title,
            (
                self.width // 2 - title.get_width() // 2,
                int(150 * self.ui_scale)
            )
        )

        score_text = self.font_med.render(f"Score: {score}", True, WHITE)
        screen.blit(
            score_text,
            (
                self.width // 2 - score_text.get_width() // 2,
                int(250 * self.ui_scale)
            )
        )

        self.btn_replay.draw(screen, self.font_med)
        self.btn_home.draw(screen, self.font_med)

    def handle_input(self, scene, mx, my, click):
        if scene == "MENU":
            self.btn_play.check_hover(mx, my)
            return self.btn_play.check_click(mx, my, click)

        elif scene == "MODE_SEL":
            self.btn_classic.check_hover(mx, my)
            self.btn_survival.check_hover(mx, my)
            self.btn_back_mode.check_hover(mx, my)

            a1 = self.btn_classic.check_click(mx, my, click)
            a2 = self.btn_survival.check_click(mx, my, click)
            a3 = self.btn_back_mode.check_click(mx, my, click)

            return a1 or a2 or a3

        elif scene == "INPUT_SEL":
            self.btn_mouse.check_hover(mx, my)
            self.btn_hand.check_hover(mx, my)
            self.btn_back_input.check_hover(mx, my)

            a1 = self.btn_mouse.check_click(mx, my, click)
            a2 = self.btn_hand.check_click(mx, my, click)
            a3 = self.btn_back_input.check_click(mx, my, click)

            return a1 or a2 or a3

        elif scene == "PAUSE":
            self.btn_resume.check_hover(mx, my)
            self.btn_back_pause.check_hover(mx, my)

            a1 = self.btn_resume.check_click(mx, my, click)
            a2 = self.btn_back_pause.check_click(mx, my, click)

            return a1 or a2

        elif scene == "OVER":
            self.btn_replay.check_hover(mx, my)
            self.btn_home.check_hover(mx, my)

            a1 = self.btn_replay.check_click(mx, my, click)
            a2 = self.btn_home.check_click(mx, my, click)

            return a1 or a2

        return None