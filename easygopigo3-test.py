import easygopigo3 as easy
import time

sensor_readings = None
gpg = easy.EasyGoPiGo3()
my_distance_portI2C = gpg.init_distance_sensor('I2C')
time.sleep(0.1)


# start
gpg.set_speed(500)
while True:
    while my_distance_portI2C.read_inches() > 5:
        gpg.forward()
    gpg.backward()
    time.sleep(1)
    gpg.stop()
    gpg.turn_degrees(-45, blocking=True)
    time.sleep(0.05) # slowdown
