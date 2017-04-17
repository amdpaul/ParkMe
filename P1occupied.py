'''
Name: Ahmed Paul
Date Created: 04/16/17
Course: EE 551
Project: ParkMe
File Name: 'P1occupied.py'
Code Description: ISR for when a car enters a parking spot 1 in Zone 1.
'''

# Modules
import time

# Convert from H:M:S to seconds
def hms_to_sec(time):
    h, m, s  = [int(i) for i in time.split(':')]
    sectotal = (h * 3600) + (m * 60) + s
    return sectotal

# Mark parking spot occupied
P1.status = 'Full '
P1.plate  = 'GRD8042'

# Mark time parking session starts
P1.startP = time.strftime("%I:%M:%S")

# Check if spot is legal
startI = hms_to_sec(P1.startI)
endI   = hms_to_sec(P1.endI)
startP = hms_to_sec(P1.startP)

if startI < startP and startP < endI:
    P1.legal = 'No "
elif startP < startI:
    timetoillegal = startI - startP
else:
    pass


