# 16-channel relay simulator

from time import sleep
import threading
import sys
import os
import colorful as cf

simulating = False

if not simulating:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM) # GPIO Numbers instead of board numbers

running = True
sixteenChannels = False

lock = threading.Lock()

defaultSleepTime = 0.5

# Refresh rates in seconds
displayRefreshRate = defaultSleepTime / 5
relayRefreshRate = defaultSleepTime / 10

if simulating:
    ON_STATE = True
    OFF_STATE = False
else:
    ON_STATE = GPIO.LOW
    OFF_STATE = GPIO.HIGH

RELAY_PINS = []

if simulating:
    for i in range(16):
        RELAY_PINS.append(i + 1)
        if not sixteenChannels and i == 7:
            break
else:
    RELAY_PINS.append(14)   # 1
    RELAY_PINS.append(15)   # 2
    RELAY_PINS.append(18)   # 3
    RELAY_PINS.append(23)   # 4
    RELAY_PINS.append(24)   # 5
    RELAY_PINS.append(25)   # 6
    RELAY_PINS.append(8)    # 7
    RELAY_PINS.append(7)    # 8

    if sixteenChannels:
        RELAY_PINS.append(4)    # 9
        RELAY_PINS.append(17)   # 10
        RELAY_PINS.append(27)   # 11
        RELAY_PINS.append(22)   # 12
        RELAY_PINS.append(10)   # 13
        RELAY_PINS.append(9)    # 14
        RELAY_PINS.append(11)   # 15
        RELAY_PINS.append(0)    # 16

RELAY_STATES = []
for pin in RELAY_PINS:
    RELAY_STATES.append(OFF_STATE)

if not simulating:
    # Setup pins
    for pin in RELAY_PINS:
        GPIO.setup(pin, GPIO.OUT) # GPIO Assign mode

def SetChannel(channel, on):
    if channel < len(RELAY_PINS):
        lock.acquire()
        if on:
            RELAY_STATES[channel] = ON_STATE
        else:
            RELAY_STATES[channel] = OFF_STATE
        lock.release()
    else:
        print(f"Error {channel} is too large")

def UpdateDisplay():
    while running:
        display = "-" * 4 * (len(RELAY_PINS)+1) + "\n"
        for i in range(len(RELAY_STATES)):
            if RELAY_STATES[i] == ON_STATE:
                display = display + cf.bold_red(str(RELAY_PINS[i]).rjust(4, " "))
            else:
                display = display + cf.white(str(RELAY_PINS[i]).rjust(4, " "))

        display = display + "\n" + "-" * 4 * (len(RELAY_PINS)+1) + "\n\n"

        os.system("clear")
        sys.stdout.write(display)
        sys.stdout.flush()
        sleep(displayRefreshRate)

def UpdateRelayModule():
    while running and not simulating:
        GPIO.output(RELAY_PINS, RELAY_STATES)
        sleep(relayRefreshRate)

def All(on):
    for channel in range(len(RELAY_PINS)):
        SetChannel(channel, on)

def Range(start, end, on):
    for channel in range(start - 1, end):
        SetChannel(channel, on)

def RangeLength(start, on, length):
    for channel in range(start - 1, start + length - 1):
        SetChannel(channel, on)

def Stimulate():
    # Even on
    All(False)
    for i in range(len(RELAY_PINS)):
        if i % 2:
            SetChannel(i, True)
        sleep(defaultSleepTime)

    # Blink all
    for i in range(5):
        All(False)
        sleep(defaultSleepTime)
        All(True)
        sleep(defaultSleepTime)
    
    # Odds on
    All(False)
    for i in range(len(RELAY_PINS)):
        if not i % 2:
            SetChannel(i, True)
        sleep(defaultSleepTime)

    # Blink all
    for i in range(5):
        All(False)
        sleep(defaultSleepTime)
        All(True)
        sleep(defaultSleepTime)
    
    for i in range(10):
        Range(1, 4, True)
        Range(5, 8, False)
        if sixteenChannels:
            Range(9, 12, True)
            Range(13, 16, False)
        sleep(defaultSleepTime)
        Range(1, 4, False)
        Range(5, 8, True)
        if sixteenChannels:
            Range(9, 12, False)
            Range(13, 16, True)
        sleep(defaultSleepTime)

try:
    displayThread = threading.Thread(target=UpdateDisplay)
    displayThread.start()
    
    relayThread = threading.Thread(target=UpdateRelayModule)
    relayThread.start()
    
    while True:
        Stimulate()

except KeyboardInterrupt:
    running = False
    print("Terminating...")

except:
    print("Other error or exception occurred!")

finally:
    displayThread.join()
    relayThread.join()

    if not simulating: 
        GPIO.cleanup() # this ensures a clean exit  
