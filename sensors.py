import cv2
import mediapipe as mp
import time
import math
from threading import Thread
import platform


class HandTracker:
    def __init__(self, detection_con=0.6, track_con=0.6):
        self.mp_hands = mp.solutions.hands

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            model_complexity=0,
            min_detection_confidence=detection_con,
            min_tracking_confidence=track_con
        )

        # Tracking State
        self.prev_x, self.prev_y = 0, 0
        self.prev_time = time.time()

        # Higher alpha = faster response, less smoothing
        self.alpha = 0.8

    def find_position(self, frame):
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_rgb.flags.writeable = False

        results = self.hands.process(img_rgb)

        timestamp = time.time()
        dt = timestamp - self.prev_time

        if dt == 0:
            dt = 0.001

        # If no hand is visible, reset tracking to avoid jump when hand returns
        if not results.multi_hand_landmarks:
            self.prev_x, self.prev_y = 0, 0
            self.prev_time = timestamp
            return None, None, 0.0, False

        hand_lms = results.multi_hand_landmarks[0]
        h, w, c = frame.shape

        pixel_lms = []

        for idx, lm in enumerate(hand_lms.landmark):
            pixel_lms.append(
                [idx, int(lm.x * w), int(lm.y * h)]
            )

        # Index finger tip is landmark 8
        raw_x, raw_y = pixel_lms[8][1], pixel_lms[8][2]

        # Faster smoothing response
        dist = math.hypot(raw_x - self.prev_x, raw_y - self.prev_y)

        if dist > 25:
            target_alpha = 0.9
        else:
            target_alpha = 0.7

        self.alpha = target_alpha

        first_frame = self.prev_x == 0 and self.prev_y == 0

        if first_frame:
            smooth_x, smooth_y = raw_x, raw_y
            move_dist = 0
        else:
            smooth_x = self.alpha * raw_x + (1 - self.alpha) * self.prev_x
            smooth_y = self.alpha * raw_y + (1 - self.alpha) * self.prev_y
            move_dist = math.hypot(
                smooth_x - self.prev_x,
                smooth_y - self.prev_y
            )

        velocity = move_dist / dt

        self.prev_x, self.prev_y = smooth_x, smooth_y
        cx, cy = int(smooth_x), int(smooth_y)

        self.prev_time = timestamp

        return cx, cy, velocity, False


class WebcamStream:
    def __init__(self, src=0, width=640, height=480):
        # Cross-platform camera initialization
        if platform.system() == "Windows":
            self.stream = cv2.VideoCapture(src, cv2.CAP_DSHOW)
        else:
            self.stream = cv2.VideoCapture(src)

        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        # Try to reduce latency and increase FPS
        try:
            self.stream.set(cv2.CAP_PROP_FPS, 60)
        except Exception:
            pass

        try:
            self.stream.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        except Exception:
            pass

        self.frame = None
        self.tracked_data = (None, None, 0.0, False)
        self.stopped = False

        self.tracker = HandTracker()

    def start(self):
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        while not self.stopped:
            grabbed, frame = self.stream.read()

            if not grabbed or frame is None:
                time.sleep(0.01)
                continue

            # Mirror image
            frame = cv2.flip(frame, 1)

            # Track in background thread
            cx, cy, velocity, _ = self.tracker.find_position(frame)

            self.tracked_data = (cx, cy, velocity, False)
            self.frame = frame

    def read(self):
        return self.frame

    def get_tracked_data(self):
        return self.tracked_data

    def stop(self):
        self.stopped = True
        self.stream.release()