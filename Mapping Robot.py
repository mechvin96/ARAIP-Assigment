"""
TSAHEYLU: TELEOP LEARN, SAVE & AUTOMATED REPLAY
Project Tun Kameie - Assignment 3
Workflow: 
1. RECORD: Use Arrow Keys to drive. Press 'C' to mark a "Capture Point" in the map.
2. SAVE: Press 'S' to save the movement/capture map to JSON and start REPLAY.
3. REPLAY: The robot executes the movements and automatically snaps photos at 
   every 'C' marker found in the JSON file.
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

# Setup Paths
SAVE_FOLDER = r"C:\WebotCaptureImage"
MAP_FILE = os.path.join(SAVE_FOLDER, "recorded_path_map.json")

if not os.path.exists(SAVE_FOLDER):
    try:
        os.makedirs(SAVE_FOLDER)
    except:
        pass

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

# 2. MISSION VARIABLES
path_map = []
current_action = [0.0, 0.0] # [left, right]
action_duration = 0

mode = "RECORDING" # Modes: RECORDING, REPLAYING, FINISHED
replay_index = 0
replay_step_counter = 0

def capture_image(suffix="manual"):
    """Function to stabilize the robot and capture an image for AI processing."""
    print(f"\n[!] CAPTURING: Stabilizing for '{suffix}' snap...")
    
    # Brake motors for clarity
    left_motor.setVelocity(0.0)
    right_motor.setVelocity(0.0)
    
    # Wait 1.5 seconds for mechanical vibrations to stop
    for _ in range(25):
        robot.step(TIME_STEP)
        
    if camera:
        raw_image = camera.getImage()
        if raw_image:
            img_data = np.frombuffer(raw_image, np.uint8).reshape((camera.getHeight(), camera.getWidth(), 4))
            img = Image.fromarray(img_data[:,:,:3]).convert('RGB')
            filename = f"snap_{suffix}_{int(robot.getTime()*100)}.png"
            img.save(os.path.join(SAVE_FOLDER, filename))
            print(f">>> SUCCESS: Saved {filename} to {SAVE_FOLDER}")
    
    # Short pause after snap
    for _ in range(5):
        robot.step(TIME_STEP)

def save_map():
    """Saves the recorded path_map to a JSON file."""
    try:
        with open(MAP_FILE, 'w') as f:
            json.dump(path_map, f, indent=4)
        print(f"\n>>> MISSION MAP EXPORTED: {MAP_FILE}")
    except Exception as e:
        print(f">>> ERROR SAVING MAP: {e}")

def record_current_move():
    """Helper to push the current accumulated movement to the map."""
    global action_duration
    if action_duration > 0:
        path_map.append({
            "type": "move",
            "l": current_action[0],
            "r": current_action[1],
            "steps": action_duration
        })
        action_duration = 0

print("\n" + "="*50)
print(">>> MODE: RECORDING (Manual Control)")
print(">>> Arrow Keys: Drive")
print(">>> 'C': Mark Capture Point (Saved to JSON)")
print(">>> 'S': Save Map & Start Replay")
print("="*50 + "\n")

# Main Simulation Loop
while robot.step(TIME_STEP) != -1:
    
    if mode == "RECORDING":
        key = keyboard.getKey()
        
        new_left = 0.0
        new_right = 0.0
        
        if key == Keyboard.UP:
            new_left, new_right = 0.6 * MAX_SPEED, 0.6 * MAX_SPEED
        elif key == Keyboard.DOWN:
            new_left, new_right = -0.6 * MAX_SPEED, -0.6 * MAX_SPEED
        elif key == Keyboard.LEFT:
            new_left, new_right = -0.3 * MAX_SPEED, 0.3 * MAX_SPEED
        elif key == Keyboard.RIGHT:
            new_left, new_right = 0.3 * MAX_SPEED, -0.3 * MAX_SPEED
        elif key == ord('C'):
            record_current_move()
            path_map.append({"type": "capture"})
            print(f"[+] Capture Point marked at event index {len(path_map)}")
            # Optional: Take a snap now to confirm view
            capture_image("record_confirm")
            # Clear keyboard buffer
            while keyboard.getKey() != -1: pass 
            continue
        elif key == ord('S'):
            record_current_move()
            save_map()
            mode = "REPLAYING"
            print("\n>>> REPLAYING RECORDED MISSION...")
            robot.step(1000)
            continue
        
        # Action tracking
        if new_left == current_action[0] and new_right == current_action[1]:
            action_duration += 1
        else:
            record_current_move()
            current_action = [new_left, new_right]
            action_duration = 1
            
        left_motor.setVelocity(new_left)
        right_motor.setVelocity(new_right)

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
                # Automated capture at recorded spot
                capture_image("auto_replay")
                replay_index += 1
        else:
            mode = "FINISHED"

    elif mode == "FINISHED":
        left_motor.setVelocity(0)
        right_motor.setVelocity(0)
        print(">>> MISSION COMPLETE: Replay finished.")
        break