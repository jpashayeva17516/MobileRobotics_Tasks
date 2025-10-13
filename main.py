#!/usr/bin/env python3
from ev3dev2.motor import MoveTank, OUTPUT_B, OUTPUT_C
from ev3dev2.sensor.lego import ColorSensor
from time import sleep, time

# --- Motors and sensor setup ---
tank = MoveTank(OUTPUT_B, OUTPUT_C)
color_sensor = ColorSensor()

# --- Line following parameters ---
BASE_SPEED = 15
KP = 0.5
TARGET_REFLECTION = 30
LOSS_THRESHOLD = 5
SEARCH_SPEED = 5

# --- Grey detection ---
grey_count = 0
on_grey = False
grey_streak = 0
GREY_STREAK_REQUIRED = 3
GREY_REFLECTION_MIN = 28
GREY_REFLECTION_MAX = 38
first_grey_done = False

# --- Data logging setup ---
LOG_FILE_PATH = "/home/robot/movement_log.txt"
log_data = []

def log_state(reflection, left_speed, right_speed, grey_count):
    """Record reflection and motor state for visualization."""
    log_data.append("{:.2f},{:.2f},{:.2f},{:.2f},{}\n".format(
        time(), reflection, left_speed, right_speed, grey_count
    ))

def save_log():
    """Write collected data to a file on the EV3 brick."""
    try:
        with open(LOG_FILE_PATH, "w") as f:
            f.writelines(log_data)
        print("Data saved to {}".format(LOG_FILE_PATH))
    except Exception as e:
        print("Failed to save log:", e)

def search_line_tight():
    """Search for the line using small, alternating turns."""
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

        # --- Debug print ---
        print("Reflection: {}, Grey count: {}".format(reflection, grey_count))

        # --- Log data ---
        error = TARGET_REFLECTION - reflection
        turn = KP * error
        left_speed = BASE_SPEED + turn
        right_speed = BASE_SPEED - turn
        log_state(reflection, left_speed, right_speed, grey_count)

        # --- Grey detection ---
        if GREY_REFLECTION_MIN <= reflection <= GREY_REFLECTION_MAX:
            grey_streak += 1
            if grey_streak >= GREY_STREAK_REQUIRED and not on_grey:
                on_grey = True
                grey_count += 1
                print("Grey line count = {}".format(grey_count))

                # First grey → spin 360
                if grey_count == 1 and not first_grey_done:
                    print("First grey line detected: spinning 360 degrees...")
                    tank.on_for_degrees(20, -20, 720)
                    sleep(0.5)
                    first_grey_done = True
                    grey_streak = 0
                    on_grey = False
                    continue  # resume line following

                # Second grey → stop
                elif grey_count == 2 and first_grey_done:
                    print("Second grey line detected: stopping robot.")
                    tank.off()
                    save_log()
                    break
        else:
            grey_streak = 0
            on_grey = False

        # --- Line following (proportional control) ---
        if reflection < LOSS_THRESHOLD or reflection > 90:
            tank.off()
            found = search_line_tight()
            if not found:
                sleep(0.2)
            continue

        tank.on(left_speed, right_speed)
        sleep(0.05)

# --- Run the program ---
try:
    follow_line()
except KeyboardInterrupt:
    tank.off()
    save_log()
    print("Stopped by user.")