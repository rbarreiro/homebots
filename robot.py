import requests

class Robot:
    def __init__(self, ip, arm_angle_min=0, arm_angle_max=180, angle_offset=0):
        self.arm_angle_min = arm_angle_min
        self.arm_angle_max = arm_angle_max
        self.angle_offset = angle_offset
        self.ip = ip


    def drive(self, duration, speed_left, speed_right):
        requests.post(f'http://{self.ip}/drive', json={"duration": duration, "speed_left": speed_left, "speed_right": speed_right})

    def forward(self, duration=1, speed = 1):
        self.drive(duration, speed, speed)

    def set_arm_angle(self, angle):
        angle = angle + self.angle_offset
        if angle < self.arm_angle_min:
            angle = self.arm_angle_min
        elif angle > self.arm_angle_max:
            angle = self.arm_angle_max

        requests.post(f'http://{self.ip}/arm', json={"angle": angle})

    def gripper(self, speed):
        requests.post(f'http://{self.ip}/gripper', json={"speed": speed})

    def turn_left(self, duration=1, speed = 0.4):
        self.drive(duration, -speed, speed)
    
    def turn_right(self, duration=1, speed = 0.4):
        self.drive(duration, speed, -speed)
        
    def set_arm_speed(self, speed, step):
        requests.post(f'http://{self.ip}/arm_speed', json={"speed": speed, "step": step})
