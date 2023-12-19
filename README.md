# ORB Recoil Control Script

This script uses OpenCV and Python to assist with recoil control in FPS games by detecting and compensating for the upward movement of the gun when firing.

## Features

- Utilizes ORB (Oriented FAST and Rotated BRIEF) feature detection to monitor on-screen changes.
- Applies an Exponential Moving Average (EMA) filter for smooth mouse movements.
- Dynamically adjusts recoil compensation based on shooting patterns.

## Functions

- `get_monitor_area()`: Calculates the screen area for capturing the game.
- `orb_detection_and_compute(img1, img2)`: Detects and matches features between two images.
- `smooth_movement(values, window_size)`: Averages movements for a smoother transition.
- `control_recoil()`: Main function to control the recoil by moving the mouse.

## How to Use

1. Ensure you have the required Python libraries: `cv2`, `numpy`, `mss`, `win32api`, `win32con`, `keyboard`, `screeninfo`.
2. Run the script before starting your game session.
3. Press the 'x' key to toggle the script on/off during gameplay.
4. Press the 'o' key to exit the script.
5. Start shooting in-game and the script will attempt to control the recoil by moving the mouse.

## Customization

Users can edit the following variables in the script for fine-tuning:
- `recoil_compensation_factor`: Adjusts the intensity of the recoil compensation.
- `horizontal_movement_scale`: Modifies the scale of horizontal recoil control.
- `quick_start_compensation`: Sets immediate compensation for the first few bullets when firing.
- `ema_alpha`: Controls the sensitivity of the EMA filter.

## Installation

To install the necessary libraries, use the following pip commands:
```bash
pip install requirements.txt
```

## License
MIT License

Made by KripT to the community, feel free to do anything you want with this script!