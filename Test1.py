'''
####################################################################
Name: Ahmed Paul
Date Created: 04/21/17
Course: EE 551
Project Name: ParkMe
File Name: 'ParkMe.py'
Code Description: The following code implements the ParkMe system.
The system keeps track of how long a user parks for and charges the
user a fee depending on how long they've parked for. The system also
monitors whether or not user is parked legally. The system outputs
data to text files and sends notifications to the user via email.
####################################################################
'''
###################################
# Modules, Definitions, GPIO setup
###################################

# Modules
import smtplib
import string
import time
import datetime
from threading import Timer
import RPi.GPIO as GPIO  
GPIO.setmode(GPIO.BCM)

# Set up GPIO pins
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_UP) 

# Definitions
P1_gpio_f = 4
P2_gpio_f = 5
P3_gpio_f = 6
P1_gpio_r = 23
P2_gpio_r = 24
P3_gpio_r = 25
warningt = 30
parkrate = 0.01  #$0.01 per minute

global t1a
global t2a
global t3a

#################################
# Function and Class Definitions
#################################

# Send email to user to charge parking fee
def ChargeUser(spot):
    To   = "saju.jose1@gmail.com"
    From = "saju.jose1@gmail.com"
    Subj = "PARKME: PARKING RECEIPT"
    Text = """Zone #{} - Parking Spot #{}:

Thank you for parking.
Your total parking time (hh:mm:ss) is {}.
Please pay ${} within 24 hours.""".format(spot.zone, spot.number, spot.totalP, spot.cost)

    Body = string.join((
        "From: %s" % From,
        "To: %s" % To,
        "Subject: %s" % Subj,
        "",
        Text,
        ), "\r\n")

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.ehlo()
    s.starttls()
    # Enter password
    s.login('saju.jose1@gmail.com', 'XXXXXXX')
    s.sendmail(From,[To],Body)
    s.quit()

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
    zone     = 0
    number   = 0
    status   = 'Empty'
    plate    = '-------'
    startP   = '00:00:00'
    endP     = '00:00:00'
    totalP   = '00:00:00'
    cost     = '00.00'
    startI   = '00:00:00'
    endI     = '00:00:00'
    legal    = 'Yes'
    time2ill = 0

    def __init__(self, zone, number, status, plate, startP, endP, totalP, cost, startI, endI, legal, time2ill):
        self.zone     = zone
        self.number   = number
        self.status   = status
        self.plate    = plate
        self.startP   = startP
        self.endP     = endP
        self.totalP   = totalP
        self.cost     = cost
        self.startI   = startI
        self.endI     = endI
        self.legal    = legal
        self.time2ill = time2ill

    def CalculateTotalP(self):
        startsec    = hms_to_sec(self.startP)
        endsec      = hms_to_sec(self.endP)
        totalsec    = endsec - startsec
        self.totalP = time.strftime("%H:%M:%S", time.gmtime(totalsec))
        return self.totalP

# Define parking spots and zone
P1 = ParkingSpot(1, 1, 'Empty', '-------', "00:00:00", "00:00:00", "00:00:00", "00.00", "00:00:00", "00:00:00", 'Yes', 0)
P2 = ParkingSpot(1, 2, 'Empty', '-------', "00:00:00", "00:00:00", "00:00:00", "00.00", "00:00:00", "00:00:00", 'Yes', 0)
P3 = ParkingSpot(1, 3, 'Empty', '-------', "00:00:00", "00:00:00", "00:00:00", "00.00", "00:00:00", "00:00:00", 'Yes', 0)
Zone1 = [P1, P2, P3]

# Update main table
def UpdateTable(Zone1):
    f = open("/home/pi/Documents/EE551 Project/MainTable", 'w')
    Zone1 = Zone1
    
    print ("                                   |             Parked             |      |          Legality          |")
    print ("Zone # | Spot # | Status | Plate # |  Start  |   End   | Total Time | Cost |  Start  |   End   | Legal? |")

    f.write ("                                   |             Parked             |      |          Legality          |\n")
    f.write ("Zone # | Spot # | Status | Plate # |  Start  |   End   | Total Time | Cost |  Start  |   End   | Legal? |\n")
    
    for spot in Zone1:
        print "      {}|       {}|   {}|  {}| {}| {}|    {}| {}| {}| {}|     {}|".format(spot.zone, spot.number, spot.status, spot.plate, spot.startP, spot.endP, spot.totalP, spot.cost, spot.startI, spot.endI, spot.legal)
        f.write ("      {}|       {}|   {}|  {}| {}| {}|    {}| {}| {}| {}|     {}|\n".format(spot.zone, spot.number, spot.status, spot.plate, spot.startP, spot.endP, spot.totalP, spot.cost, spot.startI, spot.endI, spot.legal))

    f.close()
      
