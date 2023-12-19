"""ORB Recoil Detection using OpenCV

How to Use:
- Simply execute the main.py file and press 'x' to start/pause the script.
- Press 'o' to exit the script.
- Hold left-click(shoot) to compensate for recoil.

Functions and its description:
- exponential_moving_average(values, alpha): - Compute an exponential moving average of the values list.
- get_monitor_area(): - Get the monitor area to capture.
- orb_detection_and_compute(img1, img2): - Detect and compute the keypoints and descriptors using ORB.
- smooth_movement(values, window_size): - Smooth the movement of the mouse.
- control_recoil(): - Main function to control recoil.
"""


import cv2
import time
import numpy as np
from mss import mss
import win32api
import win32con
import keyboard
import screeninfo

orb = cv2.ORB_create()


def exponential_moving_average(values, alpha):
    """
    Compute an exponential moving average of the values list.
    The alpha parameter controls the smoothing factor.
    """
    ema_values = []
    ema = 0
    for value in values:
        if not ema_values:  # if ema_values list is empty
            ema = value
        else:
            ema = alpha * value + (1 - alpha) * ema
        ema_values.append(ema)
    return ema_values[-1] if ema_values else 0


def get_monitor_area():
    screen = screeninfo.get_monitors()[0]
    width, height = screen.width, screen.height
    top_offset = 30 * height // 100
    left_offset = 25 * width // 100
    return {'top': top_offset, 'left': left_offset, 'width': width // 2, 'height': height // 2}


def orb_detection_and_compute(img1, img2):
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)
    bfmatcher = cv2.BFMatcher(cv2.NORM_HAMMING)
    matches = bfmatcher.match(des1, des2)
    return sorted(matches, key=lambda x: x.distance), kp1, kp2


def smooth_movement(values, window_size):
    if len(values) < window_size:
        return values[-1]
    return sum(values[-window_size:]) / window_size


def control_recoil():
    # You may change these values
    recoil_compensation_factor = 1.5  # Adjust as needed for downward compensation
    horizontal_movement_scale = 0.3  # Scale down horizontal movement
    quick_start_compensation = 20  # Immediate compensation for the first few bullets
    ema_alpha = 0.2
    shots_fired = 0
    dynamic_factor = 2  # Start with a strong compensation and decrease it
    max_y_movement = 100  # Maximum limit for Y-axis movement
    exit_key = 'o'
    game_key = 'x'
    smoothing_window = 10

    # Do not change
    bbox = get_monitor_area()
    running = True
    movements_x = []
    movements_y = []
    game_state = 0

    with mss() as sct:
        old_img = np.array(sct.grab(bbox))
        old_img = cv2.cvtColor(old_img, cv2.COLOR_BGR2GRAY)
        print("hi")

        while running:
            if keyboard.is_pressed(exit_key):
                print("Exiting...")
                break

            if keyboard.is_pressed(game_key):
                game_state = not game_state
                print("Game state: ", game_state)
                time.sleep(0.3)

            if win32api.GetAsyncKeyState(0x01) != 0 and game_state:  # Left mouse button pressed
                new_img = np.array(sct.grab(bbox))
                new_img = cv2.cvtColor(new_img, cv2.COLOR_BGR2GRAY)
                matches, kp1, kp2 = orb_detection_and_compute(old_img, new_img)

                xm, ym = 0, 0
                for match in matches[:20]:
                    x1, y1 = kp1[match.queryIdx].pt
                    x2, y2 = kp2[match.trainIdx].pt
                    xm += x2 - x1
                    ym += y2 - y1

                xm, ym = xm / 100, ym / 100
                movements_x.append(xm)
                movements_y.append(-ym)  # Inverting Y-axis movement

                if len(movements_x) > smoothing_window:
                    filtered_x = exponential_moving_average(movements_x, ema_alpha)
                    filtered_y = exponential_moving_average(movements_y, ema_alpha)
                else:
                    filtered_x, filtered_y = xm, -ym

                if shots_fired < 5:
                    smooth_y = -quick_start_compensation
                    dynamic_factor = 2.0  # Reset the dynamic factor after quick start
                else:
                    smooth_y = min(filtered_y * recoil_compensation_factor * dynamic_factor, max_y_movement)

                smooth_x = filtered_x * horizontal_movement_scale

                # Adjust the dynamic factor decrement rate based on the weapon's fire rate and recoil pattern
                dynamic_factor = max(dynamic_factor - 0.05, 1.0)  # Slow down the decrement rate

                shots_fired += 1  # Increment shots fired

                if matches[0].distance > 12:
                    old_img = new_img

                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(smooth_x), int(-smooth_y), 0, 0)
                time.sleep(0.1)


if __name__ == "__main__":
    control_recoil()
