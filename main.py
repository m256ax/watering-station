from machine import Pin, ADC, Timer, RTC
import time, os

# constants
PIN_PUMP_1 = 14
PIN_PUMP_2 = 15
PIN_LED_L_1 = 2
PIN_LED_L_2 = 3
PIN_LED_L_3 = 4
PIN_LED_L_4 = 5
PIN_LED_R_1 = 18
PIN_LED_R_2 = 19
PIN_LED_R_3 = 20
PIN_LED_R_4 = 21

PIN_BUTTON_1 = 6
PIN_BUTTON_2 = 17

PIN_WATER_LEVEL_SENSOR_1 = 0
PIN_WATER_LEVEL_SENSOR_2 = 1

WATERING_CYCLE_TIMES_ARRAY = [10, 15, 20, 30]  # time in minutes

# global variables
selectionActive = True
dailyWateringCycles = 0
wateringCycleTime = 1  # choose from WATERING_CYCLE_TIMES
selectionTimer = Timer()
rtc = RTC()

initRtcFile = 'rtcInit.txt' # choose init time for RTC
wateringTimeFile = 'wateringTimes.txt' # choose time for start watering

wateringTimes = []

pump1 = Pin(PIN_PUMP_1, Pin.OUT)
pump2 = Pin(PIN_PUMP_2, Pin.OUT)

ledL1 = Pin(PIN_LED_L_1, Pin.OUT)
ledL2 = Pin(PIN_LED_L_2, Pin.OUT)
ledL3 = Pin(PIN_LED_L_3, Pin.OUT)
ledL4 = Pin(PIN_LED_L_4, Pin.OUT)
ledR1 = Pin(PIN_LED_R_1, Pin.OUT)
ledR2 = Pin(PIN_LED_R_2, Pin.OUT)
ledR3 = Pin(PIN_LED_R_3, Pin.OUT)
ledR4 = Pin(PIN_LED_R_4, Pin.OUT)

button1 = Pin(PIN_BUTTON_1, Pin.IN, Pin.PULL_DOWN)
button2 = Pin(PIN_BUTTON_2, Pin.IN, Pin.PULL_DOWN)
wl1 = Pin(PIN_WATER_LEVEL_SENSOR_1, Pin.IN, Pin.PULL_UP)
wl2 = Pin(PIN_WATER_LEVEL_SENSOR_2, Pin.IN, Pin.PULL_UP)

sensor1 = ADC(Pin(27))
sensor2 = ADC(Pin(26))

# use variables instead of numbers:
soil1 = (1, 6000, 60000, )# Soil moisture PIN reference, calibraton value min, calibraton value min max
soil2 = (2, 6000, 60000, )# Soil moisture PIN reference, calibraton value min, calibraton value min max

def isDry(soilSensor):
    minMoisture=soilSensor[1]
    maxMoisture=soilSensor[2]
    if soilSensor[0] == 1:
        sensor = sensor1
    else:
        sensor = sensor2
    print('sensor' + str(soilSensor[0]) + ' = ' + str(sensor.read_u16()))
    # read moisture value and convert to percentage into the calibration range
    moisture = (maxMoisture - sensor.read_u16())*100 /(maxMoisture - minMoisture)
    if moisture > 100:
        moisture = 100
    elif moisture < 0:
        moisture = 0
    # print values
    print('moisture: ' + '%.2f' % moisture + '% (adc: ' + str(sensor.read_u16()) + ')')
    return 0 if moisture > 30 else 1

def checkKeys():
    global selectionActive
    if (button1.value() or button2.value()):
        selectionActive = True
        selectionTimer.init(mode=Timer.ONE_SHOT, period=10000, callback=disableSelection)


def disableSelection(t):
    global selectionActive
    selectionActive = False
    ledL1.value(0)
    ledL2.value(0)
    ledL3.value(0)
    ledL4.value(0)
    ledR1.value(0)
    ledR2.value(0)
    ledR3.value(0)
    ledR4.value(0)
    saveSettings()
    selectionTimer.init(mode=Timer.PERIODIC, freq=0.1, callback=signOfLife)


def saveSettings():
    # saving settings
    try:
        os.remove('t.txt')
    except OSError:
        print('t.txt doesn\'t exists')
    try:
        os.remove('c.txt')
    except OSError:
        print("t.txt doesn't exists")

    f = open('t.txt', 'w+')
    f.write(str(wateringCycleTime))
    f.close()
    f = open('c.txt', 'w+')
    f.write(str(dailyWateringCycles))
    f.close()


