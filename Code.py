"""
Project Tun Kameie - Obstacle Avoidance Phase
This controller implements basic navigation using proximity sensors.
"""

from controller import Robot
import random # Importin random for robot wandering behavior

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

# Set motors to "velocity mode" by setting position to infinity
left_motor.setPosition(float('inf'))
right_motor.setPosition(float('inf'))
left_motor.setVelocity(0.0)
right_motor.setVelocity(0.0)

#Add Random Wandering
wander_counter = 0

# Main Simulation Loop
while robot.step(TIME_STEP) != -1:
    # 2. READ SENSOR DATA
    # Sensor values typically range from 0 (nothing) to 4000+ (very close)
    ps_values = [sensor.getValue() for sensor in ps]

    # 3. OBSTACLE AVOIDANCE LOGIC
    # Define thresholds for detection
    threshold = 80.0
    
    # Check for obstacles on the left (ps5, ps6, ps7)
    left_obstacle = ps_values[5] > threshold or ps_values[6] > threshold or ps_values[7] > threshold
    
    # Check for obstacles on the right (ps0, ps1, ps2)
    right_obstacle = ps_values[0] > threshold or ps_values[1] > threshold or ps_values[2] > threshold

    # Initialize motor speeds at 50% max
    left_speed = 0.5 * MAX_SPEED
    right_speed = 0.5 * MAX_SPEED

    if left_obstacle:
        # Obstacle on the left? Turn right
        left_speed = 0.5 * MAX_SPEED
        right_speed = -0.5 * MAX_SPEED
        wander_counter = 0  # Reset wandering counter when an obstacle is detected
    elif right_obstacle:
        # Obstacle on the right? Turn left
        left_speed = -0.5 * MAX_SPEED
        right_speed = 0.5 * MAX_SPEED
        wander_counter = 0 # Reset wandering counter when an obstacle is detected
    else:
                # No obstacles detected, move forward
        left_speed = 0.5 * MAX_SPEED
        right_speed = 0.5 * MAX_SPEED
        
        # Add random wandering behavior every 100 steps
        wander_counter += 1
        if wander_counter > 100:
            left_speed += random.uniform(-0.2, 0.2) * MAX_SPEED
            right_speed += random.uniform(-0.2, 0.2) * MAX_SPEED
            wander_counter = 0

    # 4. APPLY SPEEDS TO MOTORS
    left_motor.setVelocity(left_speed)
    right_motor.setVelocity(right_speed)