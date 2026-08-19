import pygame
import cv2
import math
import time
from sensors import WebcamStream

# ------------------------------------------------------------
# Camera and pointer tuning
# ------------------------------------------------------------
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# Increase this if pointer still feels slow.
# Try 2.0 or 2.2 if needed.
HAND_SENSITIVITY = 1.4

# Boosts slice velocity detection.
HAND_VELOCITY_BOOST = 1.8


class InputProvider:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def get_input(self):
        return None, None, 0, False

    def cleanup(self):
        pass


class MouseInput(InputProvider):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.prev_pos = None
        self.prev_time = time.time()

    def get_input(self):
        cur_time = time.time()
        dt = cur_time - self.prev_time

        if dt == 0:
            dt = 0.001

        mx, my = pygame.mouse.get_pos()
        buttons = pygame.mouse.get_pressed()

        if not buttons[0]:
            self.prev_pos = None
            self.prev_time = cur_time
            return None, None, 0, False

        velocity = 0

        if self.prev_pos:
            dist = math.hypot(
                mx - self.prev_pos[0],
                my - self.prev_pos[1]
            )
            velocity = dist / dt

        self.prev_pos = (mx, my)
        self.prev_time = cur_time

        return mx, my, velocity, False


class HandInput(InputProvider):
    def __init__(self, width, height):
        super().__init__(width, height)

        # Use lower camera resolution for speed, then map to screen size
        self.webcam = WebcamStream(
            src=0,
            width=CAMERA_WIDTH,
            height=CAMERA_HEIGHT
        ).start()

        self.cam_w = CAMERA_WIDTH
        self.cam_h = CAMERA_HEIGHT

    def get_input(self):
        tx, ty, velocity, _ = self.webcam.get_tracked_data()

        if tx is None:
            return None, None, 0, False

        # Normalize camera coordinates
        nx = tx / self.cam_w
        ny = ty / self.cam_h

        # Apply sensitivity around screen center
        nx = 0.5 + (nx - 0.5) * HAND_SENSITIVITY
        ny = 0.5 + (ny - 0.5) * HAND_SENSITIVITY

        # Clamp to screen bounds
        nx = max(0.0, min(1.0, nx))
        ny = max(0.0, min(1.0, ny))

        sx = int(nx * self.width)
        sy = int(ny * self.height)

        return sx, sy, velocity * HAND_VELOCITY_BOOST, False

    def get_frame(self):
        return self.webcam.read()

    def cleanup(self):
        self.webcam.stop()