# Initiate parking logs:
f = open("/home/pi/Documents/EE551 Project/P1Log", 'w')
f.write("Plate # | Cost | Legal? |\n")
f.close()

f = open("/home/pi/Documents/EE551 Project/P2Log", 'w')
f.write("Plate # | Cost | Legal? |\n")
f.close()

f = open("/home/pi/Documents/EE551 Project/P3Log", 'w')
f.write("Plate # | Cost | Legal? |\n")
f.close()

# Append parking logs for every car that parks
def UpdateLogP1(P1):
    f = open("/home/pi/Documents/EE551 Project/P1Log", 'a')
    f.write (" {}| {}|     {}|\n".format(P1.plate, P1.cost, P1.legal))
    f.close()

def UpdateLogP2(P2):
    f = open("/home/pi/Documents/EE551 Project/P2Log", 'a')
    f.write (" {}| {}|     {}|\n".format(P2.plate, P2.cost, P2.legal))
    f.close()

def UpdateLogP3(P3):
    f = open("/home/pi/Documents/EE551 Project/P3Log", 'a')
    f.write (" {}| {}|     {}|\n".format(P3.plate, P3.cost, P3.legal))
    f.close()

# Change parking spot to illegal after time to illegal has expired
def NowIllegal(P, Z):
    P.legal = 'No '
    UpdateTable(Z)

# Notify parking spot will be illegal soon
def SoonIllegal(P):
    To   = "saju.jose1@gmail.com"
    From = "saju.jose1@gmail.com"
    Subj = "PARKME: ILLEGALLY PARKED NOTIFICATION"
    Text = """Zone #{} - Parking Spot #{}:

Your car will be illegally parked in {}s.
Please move your car to avoid paying a fine.""".format(P.zone, P.number, warningt)

    Body = string.join((
        "From: %s" % From,
        "To: %s" % To,
        "Subject: %s" % Subj,
        "",
        Text,
        ), "\r\n")

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.ehlo()
    s.starttls()
    # Enter password
    s.login('saju.jose1@gmail.com', 'XXXXXXX')
    s.sendmail(From,[To],Body)
    s.quit()

# Set timer to count down until time until illegally parked and
# timer to notify that car will be illegally parked soon
def SetTimersP1(P1, Z):
    t1a = Timer(P1.time2ill, NowIllegal(P1, Z))
    t1a.start()

    z = P1.time2ill - warningt 
    t1b = Timer(z, SoonIllegal(P1))
    t1b.start()

def SetTimersP2(P2, Z):
    t2a = Timer(P2.time2ill, NowIllegal(P2, Z))
    t2a.start()

    z = P2.time2ill - warningt 
    t2b = Timer(z, SoonIllegal(P2))
    t2b.start()

def SetTimersP3(P3, Z):
    t3a = Timer(P3.time2ill, NowIllegal(P3, Z))
    t3a.start()

    z = P3.time2ill - warningt 
    t3b = Timer(z, SoonIllegal(P3))
    t3b.start()

#############
# Interrupts
#############

# Interrupt - Mark P1 occupied
def callback_4_F(channel):
    #GPIO.wait_for_edge(P1_gpio, GPIO.FALLING)  

    # Mark parking spot occupied
    P1.status = 'Full '
    P1.plate  = '1234567'

    # Mark time parking session starts
    P1.startP = time.strftime("%I:%M:%S")

    # Check if spot is legal
    startI = hms_to_sec(P1.startI)
    endI   = hms_to_sec(P1.endI)
    startP = hms_to_sec(P1.startP)

    if startI < startP and startP < endI:
        P1.legal = 'No '
    elif startP < startI:
        P1.time2ill = startI - startP
        SetTimersP1(P1, Zone1)
    else:
        pass
        
    # Update main table
    UpdateTable(Zone1)
        
#except KeyboardInterrupt:  
#    GPIO.cleanup()  # clean up GPIO on CTRL+C exit  
#GPIO.cleanup()  # clean up GPIO on normal exit

# Interrupt - Mark P2 occupied
def callback_5_F(channel):
    #GPIO.wait_for_edge(P2_gpio, GPIO.FALLING)  

    # Mark parking spot occupied
    P2.status = 'Full '
    P2.plate  = 'sajjose'

    # Mark time parking session starts
    P2.startP = time.strftime("%I:%M:%S")

    # Check if spot is legal
    startI = hms_to_sec(P2.startI)
    endI   = hms_to_sec(P2.endI)
    startP = hms_to_sec(P2.startP)

    if startI < startP and startP < endI:
        P2.legal = 'No '
    elif startP < startI:
        P2.time2ill = startI - startP
        SetTimersP2(P2, Zone1)
    else:
        pass
        
    # Update main table
    UpdateTable(Zone1)
        
