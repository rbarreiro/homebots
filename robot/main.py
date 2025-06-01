from microdot import Microdot
import network
import asyncio
import time
import machine

print("Starting up... 40")

# Replace with your network credentials
ssid = 'MEO-F51500'
password = '7b82f8f1ac'

# Create station interface
wlan = network.WLAN(network.STA_IF)

# Activate the interface
wlan.active(True)

# Connect to the network
print("Connecting to WiFi", end="")
wlan.connect(ssid, password)

# Wait for connection
max_wait = 10
while max_wait > 0:
    if wlan.isconnected():
        break
    max_wait -= 1
    print(".", end="")
    time.sleep(1)
print("")


if wlan.isconnected():
    print("Connected to WiFi")
    print("IP Address:", wlan.ifconfig()[0])
else:
    print("Failed to connect to WiFi")
    
class DCMotor:
    def __init__(self, forward_pin, backward_pin, pwm_pin):
        self.forward_pin = machine.Pin(forward_pin, machine.Pin.OUT)
        self.backward_pin = machine.Pin(backward_pin, machine.Pin.OUT)
        self.pwm = machine.PWM(machine.Pin(pwm_pin), freq=50, duty=0)
    
    def set_speed(self, speed):
        if speed > 0:
            self.forward_pin.on()
            self.backward_pin.off()
            self.pwm.duty_u16(int(speed * 65535))
        elif speed < 0:
            self.forward_pin.off()
            self.backward_pin.on()
            self.pwm.duty_u16(int(-speed * 65535))
        else:
            self.forward_pin.off()
            self.backward_pin.off()
            self.pwm.duty_u16(0)

class MG996RServo:
    def __init__(self, pin, angle_init=90, speed=100, step=3):
        self.min = 1200
        self.max = 8400 
        self.range = self.max - self.min
        self.servo = machine.PWM(machine.Pin(pin), freq=50, duty=0)
        self.speed = speed
        self.angle_to_duty_ratio = self.range / 180
        self.current_duty = self.angle_to_duty(angle_init)
        self.servo.duty_u16(self.current_duty)
        self.step = step
    
    def angle_to_duty(self, angle):
        duty = int(angle * self.angle_to_duty_ratio + self.min)
        return duty

    async def set_angle(self, angle):
        target_duty = self.angle_to_duty(angle)
        for a in range(self.current_duty, target_duty, self.step if target_duty > self.current_duty else -self.step):
            self.servo.duty_u16(a)
            await asyncio.sleep(self.step / self.angle_to_duty_ratio / self.speed)
        self.servo.duty_u16(target_duty)
        self.current_duty = target_duty

    def set_degrees_per_second(self, speed):
        self.speed = speed

    def set_step(self, step):
        self.step = step


    

left_motor = DCMotor(forward_pin=32, backward_pin=33, pwm_pin=25)
right_motor = DCMotor(forward_pin=14, backward_pin=27, pwm_pin=26)
arm_servo = MG996RServo(pin=12)
gripper_motor = DCMotor(forward_pin=4, backward_pin=16, pwm_pin=17)
app = Microdot()

@app.post('/drive')
async def drive(request):
    j = request.json
    print("Received drive command:", j)
    left_motor.set_speed(j['speed_left'])
    right_motor.set_speed(j['speed_right'])
    await asyncio.sleep(j['duration'])
    left_motor.set_speed(0)
    right_motor.set_speed(0)
    return 'true'

@app.post('/gripper')
async def gripper(request):
    j = request.json
    print("Received gripper command:", j)
    gripper_motor.set_speed(j['speed'])
    return 'true'

@app.post('/arm_speed')
async def arm_speed(request):
    j = request.json
    print("Received arm speed command:", j)
    arm_servo.set_degrees_per_second(j['speed'])
    arm_servo.set_step(j['step'])
    return 'true'

@app.post('/arm')
async def arm(request):
    j = request.json
    print("Received arm command:", j)
    await arm_servo.set_angle(j['angle'])
    return 'true'

if __name__ == '__main__':
    print("Starting server on port 80")
    app.run(port= 80, host='0.0.0.0')
