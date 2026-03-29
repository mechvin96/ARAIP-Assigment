"""
TSAHEYLU: COLAB-DRIVEN NEURAL MISSION
Project Tun Kameie - Assignment 3
Workflow (COLAB METHOD): 
1. NAVIGATION: Loads 'recorded_path_map.json' or allows manual Arrow-Key recording.
2. CAPTURE: At every 'C' event, the robot stops, stabilizes, and saves a high-res PNG.
3. CLOUD AI: You upload these PNGs and your .h5 file to Google Colab for processing.
"""

from controller import Robot, Keyboard
import numpy as np
from PIL import Image
import os
import json

# 1. INITIALIZATION
robot = Robot()
keyboard = Keyboard()
TIME_STEP = 64
MAX_SPEED = 6.28

# Enable Keyboard
keyboard.enable(TIME_STEP)

# Setup Paths (Sync these with Google Drive Desktop for automation)
SAVE_FOLDER = r"C:\WebotCaptureImage"
MAP_FILE = os.path.join(SAVE_FOLDER, "recorded_path_map.json")

if not os.path.exists(SAVE_FOLDER):
    try:
        os.makedirs(SAVE_FOLDER)
    except:
        pass

# --- JSON MAP LOADING ---
path_map = []
mode = "RECORDING"

if os.path.exists(MAP_FILE):
    try:
        with open(MAP_FILE, 'r') as f:
            path_map = json.load(f)
        if path_map:
            mode = "REPLAYING"
            print(f">>> MAP DETECTED: Loading {len(path_map)} actions from JSON.")
            print(">>> Starting AUTOMATIC MISSION (Colab Method)...")
    except Exception as e:
        print(f">>> ERROR LOADING JSON: {e}")

# Initialize Motors
left_motor = robot.getDevice('left wheel motor')
right_motor = robot.getDevice('right wheel motor')
left_motor.setPosition(float('inf'))
right_motor.setPosition(float('inf'))
left_motor.setVelocity(0.0)
right_motor.setVelocity(0.0)

camera = robot.getDevice('camera')
if camera:
    camera.enable(TIME_STEP)

# Mission State Variables
current_action = [0.0, 0.0]
action_duration = 0
replay_index = 0
replay_step_counter = 0

def execute_capture(suffix="auto"):
    """Brakes robot and saves a high-quality image for Colab processing."""
    print(f"\n[!] DATA CAPTURE: Saving frame for Colab ('{suffix}')...")
    left_motor.setVelocity(0.0)
    right_motor.setVelocity(0.0)
    
    # Wait for mechanical stabilization to ensure zero motion blur
    for _ in range(30): 
        robot.step(TIME_STEP)
        
    if camera:
        raw_data = camera.getImage()
        if raw_data:
            # Save Physical Copy for Colab
            img_data = np.frombuffer(raw_data, np.uint8).reshape((camera.getHeight(), camera.getWidth(), 4))
            img = Image.fromarray(img_data[:,:,:3]).convert('RGB')
            
            # Timestamp ensures unique filenames
            filename = f"colab_ready_{int(robot.getTime()*100)}.png"
            img.save(os.path.join(SAVE_FOLDER, filename))
            
            print(f"--------------------------------------------------")
            print(f">>> IMAGE SAVED: {filename}")
            print(f">>> STATUS: Ready for Colab Inference.")
            print(f"--------------------------------------------------")
    
    # Pause briefly after save
    for _ in range(5): robot.step(TIME_STEP)

def save_new_map():
    """Saves the recorded movement buffer to JSON."""
    try:
        with open(MAP_FILE, 'w') as f:
            json.dump(path_map, f, indent=4)
        print(f"\n>>> MISSION MAP EXPORTED TO: {MAP_FILE}")
    except Exception as e:
        print(f">>> SAVE ERROR: {e}")

print("\n" + "="*50)
if mode == "RECORDING":
    print(">>> MODE: RECORDING (Manual Data Collection)")
    print(">>> Arrows: Drive | 'C': Mark Capture Spot | 'S': Save & Replay")
else:
    print(">>> MODE: REPLAYING (Automated Data Collection)")
print("="*50 + "\n")

# --- MAIN LOOP ---
while robot.step(TIME_STEP) != -1:
    
    if mode == "RECORDING":
        key = keyboard.getKey()
        new_l, new_r = 0.0, 0.0
        
        if key == Keyboard.UP: new_l, new_r = 0.6*MAX_SPEED, 0.6*MAX_SPEED
        elif key == Keyboard.DOWN: new_l, new_r = -0.6*MAX_SPEED, -0.6*MAX_SPEED
        elif key == Keyboard.LEFT: new_l, new_r = -0.3*MAX_SPEED, 0.3*MAX_SPEED
        elif key == Keyboard.RIGHT: new_l, new_r = 0.3*MAX_SPEED, -0.3*MAX_SPEED
        elif key == ord('C'):
            # Save movement up to this point
            if action_duration > 0:
                path_map.append({"type":"move", "l":current_action[0], "r":current_action[1], "steps":action_duration})
                action_duration = 0
            # Mark capture point
            path_map.append({"type":"capture"})
            execute_capture("manual_mark")
            # Clear buffer
            while keyboard.getKey() != -1: pass
            continue
        elif key == ord('S'):
            if action_duration > 0:
                path_map.append({"type":"move", "l":current_action[0], "r":current_action[1], "steps":action_duration})
            save_new_map()
            mode = "REPLAYING"
            replay_index = 0
            continue
        
        # Accumulate steps for current movement
        if [new_l, new_r] == current_action:
            action_duration += 1
        else:
            if action_duration > 0:
                path_map.append({"type":"move", "l":current_action[0], "r":current_action[1], "steps":action_duration})
            current_action = [new_l, new_r]
            action_duration = 1
            
        left_motor.setVelocity(new_l)
        right_motor.setVelocity(new_r)

    elif mode == "REPLAYING":
        if replay_index < len(path_map):
            event = path_map[replay_index]
            if event["type"] == "move":
                left_motor.setVelocity(event["l"])
                right_motor.setVelocity(event["r"])
                replay_step_counter += 1
                if replay_step_counter >= event["steps"]:
                    replay_index += 1
                    replay_step_counter = 0
            elif event["type"] == "capture":
                execute_capture("auto_replay")
                replay_index += 1
        else:
            print(">>> MISSION COMPLETE: All frames gathered for Colab.")
            left_motor.setVelocity(0)
            right_motor.setVelocity(0)
            mode = "FINISHED"

    elif mode == "FINISHED":
        pass