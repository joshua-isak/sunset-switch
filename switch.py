import RPi.GPIO as GPIO
import suntime
import time
import datetime


LED_RED = 26     # int; Pinout (BCM)
LED_GREEN = 13
LED_YELLOW = 19
SWITCH_ON = 6
SWITCH_OFF = 5

LATITUDE = 0        # float; coordinates of the pi
LONGITUDE = 0
BLACKOUT_TIME = 24  # int; hour to turn off lights regardless of sunrise time (hours in day 1-24) set 0 for no blackout time
BUFFER_TIME = 0     # int; turn lights on x minutes before sunset and x minutes after sunrise


# Setup the pi's pins
#GPIO.setwarnings(False)
pinout = (LED_RED, LED_GREEN, LED_YELLOW, SWITCH_ON, SWITCH_OFF)
GPIO.setmode(GPIO.BCM)
GPIO.setup(pinout, GPIO.OUT)


def turn_lights_on():
    for x in range(2):
        GPIO.output(SWITCH_ON, True)
        GPIO.output(LED_RED, True)
        time.sleep(1)

        GPIO.output(SWITCH_ON, False)
        GPIO.output(LED_RED, False)
        time.sleep(1)

    GPIO.output(LED_YELLOW, True)

def turn_lights_off():
    for x in range(2):
        GPIO.output(SWITCH_OFF, True)
        GPIO.output(LED_RED, True)
        time.sleep(1)

        GPIO.output(SWITCH_OFF, False)
        GPIO.output(LED_RED, False)
        time.sleep(1)

    GPIO.output(LED_YELLOW, False)



def main():
    # some code in another thread about being connected to the internet (when network control becomes a thing of course)
    GPIO.output(LED_GREEN, True)
    GPIO.output(LED_YELLOW, False)
    GPIO.output(LED_RED, False)
    light_status = False

    while True:

        # Calculate today's sunset and sunrise times
        sun = suntime.Sun(LATITUDE, LONGITUDE)
        sunset_time = sun.get_sunset_time()
        sunrise_time = sun.get_sunrise_time()

        # Wait until sunset
        seconds_until_sunset = (sunset_time.seconds - datetime.datetime.now(datetime.timezone.utc)).seconds
        #print("Turning on lights in {} seconds".format(seconds_until_sunset - BUFFER_TIME*60))
        if seconds_until_sunset < 0:
            pass
        else:
            time.sleep(seconds_until_sunset - BUFFER_TIME*60)
        if light_status == False:   # Turn the lights on if they're off
            turn_lights_on()
            light_status = True

        # Wait until Blackout Time (if applicable)
        if BLACKOUT_TIME:
            time_now = datetime.datetime.now().time()
            seconds_until_blackout = abs(time_now.hour - BLACKOUT_TIME)*3600 + (60 - time_now.minute)*60 - 3600
            #print("Turning off lights in {} seconds".format(seconds_until_blackout))

            time.sleep(seconds_until_blackout)

            if light_status == True:
                turn_lights_off()
                light_status = False

        # Wait until sunrise
        seconds_until_sunrise = (sunrise_time - datetime.datetime.now(datetime.timezone.utc)).seconds
        time.sleep(seconds_until_sunrise + BUFFER_TIME*60)
        if light_status == True:    # Turn the lights off if they're still on
            turn_lights_off()
            light_status = False

    GPIO.cleanup()

try:
    main()
except KeyboardInterrupt:
    raise
    GPIO.cleanup()
except:
    raise
    GPIO.cleanup()