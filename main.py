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
    ema = values[0]
    for value in values[1:]:
        ema = alpha * value + (1 - alpha) * ema
    return ema


def get_monitor_area():
    screen = screeninfo.get_monitors()[0]
    width, height = screen.width, screen.height

    # Define the percentage of the screen to capture from the top-left corner
    capture_width_percent = 50  # captures 50% of the screen's width
    capture_height_percent = 50  # captures 50% of the screen's height

    # Calculate the actual pixel dimensions based on the percentages
    capture_width = int(width * capture_width_percent / 100)
    capture_height = int(height * capture_height_percent / 100)

    # The top and left offsets remain 0 to start from the top-left corner
    return {'top': 0, 'left': 0, 'width': capture_width, 'height': capture_height}


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
    recoil_compensation_factor = 2 # Adjust as needed for downward compensation
    horizontal_movement_scale = 0.3  # Scale down horizontal movement
    quick_start_compensation = 8  # Immediate compensation for the first few bullets
    ema_alpha = 0.3  # 0.1 - 0.9, higher value = more smoothing
    dynamic_factor = 3  # Start with a strong compensation and decrease it
    max_y_movement = 100  # Maximum limit for Y-axis movement
    smoothing_window = 10
    exit_key = "o"  # Press this key to exit the script
    game_key = 'x'  # Press this key to start/pause the script
    debug_key = 'f5'  # Press this key to enable/disable debug mode

    # Do not change
    shots_fired = 0
    debug_mode = False
    bbox = get_monitor_area()
    running = True
    movements_x = []
    movements_y = []
    game_state = 0

    with mss() as sct:
        old_img = np.array(sct.grab(bbox))
        old_img = cv2.cvtColor(old_img, cv2.COLOR_BGR2GRAY)

        while running:
            if keyboard.is_pressed(exit_key):
                print("Exiting...")
                break

            if keyboard.is_pressed(game_key):
                game_state = not game_state
                print("Game state: ", game_state)
                time.sleep(0.3)

            if keyboard.is_pressed(debug_key):
                debug_mode = not debug_mode
                print("Debug mode: ", debug_mode)
                time.sleep(0.3)

            if win32api.GetAsyncKeyState(0x01) != 0 and game_state:  # Left mouse button pressed
                new_img = np.array(sct.grab(bbox))
                new_img = cv2.cvtColor(new_img, cv2.COLOR_BGR2GRAY)
                try:
                    matches, kp1, kp2 = orb_detection_and_compute(old_img, new_img)
                except Exception as err:
                    print(err)
                    continue

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
                    movements_x = movements_x[-smoothing_window:]
                    movements_y = movements_y[-smoothing_window:]

                # Then calculate the filtered values
                if len(movements_x) > 1:
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
                if debug_mode:
                    print("Smooth X: ", smooth_x, "Y: ", smooth_y)
                    print("Movements\nX:", movements_x, "Y: ", movements_y)

                # Adjust the dynamic factor decrement rate based on the weapon's fire rate and recoil pattern
                dynamic_factor = max(dynamic_factor - 0.05, 1.0)  # Slow down the decrement rate

                shots_fired += 1  # Increment shots fired

                if matches[0].distance > 12:
                    old_img = new_img

                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(smooth_x), int(-smooth_y), 0, 0)

            # Do not remove, this is a sleep for the main loop
            time.sleep(0.01)


if __name__ == "__main__":
    control_recoil()
