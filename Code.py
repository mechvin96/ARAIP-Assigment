"""
Project Tun Kameie - Final Integrated Controller
This controller implements obstacle avoidance, random wandering, 
and color recognition for Red, Blue, and Green blocks.
"""

from controller import Robot
import random

# Initialize the Robot
robot = Robot()
TIME_STEP = 64
MAX_SPEED = 6.28

# 1. SETUP DEVICES
# Initialize 8 Proximity Sensors (ps0 to ps7)
ps = []
ps_names = ['ps0', 'ps1', 'ps2', 'ps3', 'ps4', 'ps5', 'ps6', 'ps7']
for name in ps_names:
    sensor = robot.getDevice(name)
    sensor.enable(TIME_STEP)
    ps.append(sensor)

# Initialize Motors
left_motor = robot.getDevice('left wheel motor')
right_motor = robot.getDevice('right wheel motor')

# Set motors to "velocity mode"
left_motor.setPosition(float('inf'))
right_motor.setPosition(float('inf'))
left_motor.setVelocity(0.0)
right_motor.setVelocity(0.0)

# Initialize Camera for Color Recognition
camera = robot.getDevice('camera')
camera.enable(TIME_STEP)
cam_width = camera.getWidth()
cam_height = camera.getHeight()
print("Camera Initialized and enabled") # Debug Statement(trying out something new)

# Tracking Variables for Color Recognition
found_status = {'red': False, 'green': False, 'blue': False}
found_history = []

def print_summary():
    """Prints a summary of all items recognized so far."""
    if not found_history:
        print("Summary of colors encountered: None")
    else:
        summary_store = ", ".join(found_history)
        print(f"Summary of colors encountered: {summary_store}")

# Wandering counter
wander_counter = 0
#Camera Timing to make the software not lag
vision_timer = 0 

# Main Simulation Loop
while robot.step(TIME_STEP) != -1:

    #  1. VISION LOGIC (Lag Free Sampling)
    #  Only run vision every 10 step to maintain performance and reduce lag
    vision_timer += 1
    if camera and vision_timer % 10 == 0:
        image = camera.getImage()
    
        if image:
            red_count = 0
            green_count = 0
            blue_count = 0
            total_samples = 0
        # Sample the center pixel
        #cx, cy = cam_width // 2, cam_height // 2
        
        # Use a step of 8 to sample  the frame sparsely and reduce lag
            step = 8
            for x in range(0, cam_width, step):
                for y in range(0, cam_height, step):
                    total_sample +=1
                    r = camera.imageGetRed(image, cam_width, x, y)
                    g = camera.imageGetGreen(image, cam_width, x, y)
                    b = camera.imageGetBlue(image, cam_width, x, y)

                    #Use a specified threshold to count colors, this is more robust than checking a single pixel
                    if r > 90 and g < 75 and b < 75:
                        red_count += 1
                    elif g > 90 and r < 75 and b < 75:
                        green_count += 1
                    elif b > 90 and r < 75 and g < 75:
                        blue_count += 1


        # Get RGB values
        #r = camera.imageGetRed(image, cam_width, cx, cy)
        #g = camera.imageGetGreen(image, cam_width, cx, cy)
        #b = camera.imageGetBlue(image, cam_width, cx, cy)
        
        # OPTIONAL: Uncomment the line below to debug actual RGB values in console
        #print(f"RGB: ({r}, {g}, {b})")

            detected_color = None
        # Thresholds lowered to 160 for better detection in different lighting
            if r > 100 and g < 90 and b < 90:
                detected_color = 'red'
            elif g > 100 and r < 90 and b < 90:
                detected_color = 'green'
            elif b > 100 and r < 90 and g < 90:
                detected_color = 'blue'

        # Check if this is a new discovery
            if detected_color and not found_status[detected_color]:
                print(f"I See {detected_color}!")
                found_status[detected_color] = True
                found_history.append(detected_color)   
                print_summary()

    # --- 2. NAVIGATION LOGIC (Obstacle Avoidance & Wandering) ---
    ps_values = [sensor.getValue() for sensor in ps]
    threshold = 80.0 # Proximity threshold
    
    # Check for obstacles
    # Right side sensors (ps0, ps1, ps2)
    right_obstacle = ps_values[0] > threshold or ps_values[1] > threshold
    # Left side sensors (ps7, ps6, ps5)
    left_obstacle = ps_values[7] > threshold or ps_values[6] > threshold

    # Default forward speed
    left_speed = 0.5 * MAX_SPEED
    right_speed = 0.5 * MAX_SPEED

    if left_obstacle:
        # Turn Right
        left_speed = 0.5 * MAX_SPEED
        right_speed = -0.5 * MAX_SPEED
        wander_counter = 0
    elif right_obstacle:
        # Turn Left
        left_speed = -0.5 * MAX_SPEED
        right_speed = 0.5 * MAX_SPEED
        wander_counter = 0
    else:
        # Random wandering every 100 steps
        wander_counter += 1
        if wander_counter > 100:
            left_speed += random.uniform(-0.15, 0.15) * MAX_SPEED
            right_speed += random.uniform(-0.15, 0.15) * MAX_SPEED
            if wander_counter > 120: # Reset after a brief "wobble"
                wander_counter = 0

    # Apply speeds to motors
    left_motor.setVelocity(left_speed)
    right_motor.setVelocity(right_speed)