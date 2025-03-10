import winsound
import win32api
import win32con
import win32gui
import numpy as np
import random
import time 
import cv2
import mss
from collections import deque
import threading
from config import CONFIG
from ui import ConfigUI
import sys
import os
from downloader import download_template

def get_executable_dir():
    """Get the directory where the executable/script is located"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return os.path.dirname(sys.executable)
    else:
        # Running as script
        return os.path.dirname(os.path.abspath(__file__))

# Download template if needed
if not download_template():
    print("Failed to download or verify template image. Please check your internet connection.")
    sys.exit(1)

# Load template and create scaled versions for multi-scale matching
template_path = os.path.join(get_executable_dir(), "enemyIndic3.png")
template = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)
if template is None:
    print(f"Error: Could not load template image from {template_path}")
    print("The image file might be corrupted. Please try running the program again.")
    sys.exit(1)

template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
w, h = template_gray.shape[::-1]

# Create scaled templates for multi-scale matching
scale_factors = [0.9, 1.0, 1.1]  # 90%, 100%, 110% scales
templates = []
for scale in scale_factors:
    if scale == 1.0:
        templates.append(template_gray)
    else:
        width = int(template_gray.shape[1] * scale)
        height = int(template_gray.shape[0] * scale)
        scaled_template = cv2.resize(template_gray, (width, height), interpolation=cv2.INTER_AREA)
        templates.append(scaled_template)

# Template matching will give us top left corner coords which is not what we
# want as we must hit the center of the rhombus, so we get half of template size
# to offset coords towards the center of template (rhombus)
centerW = w//2
centerH = h//2

# Target prediction variables
target_positions = deque(maxlen=5)  # Store up to 5 positions for prediction
last_time = time.time()
last_mouse_move = (0, 0)  # Store last mouse movement for smoothing

def apply_smoothing(current_move, last_move):
    """Apply smoothing to mouse movement"""
    # Blend with previous movement
    smoothed_x = current_move[0] * (1 - CONFIG.config["smoothing_factor"]) + last_move[0] * CONFIG.config["smoothing_factor"]
    smoothed_y = current_move[1] * (1 - CONFIG.config["smoothing_factor"]) + last_move[1] * CONFIG.config["smoothing_factor"]
    
    # Apply acceleration dampening
    if abs(smoothed_x) > CONFIG.config["acceleration_cap"]:
        smoothed_x = CONFIG.config["acceleration_cap"] if smoothed_x > 0 else -CONFIG.config["acceleration_cap"]
    if abs(smoothed_y) > CONFIG.config["acceleration_cap"]:
        smoothed_y = CONFIG.config["acceleration_cap"] if smoothed_y > 0 else -CONFIG.config["acceleration_cap"]
    
    # Don't move if movement is too small (reduces jitter)
    if abs(smoothed_x) < CONFIG.config["min_movement_threshold"]:
        smoothed_x = 0
    if abs(smoothed_y) < CONFIG.config["min_movement_threshold"]:
        smoothed_y = 0
        
    return (smoothed_x, smoothed_y)

def calculate_dynamic_sensitivity(distance):
    """Calculate sensitivity based on distance to target"""
    base_sens = CONFIG.final_sensitivity
    
    # Reduce sensitivity when very close to target
    if distance < 10:
        return base_sens * 0.5
    elif distance < 30:
        return base_sens * 0.7
    else:
        return base_sens

def multi_scale_template_match(frame, templates, scale_factors):
    """Perform template matching at multiple scales and return the best match"""
    best_val = -1
    best_loc = None
    best_scale_idx = 0
    
    # Only check the original scale (index 1) first for performance
    template = templates[1]  # Original scale (1.0)
    result = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    # If we have a good match at original scale, don't check other scales
    if max_val >= CONFIG.config["match_threshold"]:
        best_val = max_val
        best_loc = max_loc
        best_scale_idx = 1
    else:
        # Check other scales only if needed
        for i, (template, scale) in enumerate(zip(templates, scale_factors)):
            if i == 1:  # Skip the original scale as we already checked it
                continue
                
            result = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val > best_val:
                best_val = max_val
                best_loc = max_loc
                best_scale_idx = i
    
    # Calculate center offset based on the template size
    w_scaled = int(w * scale_factors[best_scale_idx])
    h_scaled = int(h * scale_factors[best_scale_idx])
    center_w_scaled = w_scaled // 2
    center_h_scaled = h_scaled // 2
    
    return best_val, best_loc, center_w_scaled, center_h_scaled

def predict_target_position(positions, time_delta):
    """Predict the next position based on recent movement with improved algorithm"""
    if len(positions) < 2 or not CONFIG.config["prediction_enabled"]:
        return None
    
    # Get current position (most recent)
    current_pos = positions[-1]
    
    # Initialize velocity components
    vel_x = 0
    vel_y = 0
    
    # Calculate weighted average of velocities if we have enough positions
    if len(positions) >= 3:
        # Calculate multiple velocities with different time windows
        velocities = []
        weights = []
        
        # Calculate velocities between consecutive positions
        for i in range(len(positions) - 1):
            pos1 = positions[i]
            pos2 = positions[i + 1]
            
            # Time weight - more recent velocities get higher weight
            time_weight = (i + 1) / len(positions)
            
            # Calculate velocity components
            v_x = (pos2[0] - pos1[0]) / time_delta
            v_y = (pos2[1] - pos1[1]) / time_delta
            
            # Add to our collections
            velocities.append((v_x, v_y))
            weights.append(time_weight)
        
        # Calculate weighted average velocity
        total_weight = sum(weights)
        if total_weight > 0:
            for (v_x, v_y), weight in zip(velocities, weights):
                vel_x += v_x * (weight / total_weight)
                vel_y += v_y * (weight / total_weight)
    else:
        # Simple velocity calculation with just 2 positions
        prev_pos = positions[-2]
        vel_x = (current_pos[0] - prev_pos[0]) / time_delta
        vel_y = (current_pos[1] - prev_pos[1]) / time_delta
    
    # Apply velocity smoothing to prevent erratic predictions
    # Limit maximum velocity to prevent overshooting
    max_velocity = 500  # pixels per second
    vel_magnitude = (vel_x**2 + vel_y**2)**0.5
    
    if vel_magnitude > max_velocity:
        scaling_factor = max_velocity / vel_magnitude
        vel_x *= scaling_factor
        vel_y *= scaling_factor
    
    # Calculate prediction time factor based on velocity
    # Faster movements need shorter prediction time
    base_prediction_time = 0.05  # base prediction time in seconds
    vel_based_time = base_prediction_time * (1.0 - min(1.0, vel_magnitude / max_velocity))
    prediction_time = max(0.01, vel_based_time)  # ensure minimum prediction time
    
    # Apply global prediction strength factor
    prediction_time *= CONFIG.config["prediction_strength"]
    
    # Predict next position
    pred_x = int(current_pos[0] + vel_x * prediction_time)
    pred_y = int(current_pos[1] + vel_y * prediction_time)
    
    # Ensure prediction stays within capture region
    pred_x = max(0, min(pred_x, CONFIG.config["capture_size"]))
    pred_y = max(0, min(pred_y, CONFIG.config["capture_size"]))
    
    return (pred_x, pred_y)

def aimbot_loop(ui):
    global last_time, consecutive_matches, last_mouse_move
    screenCapture = mss.mss()
    
    while not ui.should_exit:
        # Simple sleep to prevent CPU overload
        time.sleep(0.001)
        
        # Capture screen and convert to grayscale
        GameFrame = np.array(screenCapture.grab(CONFIG.region))
        GameFrame = cv2.cvtColor(GameFrame, cv2.COLOR_BGRA2GRAY)

        # Aiming condition - right mouse button
        if win32api.GetAsyncKeyState(int(CONFIG.config["aim_key"], 16)) < 0:
            # Multi-scale template matching
            max_val, max_loc, center_w, center_h = multi_scale_template_match(GameFrame, templates, scale_factors)

            # If a good match is found
            if max_val >= CONFIG.config["match_threshold"]:
                # Calculate target position
                X = max_loc[0] + center_w
                Y = max_loc[1] + center_h
                
                # Store position for prediction
                current_time = time.time()
                time_delta = current_time - last_time
                last_time = current_time
                
                # Only store position if enough time has passed
                if len(target_positions) == 0 or time_delta > 0.01:
                    target_positions.append((X, Y))
                
                # Apply prediction if enabled and we have enough data
                if CONFIG.config["prediction_enabled"] and len(target_positions) >= 2:
                    predicted_pos = predict_target_position(target_positions, time_delta)
                    if predicted_pos:
                        # Blend current position with prediction for smoother tracking
                        blend_factor = 0.7  # Higher = more weight to current position
                        X = int(X * blend_factor + predicted_pos[0] * (1 - blend_factor))
                        Y = int(Y * blend_factor + predicted_pos[1] * (1 - blend_factor))
                
                # Calculate distance to target
                crosshairU = CONFIG.config["capture_size"] // 2
                deltaX = crosshairU - X
                deltaY = crosshairU - Y
                distance = (deltaX ** 2 + deltaY ** 2) ** 0.5
                
                # Calculate mouse movement with dynamic sensitivity
                dynamic_sens = calculate_dynamic_sensitivity(distance)
                nX = (-deltaX) * dynamic_sens
                nY = (-deltaY) * dynamic_sens
                
                # Apply smoothing
                current_move = (nX, nY)
                smoothed_move = apply_smoothing(current_move, last_mouse_move)
                last_mouse_move = smoothed_move
                
                # Apply mouse movement
                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(smoothed_move[0]), int(smoothed_move[1]), 0, 0)
                
                # Handle auto-shoot with improved timing
                consecutive_matches += 1
                if CONFIG.config["auto_shoot_enabled"] and consecutive_matches >= CONFIG.config["min_consecutive_matches"]:
                    if distance < 20:  # Only shoot when close enough to target
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                        time.sleep(0.1)
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            else:
                consecutive_matches = 0
                last_mouse_move = (0, 0)  # Reset smoothing when target is lost
    
    # Clean up
    screenCapture.close()

def main():
    # Create UI instance
    ui = ConfigUI()
    
    # Start aimbot in a separate thread
    aimbot_thread = threading.Thread(target=lambda: aimbot_loop(ui))
    aimbot_thread.daemon = True
    aimbot_thread.start()
    
    # Run UI in main thread
    ui.run()
    
    # Clean up
    sys.exit(0)

if __name__ == "__main__":
    main()
