#!/usr/bin/env python3
from ev3dev2.motor import MoveTank, OUTPUT_B, OUTPUT_C
from ev3dev2.sensor.lego import ColorSensor
from time import sleep

tank = MoveTank(OUTPUT_B, OUTPUT_C)
color_sensor = ColorSensor()

BASE_SPEED = 15
KP = 0.5
TARGET_REFLECTION = 30
LOSS_THRESHOLD = 5
SEARCH_STEP_DEGREES = 5
SEARCH_SPEED = 5

grey_count = 0
on_grey = False
grey_streak = 0
GREY_STREAK_REQUIRED = 3  # consecutive readings needed

# Reflection range for grey line
GREY_REFLECTION_MIN = 28
GREY_REFLECTION_MAX = 38

first_grey_done = False  # track if first grey has been handled

def search_line_tight():
    """Search for line using very small wheel turns for smooth cornering."""
    for _ in range(10):
        tank.on(BASE_SPEED - SEARCH_SPEED, BASE_SPEED + SEARCH_SPEED)
        sleep(0.05)
        if TARGET_REFLECTION - 10 <= color_sensor.reflected_light_intensity <= TARGET_REFLECTION + 10:
            return True
    for _ in range(10):
        tank.on(BASE_SPEED + SEARCH_SPEED, BASE_SPEED - SEARCH_SPEED)
        sleep(0.05)
        if TARGET_REFLECTION - 10 <= color_sensor.reflected_light_intensity <= TARGET_REFLECTION + 10:
            return True
    return False

def follow_line():
    global grey_count, on_grey, grey_streak, first_grey_done

    while True:
        reflection = color_sensor.reflected_light_intensity

        # Grey detection
        if GREY_REFLECTION_MIN <= reflection <= GREY_REFLECTION_MAX:
            grey_streak += 1
            if grey_streak >= GREY_STREAK_REQUIRED and not on_grey:
                on_grey = True
                grey_count += 1
                tank.off()
                print("Grey line count =", grey_count)

                if grey_count == 1 and not first_grey_done:
                    print("First grey line detected: spinning 360 degrees...")
                    tank.on_for_degrees(20, -20, 720)
                    sleep(0.5)
                    first_grey_done = True
                    grey_streak = 0
                    on_grey = False
                    continue
                elif grey_count == 2 and first_grey_done:
                    print("Second grey line detected: stopping robot.")
                    tank.off()
                    break
        else:
            grey_streak = 0
            on_grey = False

        # Proportional line following
        error = TARGET_REFLECTION - reflection
        turn = KP * error
        left_speed = BASE_SPEED + turn
        right_speed = BASE_SPEED - turn

        # Line lost handling
        if reflection < LOSS_THRESHOLD or reflection > 90:
            tank.off()
            found = search_line_tight()
            if not found:
                sleep(0.2)
            continue

        tank.on(left_speed, right_speed)
        sleep(0.05)

try:
    follow_line()
except KeyboardInterrupt:
    tank.off()
    print("Stopped by user.")
