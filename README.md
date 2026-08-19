# Fruit Ninja - AI Hand Controlled

A high-performance computer vision game where you play Fruit Ninja using your real hand as the blade! Built with Python, OpenCV, MediaPipe, and Pygame.

## Features

*   **Real-Time Hand Tracking**: Uses MediaPipe to track your index finger with low latency.
*   **Physics-Based Gaming**: Fruits launch and fall with gravity; blade collision uses robust line-segment detection for fast swipes.
*   **Visual Adjustments**: 
    *   **Blade Trail**: Dynamic cyan trail that follows your finger.
    *   **Slicing Effects**: Fruits split into two halves when sliced.
    *   **Assets**: Uses real fruit graphics (Apple, Banana, Watermelon, etc.).
*   **Gameplay Mechanics**:
    *   **Bombs**: Avoid slicing the dark bombs with red fuses! (-5 points).
    *   **Palm Pause**: Show an **Open Palm** to the camera to Pause/Shield the blade (safety mechanism).
    *   **Score System**: Track your slicing performance.

## Prerequisites

*   Python 3.7+
*   Webcam

## Installation

1.  Clone the repository (or download files).
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## How to Play

1.  Run the game:
    ```bash
    python main.py
    ```
2.  **Controls**:
    *   **Slice**: Move your index finger across the screen to slice fruits. You must move fast enough to create a "cut".
    *   **Pause**: Open your hand (extend all 5 fingers) to pause the blade. This is useful if a bomb is in the way and you want to move your hand safely.
    *   **Quit**: Close the window or press `Alt+F4`.

## Troubleshooting

*   **Lag?** ensure you have good lighting for the camera.
*   **Camera Error?** The code uses `cv2.CAP_DSHOW` for Windows compatibility. If on Linux/Mac, you might need to remove that flag in `sensors.py`.

## Credits

Built with:
*   [MediaPipe](https://developers.google.com/mediapipe)
*   [Pygame](https://www.pygame.org/)
*   [OpenCV](https://opencv.org/)

# Fruit_Ninja