#except KeyboardInterrupt:  
#    GPIO.cleanup()  # clean up GPIO on CTRL+C exit  
#GPIO.cleanup()  # clean up GPIO on normal exit

# Interrupt - Mark P3 occupied
def callback_6_F(channel):
    #GPIO.wait_for_edge(P3_gpio, GPIO.FALLING)  

    # Mark parking spot occupied
    P3.status = 'Full '
    P3.plate  = 'abcdefg'

    # Mark time parking session starts
    P3.startP = time.strftime("%I:%M:%S")

    # Check if spot is legal
    startI = hms_to_sec(P3.startI)
    endI   = hms_to_sec(P3.endI)
    startP = hms_to_sec(P3.startP)

    if startI < startP and startP < endI:
        P3.legal = 'No '
    elif startP < startI:
        P3.time2ill = startI - startP
        SetTimersP3(P3, Zone1)
    else:
        pass
        
    # Update main table
    UpdateTable(Zone1)
        
#except KeyboardInterrupt:  
#    GPIO.cleanup()  # clean up GPIO on CTRL+C exit  
#GPIO.cleanup()  # clean up GPIO on normal exit

# Interrupt - Mark P1 unoccupied
def callback_23_R(channel):  
    #GPIO.wait_for_edge(P1_gpio, GPIO.RISING)  

    # Mark parking spot unoccupied
    P1.status = 'Empty'
    P1.plate  = '-------'

    # Cancel timers
#    t1a.cancel()
#    t1b.cancel()

    # Mark time parking session ends
    P1.endP = time.strftime("%I:%M:%S")

    # Calculate total time
    P1.totalP = P1.CalculateTotalP()
    P1.cost = CalculateCost(P1.totalP)
        
    # Update main table and P1 Log
    UpdateTable(Zone1)
    UpdateLogP1(P1)

    # Charge user via email
    ChargeUser(P1)
        
#except KeyboardInterrupt:  
#    GPIO.cleanup()  # clean up GPIO on CTRL+C exit  
#GPIO.cleanup()  # clean up GPIO on normal exit

# Interrupt - Mark P2 unoccupied
def callback_24_R(channel):  
    #GPIO.wait_for_edge(P2_gpio, GPIO.RISING)  

    # Mark parking spot unoccupied
    P2.status = 'Empty'
    P2.plate  = '-------'

    # Cancel timers
#    t2a.cancel()
#    t2b.cancel()

    # Mark time parking session ends
    P2.endP = time.strftime("%I:%M:%S")

    # Calculate total time
    P2.totalP = P1.CalculateTotalP()
    P2.cost = CalculateCost(P2.totalP)
        
    # Update main table and P2 log
    UpdateTable(Zone1)
    UpdateLogP2(P2)

    # Charge user via email
    ChargeUser(P2)
        
#except KeyboardInterrupt:  
#    GPIO.cleanup()  # clean up GPIO on CTRL+C exit  
#GPIO.cleanup()  # clean up GPIO on normal exit

# Interrupt - Mark P3 unoccupied
def callback_25_R(channel):
    #GPIO.wait_for_edge(P3_gpio, GPIO.RISING)  

    # Mark parking spot unoccupied
    P3.status = 'Empty'
    P3.plate  = '-------'

    # Cancel timers
#    t3a.cancel()
#    t3b.cancel()

    # Mark time parking session ends
    P3.endP = time.strftime("%I:%M:%S")

    # Calculate total time
    P3.totalP = P1.CalculateTotalP()
    P3.cost = CalculateCost(P3.totalP)
        
    # Update main table and P3 log
    UpdateTable(Zone1)
    UpdateLogP3(P3)

    # Charge user via email
    ChargeUser(P3)
        
#except KeyboardInterrupt:  
#    GPIO.cleanup()  # clean up GPIO on CTRL+C exit  
#GPIO.cleanup()  # clean up GPIO on normal exit

    
############
# Main Loop
############

raw_input("Press Enter when ready")

GPIO.add_event_detect(4, GPIO.FALLING, callback=callback_4_F, bouncetime=200)
GPIO.add_event_detect(5, GPIO.FALLING, callback=callback_5_F, bouncetime=200)
GPIO.add_event_detect(6, GPIO.FALLING, callback=callback_6_F, bouncetime=200)
GPIO.add_event_detect(23, GPIO.RISING, callback=callback_23_R, bouncetime=200)
GPIO.add_event_detect(24, GPIO.RISING, callback=callback_24_R, bouncetime=200)
GPIO.add_event_detect(25, GPIO.RISING, callback=callback_25_R, bouncetime=200)
#while(1):

######## Read email for license plate number ###########