def loadSettings():
    global wateringCycleTime, dailyWateringCycles, initRtcFile, wateringTimeFile, wateringTimes, rtc
    try:
        f = open('t.txt')
        wateringCycleTime = int(f.read())
        print('wateringCycleTime', wateringCycleTime)
        f.close()
    except OSError:
        print('t.txt doesn\'t exists')
        
    try:
        f = open('c.txt')
        dailyWateringCycles = int(f.read())
        print('dailyWateringCycles', dailyWateringCycles)
        f.close()
    except OSError:
        print('c.txt doesn\'t exists')
        
    try:
        file = open(initRtcFile)
        rtc.datetime(list(map(int, file.read().split(','))))
        print(rtc.datetime())
        file.close()
    except OSError:
        print('rtcInit.txt doesn\'t exists')    

    try:
        file = open(wateringTimeFile)
        try:
            line = file.read()
            wateringTimes = line.split("\n")
            print(wateringTimes)
        except EOFError:
            print('error read line')
        file.close()
    except OSError:
        print('wateringTimes.txt doesn\'t exists')


def displayWateringTimes():
    if (selectionActive):
        ledL4.value(1) if wateringCycleTime >= 0 else ledL4.value(0)
        ledL3.value(1) if wateringCycleTime >= 1 else ledL3.value(0)
        ledL2.value(1) if wateringCycleTime >= 2 else ledL2.value(0)
        ledL1.value(1) if wateringCycleTime >= 3 else ledL1.value(0)


def displayWateringCycles():
    if (selectionActive):
        ledR1.value(1) if dailyWateringCycles >= 0 else ledR1.value(0)
        ledR2.value(1) if dailyWateringCycles == 1 else ledR2.value(0)

def checkAndModifySettings():
    global wateringCycleTime, dailyWateringCycles
    if (button1.value()):
        time.sleep_ms(50)
        if (button1.value()):
            wateringCycleTime = (wateringCycleTime + 1) if wateringCycleTime < 3 else 0
            displayWateringTimes()
            time.sleep_ms(200)

    if (button2.value()):
        time.sleep_ms(50)
        if (button2.value()):
            dailyWateringCycles = (dailyWateringCycles + 1) if dailyWateringCycles < 1 else 0
            displayWateringCycles()
            time.sleep_ms(200)

def checkWatering():
    global wateringTimes, rtc
    now = rtc.datetime()
        
    if(dailyWateringCycles == 1):
        for i in wateringTimes:  
            wateringTime = i.split(",")
            if (now[4] == int(wateringTime[4]) and (now[5] == int(wateringTime[5]))):
                watering()
                break
    else:
        line = wateringTimes[0]
        wateringTime = line.split(",")
        if (now[4] == int(wateringTime[4]) and (now[5] == int(wateringTime[5]))):
            watering()
        
def watering():
    if (checkWaterLevel(wl1) and isDry(soil1)):
        wateringStart = time.time()
        print(str(rtc.datetime()) +  ' -> start watering pump1')
        pump1.value(1)
        while (time.time() - wateringStart < (WATERING_CYCLE_TIMES_ARRAY[wateringCycleTime] * 60)):
            ledR1.value(1)
            time.sleep_ms(200)
            ledR1.value(0)
            time.sleep_ms(200)
        pump1.value(0)
        print(str(rtc.datetime()) +  ' -> stop watering pump1')
    if (checkWaterLevel(wl2) and isDry(soil2)):
        wateringStart = time.time()
        print(str(rtc.datetime()) +  ' -> start watering pump2')
        pump2.value(1)
        while (time.time() - wateringStart < (WATERING_CYCLE_TIMES_ARRAY[wateringCycleTime] * 60)):
            ledR2.value(1)
            time.sleep_ms(200)
            ledR2.value(0)
            time.sleep_ms(200)
        pump2.value(0)
        print(str(rtc.datetime()) +  ' -> stop watering pump2')
        
def signOfLife(t):
    ledR1.value(1)
    time.sleep_ms(10)
    ledR1.value(0)
    ledL4.value(1)
    time.sleep_ms(10)
    ledL4.value(0)
    print(str(rtc.datetime()) +  ' -> sign of life')

def checkWaterLevel(wl):
    return 0 if wl.value() else 1

def checkWaterAndAlarm():
    if (checkWaterLevel(wl1) == 0):
        ledR4.value(1)
        time.sleep_ms(500)
        ledR4.value(0)
        time.sleep_ms(500)
    if (checkWaterLevel(wl2) == 0):
        ledR3.value(1)
        time.sleep_ms(500)
        ledR3.value(0)
        time.sleep_ms(500)

# loading the settings from flash before entering the loop
loadSettings()
# disable LEDs after 10 seconds
selectionTimer.init(mode=Timer.ONE_SHOT, period=10000, callback=disableSelection)

while (1):
    checkKeys()
    checkWatering()
    if (selectionActive):
        checkAndModifySettings()
        displayWateringTimes()
        displayWateringCycles()
    else:
        checkWaterAndAlarm()
    time.sleep_ms(5)
