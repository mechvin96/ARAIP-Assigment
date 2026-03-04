#Project Tun Kameie- Obstacle Avoidance Phase 1
from controller import Robot

#Initiali the robot
TimeStep = 64
Max_Speed = 6.28


#Setup Sensor
#Initilaize 8 promixmity sensors
ps=[]
ps_names = ['ps0','ps1','ps2','ps3','ps4','ps5','ps6','ps7']
for name in ps_names:
    sensor = robot.GetDevice(name)
    sensor.enable(TimeStep)
    ps.append(sensor)

#Initialize 2 motors
left_motor = robot.GetDevice('left wheel motor')
right_motor = robot.GetDevice('right wheel motor')

#Set the motors to velocity mode to infinity
left_motor.setPosition(float('inf'))
right_motor.setPosition(float('inf'))
left_motor.setVelocity(0.0)
right_motor.setVelocity(0.0)

#Main Simulation Loop
while robot.step(TimeStep)!=-1:

    #Read PS sensor values and set the threshold for obstacle detection
    ps_values = [sensor.getValue() for sensor in ps]
    threshold = 80.0

    #Check for obstacles and set motor speeds accordingly
    #Left(ps5,ps6,ps7)
    left_obstacle = ps_values[5] > threshold or ps_values[6] > threshold or ps_values[7] > threshold
    #Right(ps0,ps1,ps2)
    right_obstacle = ps_values[0] > threshold or ps_values[1] > threshold or ps_values[2] > threshold

    #Initialize motor speeds at 50% of max speed
    left_speed = 0.5 * Max_Speed
    right_speed = 0.5 * Max_Speed

    #Obstacled on the left --> turn right
    if left_obstacle:
        left_speed = 0.5 * Max_Speed
        right_speed = -0.5 * Max_Speed

    elif right_obstacle: #Obstacled on the right --> turn left
        left_speed = -0.5 * Max_Speed
        right_speed = 0.5 * Max_Speed

    #Set motor speeds
left_motor.setVelocity(left_speed)
right_motor.SetVelocity(right_speed)
          

