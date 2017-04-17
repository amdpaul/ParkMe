'''
Name: Ahmed Paul
Date Created: 04/16/17
Course: EE 551
Project: ParkMe
File Name: 'ParkTableGen.py'
Code Description: Parking Table Generator.
'''
# Modules
import time
import datetime

# Definitions
parkrate = 0.01  #$0.01 per minute

# Convert from H:M:S to minutes
def hms_to_min(time):
    h, m, s  = [int(i) for i in time.split(':')]
    mintotal = (h * 60) + m
    return mintotal

# Convert from H:M:S to seconds
def hms_to_sec(time):
    h, m, s  = [int(i) for i in time.split(':')]
    sectotal = (h * 3600) + (m * 60) + s
    return sectotal

# Calculate Cost
def CalculateCost(time):
        totalmin = hms_to_min(time)
        int(totalmin)
        cost = '{:05.2f}'.format(totalmin*parkrate)
        return cost

# Create class for parking spot
class ParkingSpot:
    zone   = 0
    number = 0
    status = 'Empty'
    plate  = '-------'
    startP = '00:00:00'
    endP   = '00:00:00'
    totalP = '00:00:00'
    cost   = '00.00'
    startI = '00:00:00'
    endI   = '00:00:00'
    legal  = 'Yes'

    def __init__(self, zone, number, status, plate, startP, endP, totalP, cost, startI, endI, legal):
        self.zone   = zone
        self.number = number
        self.status = status
        self.plate  = plate
        self.startP = startP
        self.endP   = endP
        self.totalP = totalP
        self.cost   = cost
        self.startI = startI
        self.endI   = endI
        self.legal  = legal

    def CalculateTotalP(self):
        startsec    = hms_to_sec(self.startP)
        endsec      = hms_to_sec(self.endP)
        totalsec    = endsec - startsec
        self.totalP = time.strftime("%H:%M:%S", time.gmtime(totalsec))
        return self.totalP

# Define parking spots and zone
P1 = ParkingSpot(1, 1, 'Empty', '-------', "00:00:00", "00:00:00", "00:00:00", "00.00", "00:00:00", "00:00:00", 'Yes')
P2 = ParkingSpot(1, 2, 'Empty', '-------', "00:00:00", "00:00:00", "00:00:00", "00.00", "00:00:00", "00:00:00", 'Yes')
P3 = ParkingSpot(1, 3, 'Empty', '-------', "00:00:00", "00:00:00", "00:00:00", "00.00", "00:00:00", "00:00:00", 'Yes')
Zone1 = [P1, P2, P3]

# Update main table
def UpdateTable(Zone1):
    Zone1 = Zone1
    print ("                                   |             Parked             |      |          Legality          |")
    print ("Zone # | Spot # | Status | Plate # |  Start  |   End   | Total Time | Cost |  Start  |   End   | Legal? |")
    for spot in Zone1:
        print "      {}|       {}|   {}|  {}| {}| {}|    {}| {}| {}| {}|     {}|".format(spot.zone, spot.number, spot.status, spot.plate, spot.startP, spot.endP, spot.totalP, spot.cost, spot.startI, spot.endI, spot.legal)

# Update parking log:
# Write function to append file logging info for parking spot.
# For every car that parks in the spot a new line is written (appended) to file.
'''
def UpdateLog(P):
    print "\nPlate # | Cost | Legal? |"
    print "  {}| {}|  {}|".format(P
'''   

UpdateTable(Zone1)

