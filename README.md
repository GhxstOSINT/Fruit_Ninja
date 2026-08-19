# 🍉 Fruit Ninja — AI Hand Controlled

**A computer-vision take on Fruit Ninja: your real hand is the blade.**

Built with Python, OpenCV, MediaPipe, and Pygame, this version replaces the
touchscreen swipe with real-time hand tracking — your index finger slices
fruit through the air, physics carries the pieces, and an open palm doubles
as a safety pause so you can reposition without risking a bomb.

---

## ✨ Features

- **Real-time hand tracking** — MediaPipe tracks your index finger with low
  latency to drive the blade.
- **Physics-based gameplay** — fruits launch upward and fall under gravity;
  blade collisions use robust line-segment detection so fast swipes still
  register correctly.
- **Visual polish**
  - Dynamic cyan blade trail that follows your finger.
  - Fruits split into two halves on a successful slice.
  - Real fruit artwork (apple, banana, watermelon, and more).
- **Gameplay mechanics**
  - 💣 **Bombs** — dark bombs with red fuses cost **−5 points** if sliced.
    Avoid them.
  - ✋ **Palm pause** — show an open palm to the camera to pause/shield the
    blade, a safety mechanism for repositioning your hand near a bomb.
  - Ongoing score tracking as you play.

---

## 🧰 Prerequisites

- Python 3.7+
- A webcam

---

## 📦 Installation

1. Clone the repository (or download the files).
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

---

## 🕹️ How to Play

Run the game:

```bash
python main.py
```

### Controls

| Action | How |
|---|---|
| **Slice** | Move your index finger across the screen fast enough to register a cut |
| **Pause / shield** | Open your hand (extend all five fingers) to pause the blade |
| **Quit** | Close the window, or `Alt+F4` |

---

## 🛠️ Troubleshooting

- **Laggy tracking?** Make sure you're in good, even lighting — MediaPipe's
  hand detection is noticeably less reliable in dim or backlit rooms.
- **Camera won't open?** The code uses `cv2.CAP_DSHOW` for Windows camera
  compatibility. On Linux or macOS, remove that flag in `sensors.py`.

---

## 🙌 Credits

Built with:

- [MediaPipe](https://developers.google.com/mediapipe)
- [Pygame](https://www.pygame.org/)
- [OpenCV](https://opencv.org/)
