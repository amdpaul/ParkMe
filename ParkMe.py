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
import email
import imaplib
import mailbox
import RPi.GPIO as GPIO  
GPIO.setmode(GPIO.BCM)

# Set up GPIO pins
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP) 

# Definitions
P1_gpio_f = 17
P2_gpio_f = 23
P3_gpio_f = 22
P1_gpio_r = 4
P2_gpio_r = 12
P3_gpio_r = 5

parkrate = 0.01  #$0.01 per second

#################################
# Function and Class Definitions
#################################

# Send email to user to charge parking fee
def ChargeUser(spot):
    To   = "parkme.sender@gmail.com"
    From = "parkme.receiver@gmail.com"
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
    s.login('parkme.receiver.com', 'XXXXXXX')
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
        totalsec = hms_to_sec(time)
        int(totalsec)
        cost = '{:05.2f}'.format(totalsec*parkrate)
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
P1 = ParkingSpot(1, 1, 'Empty', '-------', "00:00:00", "00:00:00", "00:00:00", "00.00", "02:44:00", "02:50:00", 'Yes', 0)
P2 = ParkingSpot(1, 2, 'Empty', '-------', "00:00:00", "00:00:00", "00:00:00", "00.00", "00:00:00", "00:00:00", 'Yes', 0)
P3 = ParkingSpot(1, 3, 'Empty', '-------', "00:00:00", "00:00:00", "00:00:00", "00.00", "00:00:00", "00:00:00", 'Yes', 0)
Zone1 = [P1, P2, P3]

# Update main table
def UpdateTable(Zone1):
    f = open("/home/pi/Documents/EE551 Project/MainTable", 'w')
    Zone1 = Zone1
    
    print ("                                   |             Parking            |      |          Legality          |")
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

# Notify parking spot will be illegal soon
def SendReg(P):
    if P.time2ill == 0:
        Text = """Zone #{} - Parking Spot #{}:

Thank you for registering your car: {}.""".format(P.zone, P.number, P.plate) 
    else:
        timetoill = time.strftime("%H:%M:%S", time.gmtime(P.time2ill))
        Text = """Zone #{} - Parking Spot #{}:

Thank you for registering your car: {}.
Your car will be illegally parked in (hh:mm:ss) {}.
Please relocate your car on time to avoid paying a fine.""".format(P.zone, P.number, P.plate, timetoill)
        
    To   = "parkme.sender@gmail.com"
    From = "parkme.receiver@gmail.com"
    Subj = "PARKME: Parking Registration"

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
    s.login('parkme.receiver.com', 'XXXXXX')
    s.sendmail(From,[To],Body)
    s.quit()

#############
# Interrupts
#############

###########
# Occupied
###########

# Interrupt - Mark P1 occupied
def callback_4_R(channel):  

    # Mark parking spot occupied
    P1.status = 'Full '
    P1.endP   = '--:--:--'
    P1.totalP = '--:--:--'
    P1.cost   = '--.--'

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
    else:
        P1.time2ill = 0
         
    # Update main table
    UpdateTable(Zone1)

# Interrupt - Mark P2 occupied
def callback_12_R(channel):  

    # Mark parking spot occupied
    P2.status = 'Full '
    P2.endP   = '--:--:--'
    P2.totalP = '--:--:--'
    P2.cost   = '--.--'

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
    else:
        P2.time2ill = 0
            
    # Update main table
    UpdateTable(Zone1)
        
# Interrupt - Mark P3 occupied
def callback_5_R(channel): 

    # Mark parking spot occupied
    P3.status = 'Full '
    P3.endP   = '--:--:--'
    P3.totalP = '--:--:--'
    P3.cost   = '--.--'

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
    else:
        P3.time2ill = 0
            
    # Update main table
    UpdateTable(Zone1)
    
#############
# Unoccupied
#############
        
# Interrupt - Mark P1 unoccupied
def callback_17_F(channel):    

    # Mark parking spot unoccupied
    P1.status = 'Empty'

    # Mark time parking session ends
    P1.endP = time.strftime("%I:%M:%S")

    # Check if illegal upon leaving
    startI = hms_to_sec(P1.startI)
    startP = hms_to_sec(P1.startP)
    endP   = hms_to_sec(P1.endP)

    if startP < startI & startI < endP:
        P1.legal = 'No '
    else:
        pass 

    # Calculate total time
    P1.totalP = P1.CalculateTotalP()
    P1.cost = CalculateCost(P1.totalP)
        
    # Update P1 Log, clear plate # and update main table
    UpdateLogP1(P1)
    P1.plate  = '-------'
    UpdateTable(Zone1)

    # Charge user via email
    ChargeUser(P1)

