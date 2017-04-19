# Modules
import datetime
import time
import RPi.GPIO as GPIO

#setup GPIO...this will be moved to the top of the main loop
GPIO.setmode(GPIO.BCM)
GPIO.setup(2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Convert from H:M:S to seconds
def hms_to_sec(time):
    h, m, s  = [int(i) for i in time.split(':')]
    sectotal = (h * 3600) + (m * 60) + s
    return sectotal

# Mark parking spot as empty, get time stamp, get total time, get cost, charge user
for spot in Zone1:
    if GPIO.input(i) == 1:   #could change depending on logic of photo transistor
        spot.status = 'Empty '
        spot.plate = '       '
        spot.endP = time.strftime("%I:%M:%S")
        spot.totalP = spot.CalculateTotalP()
        cost = hms_to_sec(spot.totalP) * .02777 / 100
        if round(cost, 2) < 10:
            spot.cost = '0' + str(round(cost, 2))
        else:
            spot.cost = str(round(cost, 2))
    else:
        pass
    i = i + 1