# Interrupt - Mark P2 unoccupied
def callback_23_F(channel):   

    # Mark parking spot unoccupied
    P2.status = 'Empty'

    # Mark time parking session ends
    P2.endP = time.strftime("%I:%M:%S")

    # Check if illegal upon leaving
    startI = hms_to_sec(P2.startI)
    startP = hms_to_sec(P2.startP)
    endP   = hms_to_sec(P2.endP)

    if startP < startI & startI < endP:
        P2.legal = 'No '
    else:
        pass 

    # Calculate total time
    P2.totalP = P2.CalculateTotalP()
    P2.cost = CalculateCost(P2.totalP)
        
    # Update P2 log, clear plate # and update main table
    UpdateLogP2(P2)
    P2.plate  = '-------'
    UpdateTable(Zone1)
    
    # Charge user via email
    ChargeUser(P2)

# Interrupt - Mark P3 unoccupied
def callback_22_F(channel):  

    # Mark parking spot unoccupied
    P3.status = 'Empty'

    # Mark time parking session ends
    P3.endP = time.strftime("%I:%M:%S")

    # Check if illegal upon leaving
    startI = hms_to_sec(P3.startI)
    startP = hms_to_sec(P3.startP)
    endP   = hms_to_sec(P3.endP)

    if startP < startI & startI < endP:
        P3.legal = 'No '
    else:
        pass 

    # Calculate total time
    P3.totalP = P3.CalculateTotalP()
    P3.cost = CalculateCost(P3.totalP)
        
    # Update P3 log, clear plate # and update main table
    UpdateLogP3(P3)
    P3.plate  = '-------'
    UpdateTable(Zone1)

    # Charge user via email
    ChargeUser(P3)
            
############
# Main Loop
############

raw_input("Press Enter when ready")

# Callbacks
GPIO.add_event_detect(P1_gpio_r, GPIO.RISING, callback=callback_4_R, bouncetime=10)
GPIO.add_event_detect(P2_gpio_r, GPIO.RISING, callback=callback_12_R, bouncetime=10)
GPIO.add_event_detect(P3_gpio_r, GPIO.RISING, callback=callback_5_R, bouncetime=10)
GPIO.add_event_detect(P1_gpio_f, GPIO.FALLING, callback=callback_17_F, bouncetime=10)
GPIO.add_event_detect(P2_gpio_f, GPIO.FALLING, callback=callback_23_F, bouncetime=10)
GPIO.add_event_detect(P3_gpio_f, GPIO.FALLING, callback=callback_22_F, bouncetime=10)

while(1):

    # Continuously check email for license plate #
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    (retcode, capabilities) = mail.login('parkme.receiver@gmail.com','XXXXXX')
    mail.list()
    mail.select('inbox')

    n = 0
    (retcode, messages) = mail.search(None, '(UNSEEN)')
    if retcode == 'OK':

       for num in messages[0].split() :
          n=n+1
          typ, data = mail.fetch(num,'(RFC822)')
          for response_part in data:
              if isinstance(response_part, tuple):
                  original = email.message_from_string(response_part[1])
                  
                  #print original['From']
                  
                  #Subject: 'Zone #1 - Parking Spot #X: GRD8042'
                  readplate = original['Subject'].split(' ')
                  #print original['Subject']
                  typ, data = mail.store(num,'+FLAGS','\\Seen')
    #print n

    # Read in license plate
    if n == 1:
        if readplate[5] == '#1:':
            P1.plate = readplate[6]
            UpdateTable(Zone1)
            SendReg(P1)
        elif readplate[5] == '#2:':
            P2.plate = readplate[6]
            UpdateTable(Zone1)
            SendReg(P2)
        elif readplate[5] == '#3:':
            P3.plate = readplate[6]
            UpdateTable(Zone1)
            SendReg(P3)
        else:
            pass
    else:
        pass
